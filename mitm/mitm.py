import socket
from select import select
from io import BytesIO
from typing import Type
from kaitaistruct import KaitaiStream

from .handler import Handler


class Mitm:

    def __init__(self, listen_addr:str, listen_port:int, dest_addr:str, dest_port:int, handler: Type[Handler]):
        self._listen_addr = listen_addr
        self._listen_port = listen_port
        self._dest_addr = dest_addr
        self._dest_port = dest_port
        self._handler_cls: Type[Handler] = handler

        self._srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 10)
        self._srvsock.bind((listen_addr, listen_port))
        self._srvsock.listen(5)

        self._descriptors = [self._srvsock]
        self._handlers = {} # socket.socket -> Handler
        self._forward_map = {}
        self._backward_map = {}

        self._pending_data = {}
        
        print('MitM server started on {}:{}'.format(listen_addr, listen_port))
    
    def run(self):
        while True:
            sread, _, _ = select(self._descriptors, [], [])

            for sock in sread:
                if sock is self._srvsock:
                    self._accept_new_connection()
                else:
                    self._handle_socket_data(sock)
    
    def _accept_new_connection(self):
        new_sock, (remote_host, remote_port) = self._srvsock.accept()
        print('new connection from {}:{}'.format(remote_host, remote_port))

        dest_sock = self._connect_to_dest()

        self._descriptors.append(new_sock)
        self._descriptors.append(dest_sock)

        handler = self._handler_cls()
        self._handlers[new_sock] = handler
        self._handlers[dest_sock] = handler

        self._forward_map[new_sock] = dest_sock
        self._backward_map[dest_sock] = new_sock

        self._pending_data[new_sock] = b''
        self._pending_data[dest_sock] = b''
    
    def _handle_socket_data(self, sock):
        new_data = sock.recv(4096)

        if not new_data:
            self._disconnect(sock)
            return
        
        old_data = self._pending_data[sock]
        data = old_data + new_data

        outgoing = sock in self._forward_map
        handler = self._handlers[sock]
        callback = handler.handle_outgoing_frame if outgoing else handler.handle_incoming_frame

        stream = KaitaiStream(BytesIO(data))
        pos = 0
        while True:
            try:
                frame = self._handlers[sock].get_frame(stream)
                new_pos = stream.pos()
                frame_bytes = data[pos:new_pos]
                pos = new_pos
            except EOFError as e:
                stream.seek(pos)
                self._pending_data[sock] = stream.read_bytes_full()
                return
            
            callback(frame)

            if sock in self._forward_map:
                matching_sock = self._forward_map[sock]
            else:
                matching_sock = self._backward_map[sock]

            matching_sock.send(frame_bytes)
    
    def _disconnect(self, sock):
        if sock in self._forward_map:
            matching_sock = self._forward_map[sock]
            del self._forward_map[sock]
            del self._backward_map[matching_sock]
        else:
            matching_sock = self._backward_map[sock]
            del self._backward_map[sock]
            del self._forward_map[matching_sock]
        
        self._descriptors.remove(sock)
        self._descriptors.remove(matching_sock)
        del self._pending_data[sock]
        del self._pending_data[matching_sock]

        del self._handlers[sock]
        del self._handlers[matching_sock]

        sock.close()
        matching_sock.close()

        print('connection disconnected')
    
    def _connect_to_dest(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._dest_addr, self._dest_port))
        print('connected to dest')
        return sock
