from pathlib import Path

import markdown


class MarkdownUp:

    def __init__(self, config):
        self.config = config
        self.root = config['content']['root']

    def wsgi_app(self, environ, start_response):

        if environ['REQUEST_METHOD'] != 'GET':
            start_response('405 Method Not Allowed', 'text/plain')
            return ['405 Method Not Allowed']

        request_path = Path(environ['PATH_INFO'][1:])
        root_request_path = self.root / request_path

        if not root_request_path.exists():
            start_response('404 Not Found', [])
            return

        with root_request_path.open('r') as file:
            source = file.read()
            html = markdown.markdown(source)
            start_response('200 OK', [('Content-Type', 'text/html')])
            yield from (bytes(b, 'UTF-8') for b in html.splitlines())
