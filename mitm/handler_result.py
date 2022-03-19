from dataclasses import dataclass

@dataclass
class HandlerResult:
    client_data: bytes
    server_data: bytes
    should_drop: bool


HANDLER_RESULT_DROP = HandlerResult(b"", b"", True)
HANDLER_RESULT_FORWARD = HandlerResult(b"", b"", False)
