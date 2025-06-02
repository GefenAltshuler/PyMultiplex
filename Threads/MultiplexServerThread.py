import socket

from Channel.Message import Message, MessageCode
from Channel.Socket import ChannelSocket
from Threads.MultiplexThread import MultiplexThread
from utils.consts import DEFAULT_BIND_ADDRESS, MAX_CLIENTS


class MultiplexServerThread(MultiplexThread):
    def init_new_channel(self, pipe_socket: socket.socket):
        # new channel
        channel_id = self.get_new_channel_id()
        channel_socket = ChannelSocket(channel_id, self._remote_sock)
        self._channels[channel_id] = channel_socket

        # remote new channel
        open_channel_message = Message(channel_id, MessageCode.open)
        self._send_message(open_channel_message)

        # pipe between socket <-> channel
        MultiplexServerThread._open_pipe(channel_socket, pipe_socket)

    def _forward_listen(self, pipe_port: int):
        pipe_listen_socket = socket.socket()
        bind_address = (DEFAULT_BIND_ADDRESS, pipe_port)

        # start listen for incoming connections
        pipe_listen_socket.bind(bind_address)
        pipe_listen_socket.listen(MAX_CLIENTS)
        self._logger.info(f"Listening on {bind_address}")

        while True:
            pipe_socket, pipe_client_address = pipe_listen_socket.accept()
            self._logger.info(f"Connected by {pipe_client_address}")
            self.init_new_channel(pipe_socket)
