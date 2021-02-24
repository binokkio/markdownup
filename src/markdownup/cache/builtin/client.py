import socket
from typing import Optional

from markdownup.cache.cache import Cache
from markdownup.markdownup import MarkdownUp


class BuiltinCacheClient(Cache):

    def __init__(self, context: MarkdownUp):
        self.server = (context.config.get('cache', 'host'), context.config.get('cache', 'port'))

    def get(self, key: str) -> Optional[bytes]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.server)
            sock.sendall(b'GET')
            self._send_bytes(sock, key.encode('UTF-8'))
            if sock.recv(3) != b'200':
                return None
            value_length = int.from_bytes(sock.recv(8), byteorder='big')
            return sock.recv(value_length)

    def put(self, key: str, value: bytes) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.server)
            sock.sendall(b'PUT')
            self._send_bytes(sock, key.encode('UTF-8'))
            self._send_bytes(sock, value)
            if sock.recv(3) != b'200':
                raise

    def delete(self, key: str) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.server)
            sock.sendall(b'DEL')
            self._send_bytes(sock, key.encode('UTF-8'))
            if sock.recv(3) != b'200':
                raise

    @staticmethod
    def _send_bytes(sock: socket.socket, b):
        sock.sendall(int.to_bytes(len(b), 8, byteorder='big'))
        sock.sendall(b)
