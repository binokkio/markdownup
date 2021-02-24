from socketserver import TCPServer, BaseRequestHandler
from typing import Any

from markdownup.config import Config


class BuiltinCacheServer(TCPServer):
    def __init__(self, config: Config):
        super().__init__((
            config.get('cache', 'host'),
            config.get('cache', 'port')
        ), _BuiltinCacheHandler)
        self.cache = {}


class _BuiltinCacheHandler(BaseRequestHandler):

    def __init__(self, request: Any, client_address: Any, server: BuiltinCacheServer):
        super().__init__(request, client_address, server)
        self.server: BuiltinCacheServer = server

    def handle(self) -> None:
        action = self.request.recv(3).decode('UTF-8')
        key_length = int.from_bytes(self.request.recv(8), byteorder='big')
        key = self.request.recv(key_length).decode('UTF-8')
        if action == 'GET':
            value = self.server.cache.get(key, None)
            if value is None:
                self.request.sendall(b'404')
            else:
                self.request.sendall(b'200')
                self.request.sendall(int.to_bytes(len(value), 8, byteorder='big'))
                self.request.sendall(value)
        elif action == 'PUT':
            value_length = int.from_bytes(self.request.recv(8), byteorder='big')
            value = self.request.recv(value_length)
            self.server.cache[key] = value
            self.request.sendall(b'200')
        elif action == 'DEL':
            self.server.cache.pop(key, None)
            self.request.sendall(b'200')
        else:
            self.request.sendall(b'400')
