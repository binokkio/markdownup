from typing import Dict

from gunicorn.app.base import BaseApplication

from markdownup.config import Config


class CacheApplication(BaseApplication):

    def __init__(self, config: Config):
        self.config = config
        self.cache: Dict[str, bytes] = {}  # TODO swap for an LRU cache
        super().__init__()

    def init(self, parser, options, args):
        pass

    def load_config(self):
        self.cfg.set('bind', self.config.get('cache', 'bind'))
        self.cfg.set('workers', 1)

    def load(self):
        return self.wsgi_app

    def wsgi_app(self, environ, start_response):

        method = environ['REQUEST_METHOD']
        key = environ['PATH_INFO'] or '/'

        if method == 'PUT':
            value = environ['wsgi.input'].read()
            self.cache[key] = value
            start_response('200 OK', [])
            yield from iter([])
        elif method == 'GET':
            value = self.cache.get(key, None)
            if value is not None:
                start_response('200 OK', [])
                yield from iter([value])
            else:
                start_response('404 Not Found', [])
                yield from iter([])
        elif method == 'DELETE':
            self.cache.pop(key, None)
            start_response('200 OK', [])
            yield from iter([])
        else:
            start_response('405 Method Not Allowed', [])
            yield from iter([])
