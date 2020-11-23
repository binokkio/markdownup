import mimetypes

import chevron
import markdown
from markdownup.markdown_directory import MarkdownDirectory
from markdownup.path_resolver import resolve_str
from markdownup.theme import Theme


class MarkdownUp:

    def __init__(self, config):
        self.config = config
        self.root = MarkdownDirectory(config)
        self.theme = Theme(config)

    def wsgi_app(self, environ, start_response):

        print(environ['REQUEST_METHOD'] + ' ' + environ['PATH_INFO'])

        if environ['REQUEST_METHOD'] != 'GET':
            start_response('405 Method Not Allowed', 'text/plain')
            return ['405 Method Not Allowed']

        request_path = environ['PATH_INFO'] or '/'
        request_path = request_path[1:]

        response = self.get(request_path)
        start_response(response.status, response.headers)
        yield from response.body

    def get(self, path: str) -> 'Response':

        markdown_file = self.root.resolve(path)

        if markdown_file:

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

        try:
            path = resolve_str(self.root.path, path) or \
                   resolve_str(self.theme.path, path)
            if not path.is_file():
                return Response('404 Not Found')
        except ValueError:
            return Response('400 Bad Request')

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
        self.body = body or iter(())
