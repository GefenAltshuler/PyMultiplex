import struct
from enum import IntEnum

class MessageCode(IntEnum):
    bind = 1
    open = 2
    data = 3
    close = 4

class Message:
    def __init__(self, channel: int, code: MessageCode, data: bytes = b''):
        self.channel = channel
        self.code = code
        self.data = data

    def to_bytes(self) -> bytes:  # todo: prevent serialization -> deserialization -> serialization between Server and Thread
        return struct.pack('!BBI', self.channel, self.code, len(self.data)) + self.data


# TODO: add specific Message class for each enum value (or create factory)