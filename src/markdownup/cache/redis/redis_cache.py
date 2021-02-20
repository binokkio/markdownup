from typing import Optional

from redis import Redis

from markdownup.cache.cache import Cache
from markdownup.markdownup import MarkdownUp


class RedisCache(Cache):

    def __init__(self, context: MarkdownUp):
        self.redis: Redis = Redis(
            host=context.config.get('cache', 'host'),
            port=context.config.get('cache', 'port'),
            db=context.config.get('cache', 'db'),
        )
        self.key_prefix = context.config.get('cache', 'prefix') or 'markdownup/'

    def get(self, key: str) -> Optional[bytes]:
        return self.redis.get(self.key_prefix + key)

    def put(self, key: str, value: bytes) -> None:
        self.redis.set(self.key_prefix + key, value)

    def delete(self, key: str) -> None:
        self.redis.delete(self.key_prefix + key)
