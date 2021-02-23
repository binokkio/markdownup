from abc import ABC, abstractmethod
from typing import Optional


class Cache(ABC):

    @staticmethod
    def instance(context) -> 'Cache':
        cache_type = context.config.get('cache', 'type')

        if cache_type == 'builtin':
            from markdownup.cache.builtin.client import BuiltinCacheClient
            return BuiltinCacheClient(context)
        elif cache_type == 'redis':
            from markdownup.cache.redis.redis_cache import RedisCache
            return RedisCache(context)
        else:
            raise ValueError('Unknown cache type: ' + cache_type)

    @abstractmethod
    def get(self, key: str) -> Optional[bytes]:
        raise NotImplementedError()

    @abstractmethod
    def put(self, key: str, value: bytes) -> None:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError()
