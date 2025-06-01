import struct
from queue import Queue
from typing import Dict
from utils import *


channels: Dict[int, tuple[Queue, socket.socket]] = {}


def read_channels_socket(communication_socket):
    channels_socket = [s[SOCKET] for s in channels.values()]
    socket_to_channel = {items[SOCKET]: channel for channel, items in channels.items()}
    readable, _, _ = select.select(channels_socket, [], [], 1)

    for ch_socket in readable:
        data = ch_socket.recv(BUFFER_SIZE)
        channel = socket_to_channel[ch_socket]
        if not data:
            logging.info(f'channel {channel} socket closed')
            close_channel(channel)
        else:
            logging.debug(f'channel {channel} socket received: {data}')
            message = build_message(channel, Message.data, data)
            communication_socket.sendall(message)


def read_channels_queues():
    channels_queues = [s[QUEUE] for s in channels.values()]
    queues_to_channel = {items[QUEUE]: channel for channel, items in channels.items()}
    readable, _, _ = select.select(channels_queues, [], [], 1)

    for ch_queue in readable:
        data = ch_queue.get()
        channel = queues_to_channel[ch_queue]
        logging.debug(f'channel {channel} queue received: {data}')
        channels[channel][1].sendall(data)


def safe_channel_io(channel: int, io_type, data):
    if channel in channels.keys():
        channels[channel][io_type].put(data)
    else:
        logging.error(f'Channel {channel} not found')


def close_channel(channel: int):
    channels[channel][1].close()
    del channels[channel]
    logging.info(f'Channel {channel} closed')


def send_message(channel, message):
    channels[channel][0].put(message)


def build_message(channel, code, data):
    message = struct.pack('!BBI', channel, code, len(data))

    return message + data


def handle_message(channel, code, data):
    """
    Handle a channel message (open, data, close)
    """
    # init new channel queue and connection
    if code == Message.open:
        channels[channel] = (Queue(), new_target_connection())

    # close requested channel
    elif code == Message.close:
        close_channel(channel)

    # receive data from channel
    elif code == Message.data:
        safe_channel_io(channel, QUEUE, data)

    # unknown code found
    else:
        logging.error(f'Unknown code {code}')

def read_messages(sock: socket.socket):
    """
    Read channels data according to the messages protocol
    """
    while True:
        channel, code, length = struct.unpack('!BBI', sock.recv(6))[0]
        data = sock.recv(length)
        logging.debug(f'Data received: {channel}|{code}|{length}|{data}')
        handle_message(channel, code, data)


def write_channel_data(channel: int, data: bytes):
    """
    Write channel data according to the messages protocol
    """
    message = struct.pack('!BBI', channel, Message.data, len(data))
    logging.info(f'Sending message: {channel}|{Message.data}|{len(data)}|{data}')
    safe_channel_io(channel, SOCKET, message + data)