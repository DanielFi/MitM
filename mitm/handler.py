from abc import ABC, abstractmethod
import os


class Handler(ABC):

    def __init__(self, outgoing_fileno: int, incoming_fileno: int):
        self._outgoing_fileno = outgoing_fileno
        self._incoming_fileno = incoming_fileno
        self.init()
    
    def send_outgoing_bytes(self, data: bytes):
        os.write(self._outgoing_fileno, data)
    
    def send_incoming_bytes(self, data: bytes):
        os.write(self._incoming_fileno, data)

    def init(self):
        pass

    @abstractmethod
    def get_frame(self, stream):
        raise NotImplementedError()

    @abstractmethod
    def handle_outgoing_frame(self, frame) -> bool:
        return True
    
    @abstractmethod
    def handle_incoming_frame(self, frame) -> bool:
        return True
