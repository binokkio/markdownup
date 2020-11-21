import re
from pathlib import Path

import chevron
import markdown


_title_pattern = re.compile(r'^#\s?(.*)')


class MarkdownUp:

    def __init__(self, config):
        self.config = config
        self.root = Path(config['content']['root']).resolve()
        self.theme = _read_theme(config['content']['theme'])

    def wsgi_app(self, environ, start_response):

        if environ['REQUEST_METHOD'] != 'GET':
            start_response('405 Method Not Allowed', 'text/plain')
            return ['405 Method Not Allowed']

        request_path = environ['PATH_INFO'] or '/'
        request_path = request_path[1:]

        response = self.get(request_path)
        start_response(response.status, response.headers)
        yield from response.body

    def get(self, path: str) -> 'Response':

        path = self.root / path
        path = path.resolve()

        if not str(path).startswith(str(self.root)):  # TODO must be a better way
            return Response('400 Bad Request')

        if not path.exists():
            return Response('404 Not Found')

        if path.is_dir():
            path = path / 'index.md'  # TODO configurable, multiple options

        with path.open('r') as file:

            source = file.read()

            html = chevron.render(self.theme, {
                'title': self.get_title(source),
                'content': markdown.markdown(source)
            })

            return Response(
                '200 OK',
                [('Content-Type', 'text/html')],
                (bytes(b, 'UTF-8') for b in html.splitlines(keepends=True))
            )

    @staticmethod
    def get_title(md: str):
        match = _title_pattern.match(md)
        return match.group(1) if match else 'Untitled document'


class Response:
    def __init__(self, status: str, headers=None, body=None):
        self.status = status
        self.headers = headers or []
        self.body = body or iter(())


def _read_theme(theme: str):

    path = Path(theme)
    if not path.is_dir():
        path = Path(__file__).parent / 'themes' / theme
        if not path.is_dir():
            raise ValueError(f'Theme "{theme}" not found')  # TODO improve feedback

    path = path / 'frame.html'

    if not path.is_file():
        raise ValueError('Theme does not contain a file named "frame.html"')

    return path.read_text()
