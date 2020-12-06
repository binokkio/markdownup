from abc import ABC, abstractmethod

from markdownup.response import Response


class File(ABC):

    @abstractmethod
    def get_response(self, environ) -> Response:
        raise NotImplemented
