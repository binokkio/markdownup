import re
from os.path import normpath
from pathlib import Path
from typing import List

import chevron
from markdown.inlinepatterns import Pattern

from markdownup.auth.auth_provider import AuthProvider
from markdownup.cache.cache import Cache
from markdownup.config import Config
from markdownup.filesystem.asset_file import AssetFile
from markdownup.filesystem.directory import Directory
from markdownup.response import Response
from markdownup.theme import Theme


class MarkdownUp:

    def __init__(self, config: Config):
        self.config = config
        self.cache: Cache = Cache.instance(self)
        self.exclusions: List[Pattern] = list(map(lambda e: re.compile(e), config.get('content', 'exclusions')))
        self.root_path: Path = Path(config.get('content', 'root')).resolve()
        self.root: Directory = Directory(self)
        self.theme: Theme = Theme(config)
        self.auth_provider: AuthProvider = AuthProvider.instance(self)

    def wsgi_app(self, environ, start_response):
        print(environ['REQUEST_METHOD'] + ' ' + environ['PATH_INFO'])
        response = self.get_response(environ)
        start_response(response.status, response.headers)
        yield from response.body

    def get_response(self, environ):

        if environ['REQUEST_METHOD'] != 'GET':
            return Response('405 Method Not Allowed')

        if self.auth_provider:
            auth_response = self.auth_provider.handle_request(environ)
            if auth_response:
                return auth_response

        response = self.get(environ['PATH_INFO'] or '/', environ)

        return response

    def get(self, path: str, environ=None) -> 'Response':

        environ = environ or {}

        # normalize path
        if not path.startswith('/'):
            return Response('400 Bad Request')
        abs_path = normpath(path)
        abs_path = Path(abs_path)
        rel_path = Path(*abs_path.parts[1:])

        # serve markdown
        file = self.root.resolve(environ, rel_path)
        if file:
            return file.get_response(environ)

        # serve theme file
        theme_file = self.theme.path / rel_path
        if theme_file.is_file():
            return AssetFile(theme_file).get_response(environ)

        # serve theme 404
        if self.theme.error_404:
            self.root.apply_access(environ)
            html = chevron.render(
                template=self.theme.error_404,
                partials_dict=self.theme.partials,
                data={
                    'title': '404 Not Found',
                    'root': self.root,
                    'auth': environ.get('auth', None)
                }
            )

            return Response(
                '404 Not Found',
                [('Content-Type', 'text/html')],
                (bytes(b, 'UTF-8') for b in html.splitlines(keepends=True))
            )

        # serve plain 404
        return Response('404 Not Found')
