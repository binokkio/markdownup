from os.path import normpath
from pathlib import Path

from markdownup.access_control import AccessControl
from markdownup.auth.auth_provider import AuthProvider
from markdownup.config import Config
from markdownup.filesystem.asset_file import AssetFile
from markdownup.filesystem.directory import Directory
from markdownup.response import Response
from markdownup.theme import Theme


class MarkdownUp:

    def __init__(self, config: Config):
        self.config = config
        self.global_access_control = AccessControl(config.get('access', 'global'))
        self.root_path = Path(config.get('content', 'root')).resolve()
        self.root = Directory(self)
        self.theme = Theme(config)
        self.auth_provider = AuthProvider.instance(config)

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

        if self.auth_provider:
            response = self.auth_provider.handle_response(environ, response)

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

        # serve 404
        return Response('404 Not Found')
