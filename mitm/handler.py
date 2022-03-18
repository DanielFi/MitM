import os

from abc import ABC, abstractmethod

from connection import Connection
from mitm.handler_result import HandlerResult

class Handler(ABC):

    def __init__(self):
        self.init()

    def handle_outgoing_frame(self, frame) -> HandlerResult:
        return HandlerResult(b"", b"", False)

    def handle_incoming_frame(self, frame) -> HandlerResult:
        return HandlerResult(b"", b"", False)

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def get_frame(self, stream):
        raise NotImplementedError()

