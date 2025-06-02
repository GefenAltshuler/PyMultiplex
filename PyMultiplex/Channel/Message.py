import struct
from enum import IntEnum
import socket
import binascii

from PyMultiplex.Channel.Exceptions import RemoteSocketClosed, UnknownProtocolMessage
from PyMultiplex.utils.consts import HEADERS_SIZE

from PyMultiplex.utils.Logger import Logger

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

    @staticmethod
    def recv(sock: socket.socket):
        headers = sock.recv(HEADERS_SIZE)
        if not headers: raise RemoteSocketClosed
        try:
            channel, code, length = struct.unpack('!BBI', headers)
            data = sock.recv(length)
            Logger.inner_debug(f'Data received: {channel}|{code}|{length}|{binascii.hexlify(data)}', Message)
        except struct.error:
            raise UnknownProtocolMessage(headers)

        return Message(channel, code, data)

# TODO: add specific Message class for each enum value (or create factory), so outside wont have to deal with Message building