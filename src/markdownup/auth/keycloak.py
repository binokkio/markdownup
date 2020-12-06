from http.cookies import BaseCookie
from typing import Optional
from urllib.parse import parse_qs
from uuid import uuid4

import requests
import jwt
from keycloak import KeycloakOpenID
from markdownup.auth.auth_provider import AuthProvider
from markdownup.cache_application import CacheApplication
from markdownup.config import Config
from markdownup.response import Response


class Keycloak(AuthProvider):

    def __init__(self, config: Config):

        self.config = config
        self.auth_config = config.get('access', 'auth')
        self.cache_url = f'http://{CacheApplication.get_bind(config)}/'

        self.keycloak = KeycloakOpenID(
            server_url=self.auth_config['server_url'],
            client_id=self.auth_config['client_id'],
            realm_name=self.auth_config['realm_name']
        )

        self.well_known = self.keycloak.well_know()

    def handle_request(self, environ) -> Optional[Response]:

        # handle session cookie
        cookies = BaseCookie(environ.get('HTTP_COOKIE', None))
        session_id = cookies['session'].value if 'session' in cookies else None
        if not session_id:
            while True:
                session_id = str(uuid4())
                if not self.get_cached_value('session/' + session_id):
                    break
        cache_key = 'session/' + session_id

        # build redirect url
        redirect_url = self.auth_config['redirect_url'] + (environ['PATH_INFO'] or '/')  # TODO include query params

        # handle incoming Keycloak redirect
        query = parse_qs(environ['QUERY_STRING'])
        if 'code' in query:
            token = self.keycloak.token(
                grant_type='authorization_code',
                code=query['code'][0],
                redirect_uri=redirect_url
            )
            cache_value = token['access_token']
            requests.put(self.cache_url + cache_key, cache_value)
            # TODO redirect to get rid of Keycloak query params
        else:
            cache_value = self.get_cached_value(cache_key)

        if not cache_value:  # TODO or expired
            # set cookie and redirect to auth url
            return Response(
                '302 Found', [
                    ('Set-Cookie', f'session={session_id}'),
                    ('Location', self.keycloak.auth_url(redirect_url))
                ], iter([]))

        decoded = jwt.decode(cache_value, verify=False)
        environ['roles'] = set(decoded['realm_access']['roles'])
        return None

    def handle_response(self, environ, response) -> Response:
        return response

    def get_cached_value(self, path):
        response = requests.get(self.cache_url + path)
        if response.status_code == 404:
            return None
        else:
            return response.text
