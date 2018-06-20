import socket

class P2PServer(object):
    def __init__(self, port=37676, time=120):
        self.port = port
        self.time = time

    def listern_response(self):
        pass

    def broadcast(self, data):
        pass
