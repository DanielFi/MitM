import os

from abc import ABC, abstractmethod

from .handler_result import HandlerResult, HANDLER_RESULT_FORWARD

class Handler(ABC):

    def __init__(self):
        self.handle_connected()

    def handle_outgoing_frame(self, frame) -> HandlerResult:
        return HANDLER_RESULT_FORWARD

    def handle_incoming_frame(self, frame) -> HandlerResult:
        return HANDLER_RESULT_FORWARD

    def handle_connected(self):
        pass

    def handle_disconnected(self):
        pass

    @abstractmethod
    def get_frame(self, stream):
        raise NotImplementedError()

