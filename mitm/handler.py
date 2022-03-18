from abc import ABC, abstractmethod


class Handler(ABC):

    def __init__(self):
        self.init()

    def init(self):
        pass

    @abstractmethod
    def get_frame(self, stream):
        raise NotImplementedError()

    @abstractmethod
    def handle_outgoing_frame(self, frame):
        return True
    
    @abstractmethod
    def handle_incoming_frame(self, frame):
        return True
