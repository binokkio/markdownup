class Response:
    def __init__(self, status: str, headers=None, body=None):
        self.status = status
        self.headers = headers or []
        self.body = body or iter([bytes(status, 'UTF-8')])
