import socket

import logging

from select import select
from io import BytesIO
from typing import Type, List
from kaitaistruct import KaitaiStream
from dataclasses import dataclass

from .connection import Connection
from .buffered_socket import BufferedSocket

from .handler import Handler, HandlerResult

MAX_CONNECTIONS = 10
MAX_ACTIVE_CONNECTIONS = 5
MAX_SOCKET_READ_BUFFER = 4096


class Mitm:

    def __init__(self, listen_addr: str, listen_port: int, dest_addr: str, dest_port: int, handler: Type[Handler]):
        self._dest_addr = dest_addr
        self._dest_port = dest_port

        self._handler_cls: Type[Handler] = handler

        self._srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, MAX_CONNECTIONS)
        self._srvsock.bind((listen_addr, listen_port))
        self._srvsock.listen(MAX_ACTIVE_CONNECTIONS)

        self._connections = []

        logging.info('MitM server started on {}:{}'.format(listen_addr, listen_port))

    def _get_descriptors(self) -> List[socket.socket]:
        return sum([[connection.get_client_socket().socket, connection.get_server_socket().socket] for connection in self._connections], [])

    def _get_connection_from_socket(self, socket: socket.socket) -> Connection:
        for connection in self._connections:
            if connection.get_client_socket().socket == socket or connection.get_server_socket().socket == socket:
                return connection
        #TODO create a named exception
        raise Exception("Nooooooooooo why did you do this to me?!")

    def run(self):
        while True:
            read_descriptors, _, _ = select(self._get_descriptors() + [self._srvsock], [], [])

            for read_descriptor in read_descriptors:
                if read_descriptor is self._srvsock:
                    self._accept_new_connection()
                else:
                    self._handle_socket_data(read_descriptor)

    def _accept_new_connection(self):
        new_sock, (remote_host, remote_port) = self._srvsock.accept()
        logging.info('new connection from {}:{}'.format(remote_host, remote_port))

        dest_sock = self._connect_to_dest()
        self._connections.append(Connection(BufferedSocket(new_sock), BufferedSocket(dest_sock), self._handler_cls()))


    def _handle_socket_data(self, sock: socket.socket):
        new_data = sock.recv(MAX_SOCKET_READ_BUFFER)
        connection = self._get_connection_from_socket(sock) # TODO catch the exception!

        if not new_data:
            self._disconnect(connection)
            return

        outgoing = sock == connection.get_client_socket().socket
        matching_sock = connection.get_server_socket() if outgoing else connection.get_client_socket()
        handler = connection.get_handler()
        callback = handler.handle_outgoing_frame if outgoing else handler.handle_incoming_frame

        old_data = matching_sock.pending_data
        data = old_data + new_data

        stream = KaitaiStream(BytesIO(data))
        pos = 0
        while True:
            try:
                frame = handler.get_frame(stream)
                new_pos = stream.pos()
                frame_bytes = data[pos:new_pos]
                pos = new_pos
            except EOFError as e:
                stream.seek(pos)
                matching_sock.pending_data = stream.read_bytes_full()
                return

            handler_result = callback(frame)
            if not handler_result.should_drop:
                matching_sock.socket.send(frame_bytes)

            if handler_result.client_data:
                connection.send_to_client(handler_result.client_data)
            if handler_result.server_data:
                connection.send_to_server(handler_result.server_data)

    def _disconnect(self, connection: Connection):
        connection.close()
        self._connections.remove(connection)
        logging.info('Connection disconnected')

    def _connect_to_dest(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._dest_addr, self._dest_port))
        logging.info(f'Connected to dest: {self._dest_addr}:{self._dest_port}')
        return sock
