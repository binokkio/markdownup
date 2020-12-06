from abc import ABC
from typing import Optional

from markdownup.response import Response


class AuthProvider(ABC):

    @staticmethod
    def instance(config):
        auth_config = config.get('access', 'auth')
        if auth_config:
            auth_type = auth_config.get('type', None)
            if auth_type is None:
                raise ValueError('Config auth section found but type key is missing')
            elif auth_type == 'keycloak':
                from markdownup.auth.keycloak import Keycloak
                return Keycloak(config)
            else:
                raise ValueError('Unknown auth type: ' + auth_type)
        else:
            return None

    def handle_request(self, environ) -> Optional[Response]:
        return None

    def handle_response(self, environ, response) -> Response:
        return response
