from typing import Optional

import requests
from yarl import URL

from markdownup.cache.cache import Cache
from markdownup.markdownup import MarkdownUp


class BuiltinCache(Cache):

    def __init__(self, context: MarkdownUp):
        self.cache_url = URL(context.config.get('cache', 'bind'))

    def get(self, key: str) -> Optional[bytes]:
        url = str(self.cache_url / key)
        response = requests.get(url)
        return None if response.status_code == 404 else response.text

    def put(self, key: str, value: bytes):
        url = str(self.cache_url / key)
        response = requests.put(url, value)
        response.raise_for_status()