import mimetypes
from os.path import normpath
from pathlib import Path

from markdownup.access_control import AccessControl
from markdownup.config import Config
from markdownup.directory import Directory
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

            if not self.global_access_control.is_access_allowed(abs_path):
                return Response('403 Forbidden')

            return file.get_response()

        # serve asset file
        asset_file = self.root_path / rel_path
        if asset_file.is_file():
            if not self.global_access_control.is_access_allowed(abs_path):
                return Response('403 Forbidden')
            else:
                return self.serve_file(asset_file)

        # serve theme file
        theme_file = self.theme.path / rel_path
        if theme_file.is_file():
            return self.serve_file(theme_file)

        # serve 404
        return Response('404 Not Found')

    @staticmethod
    def serve_file(path: Path):

        guessed_mimetype = mimetypes.guess_type(path.name)[0]

        def reader():
            with path.open('rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    yield data

        return Response(
            '200 OK',
            [('Content-Type', guessed_mimetype or 'application/octet-stream')],
            reader()
        )
