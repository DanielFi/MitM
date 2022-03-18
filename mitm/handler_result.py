from dataclasses import dataclass

@dataclass
class HandlerResult:
    client_data: bytes
    server_data: bytes
    should_drop: bool
