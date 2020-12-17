class Response:
    def __init__(self, status: str, headers=None, body=None):
        self.status = status
        self.headers = headers or []
        self.body = body

        if not body:
            self.body = iter([bytes(status, 'UTF-8')])
            self.headers.append(('Content-Type', 'text/plain'))


class ResponseException(BaseException):
    def __init__(self, status: str, headers=None, body=None):
        self.response = Response(status, headers, body)
