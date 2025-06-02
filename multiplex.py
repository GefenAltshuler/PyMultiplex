import struct
import threading
import select
import sys


from utils import *

channels = {}

def handle_channel(channel, queue, sock, main_sock):
    while True:
        readable, _, _ = select.select([queue[0], sock], [], [])
        for r in readable:
            if r is queue[0]:
                data = r.get()
                logging.debug(f'channel {channel} queue received: {data}')
                sock.sendall(data)
            elif r is sock:
                data = r.recv(BUFFER_SIZE)
                if not data:
                    logging.info(f'channel {channel} socket closed')
                    close_channel(channel, main_sock)
                    sys.exit()
                logging.debug(f'channel {channel} socket received: {data}')
                message = build_message(channel, Message.data, data)
                main_sock.sendall(message)


def close_channel(channel: int, main_sock):
    logging.info(f'Channel {channel} closed')
    channels[channel][1].close()
    del channels[channel]
    close_message = build_message(channel, Message.close)
    main_sock.sendall(close_message)


def build_message(channel, code, data=''):
    message = struct.pack('!BBI', channel, code, len(data))

    return message


def handle_message(channel, code, data, main_sock):
    """
    Handle a channel message (open, data, close)
    """
    # init new channel queue and connection
    if code == Message.open:
        queue = socket.socketpair()
        sock = new_target_connection()
        channels[channel] = (queue, sock)
        t = threading.Thread(target=handle_channel, args=(channel, queue, sock, main_sock))
        t.start()

    # close requested channel
    elif code == Message.close:
        close_channel(channel, main_sock)  # todo: probably thread still alive, need to write error to select

    # receive data from channel
    elif code == Message.data:
        channels[channel][0][1].send(data)

    # unknown code found
    else:
        logging.error(f'Unknown code {code}')

def get_greeting_channel(main_sock: socket.socket):
    data = main_sock.recv(1)
    return struct.unpack('!B', data)[0]

def send_greeting_channel(client_sock: socket.socket, channel: int):
    client_sock.sendall(struct.pack('!B', channel))


def read_messages(main_sock: socket.socket):
    """
    Read channels data according to the messages protocol
    """
    headers = main_sock.recv(6)
    channel, code, length = struct.unpack('!BBI', headers)
    data = main_sock.recv(length)
    logging.debug(f'Data received: {channel}|{code}|{length}|{data}')
    handle_message(channel, code, data, main_sock)
    if code == Message.data:
        return data
    else:
        return None

