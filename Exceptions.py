class MaxChannelsReached(Exception):
    pass

class UnknownProtocolMessage(Exception):
    def __init__(self, data: bytes):
        super().__init__(f"Unknown protocol message: {data.hex()}")

class ProtocolInitializationFailed(UnknownProtocolMessage):
    pass

class RemoteSocketClosed(Exception):
    pass

