import hashlib
import mimetypes
import struct
from pathlib import Path

from markdownup.filesystem.file import File
from markdownup.response import Response


class AssetFile(File):

    def __init__(self, context, path: Path):
        super().__init__(context, path)
        if context.config.get('content', 'etag_assets'):
            if self.version:
                self.etag = f'"{self.version["hash"]}"'
            else:
                modified_time = path.stat().st_mtime
                as_bytes = struct.pack('f', modified_time)
                as_hash = hashlib.sha1(as_bytes).hexdigest()
                self.etag = f'"{as_hash}"'
        else:
            self.etag = None

    def get_response(self, environ) -> Response:

        if self.etag and environ.get('HTTP_IF_NONE_MATCH', None) == self.etag:
            return Response('304 Not Modified', [], [])

        file_size = self.path.stat().st_size
        guessed_mimetype = mimetypes.guess_type(self.path.name)[0]

        def reader():
            with self.path.open('rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    yield data

        headers = [
            ('Content-Type', guessed_mimetype or 'application/octet-stream'),
            ('Content-Length', str(file_size))
        ]

        if self.etag:
            headers.append(('ETag', self.etag))

        return Response('200 OK', headers, reader())
