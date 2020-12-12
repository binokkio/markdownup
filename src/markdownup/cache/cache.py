from abc import ABC, abstractmethod
from typing import Optional


class Cache(ABC):

    @staticmethod
    def instance(context) -> 'Cache':
        cache_config = context.config.get('cache')
        cache_type = cache_config['type']

        if cache_type == 'builtin':
            from markdownup.cache.builtin.builtin_cache import BuiltinCache
            return BuiltinCache(context)
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
