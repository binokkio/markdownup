from abc import ABC
from typing import Optional

from markdownup.response import Response


class AuthProvider(ABC):

    @staticmethod
    def instance(context):
        auth_config = context.config.get('access', 'auth')
        if auth_config:
            auth_type = auth_config.get('type', None)
            if auth_type is None:
                raise ValueError('Config auth section found but type key is missing')
            elif auth_type == 'keycloak':
                from markdownup.auth.keycloak.keycloak import Keycloak
                return Keycloak(context)
            elif auth_type == 'basic-auth':
                from markdownup.auth.basicauth.basic_auth import BasicAuth
                return BasicAuth(context)
            else:
                raise ValueError('Unknown auth type: ' + auth_type)
        else:
            return None

    def handle_request(self, environ) -> Optional[Response]:
        return None
