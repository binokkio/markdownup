from pathlib import Path

import markdown


class MarkdownUp:

    def __init__(self, config):
        self.config = config
        self.root = Path(config['content']['root']).resolve()

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
            html = markdown.markdown(source)
            return Response(
                '200 OK',
                [('Content-Type', 'text/html')],
                (bytes(b, 'UTF-8') for b in html.splitlines())
            )


class Response:
    def __init__(self, status: str, headers=None, body=None):
        self.status = status
        self.headers = headers or []
        self.body = body or iter(())
