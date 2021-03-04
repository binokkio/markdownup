import mimetypes

from markdownup.filesystem.file import File
from markdownup.response import Response


class AssetFile(File):

    def get_response(self, environ) -> Response:

        file_size = self.path.stat().st_size
        guessed_mimetype = mimetypes.guess_type(self.path.name)[0]

        def reader():
            with self.path.open('rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    yield data

        return Response(
            '200 OK',
            [
                ('Content-Type', guessed_mimetype or 'application/octet-stream'),
                ('Content-Length', str(file_size))
            ],
            reader()
        )
