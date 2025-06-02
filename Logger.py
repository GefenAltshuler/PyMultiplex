import logging
from typing import Callable


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Logger:
    def __init__(self, obj):
        self._obj = obj

    def error(self, log: str):
        self.log(log, logging.error)

    def info(self, log: str):
        self.log(log, logging.info)

    def debug(self, log: str):
        self.log(log, logging.debug)

    def log(self, log: str, func: Callable):
        func(f"{self._obj.__class__.__name__} [{self._obj.ident}]: {log}")

    @staticmethod
    def inner_debug(log: str, cls: type):
        logging.debug(f"{cls.__name__}: {log}")

