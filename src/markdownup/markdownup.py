import mimetypes
from os.path import normpath
from pathlib import Path

import chevron
import markdown
from markdownup.access_control import AccessControl
from markdownup.markdown_directory import MarkdownDirectory
from markdownup.theme import Theme


class MarkdownUp:

    def __init__(self, config):
        self.config = config
        self.access_control = AccessControl(config)
        self.root_path = Path(config['content']['root']).resolve()
        self.root = MarkdownDirectory(self)
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
        markdown_file = self.root.resolve(rel_path)
        if markdown_file:

            if not self.access_control.is_access_allowed(abs_path):  # TODO use environ for more advanced access control
                return Response('403 Forbidden')

            source = markdown_file.read()

            html = chevron.render(
                template=self.theme.frame,
                partials_path=str(self.theme.path),
                partials_ext='html',
                data={
                    'title': markdown_file.title,
                    'file': markdown_file,
                    'content': markdown.markdown(source, extensions=self.config['markdown']['extensions']),
                    'root': self.root
                }
            )

            return Response(
                '200 OK',
                [('Content-Type', 'text/html')],
                (bytes(b, 'UTF-8') for b in html.splitlines(keepends=True))
            )

        # serve asset file
        asset_file = self.root_path / rel_path
        if asset_file.is_file():
            if not self.access_control.is_access_allowed(abs_path):  # TODO use environ for more advanced access control
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


class Response:
    def __init__(self, status: str, headers=None, body=None):
        self.status = status
        self.headers = headers or []
        self.body = body or iter([bytes(status, 'UTF-8')])
