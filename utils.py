import random
import logging
import socket

from enum import IntEnum

class Message(IntEnum):
    open = 1
    data = 2
    close = 3

QUEUE = 0
SOCKET = 1
BUFFER_SIZE = 1024

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class MaxChannelsReached(Exception):
    pass

def get_channel_number(channels):
    channel = random.randint(1, 255)

    if len(channels) >= 254:
        raise MaxChannelsReached

    if channel in channels.keys():
        return get_channel_number()

    return channel

def new_target_connection(target_address):
    """
    Create a new target connection
    """
    sock = socket.socket()
    sock.connect(target_address)

    return sock