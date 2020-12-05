from os.path import normpath
from pathlib import Path

from markdownup.access_control import AccessControl
from markdownup.config import Config
from markdownup.directory import Directory
from markdownup.file.asset_file import AssetFile
from markdownup.response import Response
from markdownup.theme import Theme


class MarkdownUp:

    def __init__(self, config: Config):
        self.config = config
        self.global_access_control = AccessControl(config.get('access', 'global'))
        self.root_path = Path(config.get('content', 'root')).resolve()
        self.root = Directory(self)
        self.theme = Theme(config)

    def wsgi_app(self, environ, start_response):

        print(environ['REQUEST_METHOD'] + ' ' + environ['PATH_INFO'])

        if environ['REQUEST_METHOD'] != 'GET':
            start_response('405 Method Not Allowed', 'text/plain')
            return ['405 Method Not Allowed']

        request_path = environ['PATH_INFO'] or '/'

        response = self.get(request_path)
        start_response(response.status, response.headers)
        yield from response.body

    def get(self, path: str, environ=None) -> 'Response':

        environ = environ or {}

        # normalize path
        if not path.startswith('/'):
            return Response('400 Bad Request')
        abs_path = normpath(path)
        abs_path = Path(abs_path)
        rel_path = Path(*abs_path.parts[1:])

        # serve markdown
        file = self.root.resolve(rel_path)
        if file:
            return file.get_response()

        # serve theme file
        theme_file = self.theme.path / rel_path
        if theme_file.is_file():
            return AssetFile(theme_file).get_response()

        # serve 404
        return Response('404 Not Found')
