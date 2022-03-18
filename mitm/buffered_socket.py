import socket

from dataclasses import dataclass

class BufferedSocket:
    def __init__(self, socket: socket.socket, pending_data: bytes=b""):
        self._socket = socket
        self.pending_data = pending_data

    @property
    def socket(self) -> socket.socket:
        return self._socket
