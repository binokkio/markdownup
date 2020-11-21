import mimetypes
import re
from pathlib import Path
from typing import Optional

import chevron
import markdown
from markdownup.path_resolver import resolve_str

_title_pattern = re.compile(r'^#\s?(.*)')


class MarkdownUp:

    def __init__(self, config):
        self.config = config
        self.root = Path(config['content']['root']).resolve()
        self.theme = Theme(config['main']['theme'])

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

        try:
            path = self._get_content_path(path) or \
                   self._get_theme_path(path)
        except ValueError:
            return Response('400 Bad Request')

        if not path or not path.exists():
            return Response('404 Not Found')

        guessed_mimetype = mimetypes.guess_type(path.name)[0]

        if guessed_mimetype == 'text/markdown':

            with path.open('r') as file:

                source = file.read()

                html = chevron.render(self.theme.frame, {
                    'title': self.get_title(source),
                    'content': markdown.markdown(source, extensions=self.config['markdown']['extensions'])
                })

                return Response(
                    '200 OK',
                    [('Content-Type', 'text/html')],
                    (bytes(b, 'UTF-8') for b in html.splitlines(keepends=True))
                )
        else:

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

    def _get_content_path(self, path: str) -> Optional[Path]:

        path = resolve_str(self.root, path)

        if path.is_file():
            return path

        if path.is_dir():
            for index in self.config['content']['indices']:
                index = path / index
                if index.is_file():
                    return index

        return None

    def _get_theme_path(self, path: str) -> Optional[Path]:
        path = resolve_str(self.theme.path, path)
        return path if path.is_file() else None

    @staticmethod
    def get_title(md: str):
        match = _title_pattern.match(md)
        return match.group(1) if match else 'Untitled document'


class Response:
    def __init__(self, status: str, headers=None, body=None):
        self.status = status
        self.headers = headers or []
        self.body = body or iter(())


class Theme:

    def __init__(self, theme: str):
        self.path = self._resolve_path(theme)
        self.frame = self._read_frame()

    @staticmethod
    def _resolve_path(theme: str):
        path = Path(theme)
        if not path.is_dir():
            path = Path(__file__).parent / 'themes' / theme
            if not path.is_dir():
                raise ValueError(f'Theme "{theme}" not found')  # TODO improve feedback
        return path

    def _read_frame(self):
        path = self.path / 'frame.html'
        if not path.is_file():
            raise ValueError('Theme does not contain a file named "frame.html"')
        return path.read_text()
