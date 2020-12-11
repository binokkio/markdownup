from http.cookies import BaseCookie
from typing import Optional
from urllib.parse import parse_qs, urlencode
from uuid import uuid4

import jwt
import requests

from markdownup.auth.auth_provider import AuthProvider
from markdownup.helpers import rget
from markdownup.markdownup import MarkdownUp
from markdownup.response import Response


class Keycloak(AuthProvider):

    def __init__(self, context: MarkdownUp):

        self.cache = context.cache
        self.config = context.config
        self.client_id = context.config.get('access', 'auth', 'client_id')
        self.display_name_keys = context.config.get('access', 'auth', 'display_name')
        self.display_name_keys = self.display_name_keys.split('.') if self.display_name_keys else None
        self.roles_keys = context.config.get('access', 'auth', 'roles')
        self.roles_keys = self.roles_keys.split('.') if self.roles_keys else None

        base_url = \
            self.config.get('access', 'auth', 'auth_url').rstrip('/') + \
            '/realms/' + \
            self.config.get('access', 'auth', 'realm') + \
            '/protocol/openid-connect'

        self.auth_url = base_url + '/auth?' + urlencode({
            'client_id': self.client_id,
            'response_type': 'code'
        })

        self.token_url = base_url + '/token'

    def handle_request(self, environ) -> Optional[Response]:

        session_id = self._get_session_id(environ)
        cache_key = 'session/' + session_id

        # handle incoming Keycloak redirect
        query = parse_qs(environ['QUERY_STRING'])
        if 'code' in query:

            redirect_url = self._get_redirect_url(environ)

            token_response = requests.post(
                self.token_url,
                data={
                    'client_id': self.client_id,
                    'grant_type': 'authorization_code',
                    'code': query['code'][0],
                    'redirect_uri': redirect_url
                }
            )
            token_response.raise_for_status()

            access_token = token_response.json()['access_token']
            self.cache.put(cache_key, access_token)

            # set cookie and redirect to self (removes the keycloak query parameters)
            return self._get_redirect_response(redirect_url, session_id)
        else:
            access_token = self.cache.get(cache_key)

        if not access_token:  # TODO or expired
            location = self.auth_url + '&' + urlencode({'redirect_uri': self._get_redirect_url(environ)})
            return self._get_redirect_response(location, session_id)

        access_token = jwt.decode(access_token, verify=False)
        environ['access_token'] = access_token
        environ['auth'] = {
            'display_name': rget(access_token, *self.display_name_keys) if self.display_name_keys else None,
            'roles': set(rget(access_token, *self.roles_keys)) if self.roles_keys else None,
            'access_token': access_token
        }

        return None

    def _get_session_id(self, environ):
        cookies = BaseCookie(environ.get('HTTP_COOKIE', None))
        session_id = cookies['session'].value if 'session' in cookies else None
        if not session_id:
            while True:
                session_id = str(uuid4())
                if not self.cache.get('session/' + session_id):
                    break
        return session_id

    def _get_redirect_url(self, environ):
        # TODO include query params
        return self.config.get('access', 'auth', 'redirect_url') + (environ['PATH_INFO'] or '/')

    @staticmethod
    def _get_redirect_response(location: str, session_id):
        return Response(
            '302 Found', [
                ('Set-Cookie', f'session={session_id}'),
                ('Location', str(location))
            ], iter([]))
