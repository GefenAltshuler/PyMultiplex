import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

MAX_CLIENTS = 10
MIN_CHANNELS = 1
MAX_CHANNELS = 255
HEADERS_SIZE = 6
BUFFER_SIZE = 1024
DEFAULT_BIND_ADDRESS = "0.0.0.0"