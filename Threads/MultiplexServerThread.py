import socket

from Channel.Message import Message, MessageCode
from Channel.Socket import ChannelSocket
from MultiplexThread import MultiplexThread


class MultiplexServerThread(MultiplexThread):
    def __init__(self, pipe_socket: socket.socket, *args, **kwargs) -> None:
        self._pipe_socket = pipe_socket
        super().__init__(*args, **kwargs)

    def init_new_channel(self):
        # local create new channel
        channel_id = self.get_new_channel_id()
        channel_socket = ChannelSocket(channel_id)
        self._channels[channel_id] = channel_socket

        # remote create new channel
        open_channel_message = Message(channel_id, MessageCode.open)
        self._send_message(open_channel_message)
        self._open_pipe(channel_socket)

    def _get_pipe_socket(self):
        return self._pipe_socket
