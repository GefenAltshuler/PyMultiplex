from queue import Queue
from Message import Message, MessageCode


class ChannelSocket:
    def __init__(self, channel: int):
        super().__init__()
        self._queue = Queue()
        self._channel = channel
        self.is_open = True

    def get(self):
        return self._queue.get()

    def put(self, data: bytes):
        return self._queue.put(data)

    def recv(self, _):
        return self.get()

    def sendall(self, data: bytes):
        return self.put(data)

    def close(self):
        self.is_open = False

    def get_closing_message(self):
        close_channel_message = Message(self._channel, MessageCode.close).to_bytes()
        return self.put(close_channel_message)  # todo: understand how this message will come to the remote endpoint


