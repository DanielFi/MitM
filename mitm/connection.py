from .buffered_socket import BufferedSocket

from .handler import Handler


class Connection:
    def __init__(self, client_socket: BufferedSocket, server_socket: BufferedSocket, handler: Handler):
        self._client_socket = client_socket
        self._server_socket = server_socket
        self._handler = handler

    def get_client_socket(self) -> BufferedSocket:
        return self._client_socket

    def get_server_socket(self) -> BufferedSocket:
        return self._server_socket

    def send_to_server(self, data: bytes):
        self._server_socket.socket.send(data)
    def send_to_client(self, data: bytes):
        self._client_socket.socket.send(data)

    def get_handler(self) -> Handler:
        return self._handler

    def recv_from_server(self):
        pass
    def recv_from_client(self):
        pass

    def close(self):
        self._client_socket.socket.close()
        self._server_socket.socket.close()


