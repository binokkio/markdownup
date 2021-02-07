import json
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
        self.roles_keys = context.config.get('access', 'auth', 'roles') or []
        self.roles_keys = list(map(lambda s: s.split('.'), self.roles_keys))

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
        query = parse_qs(environ['QUERY_STRING'])

        if 'login' in query and query['login'][0] == 'yes':
            location = self.auth_url + '&' + urlencode({'redirect_uri': self._get_redirect_url(environ)})
            return self._get_redirect_response(location, session_id)

        if 'logout' in query and query['logout'][0] == 'yes':
            self.cache.delete(cache_key)
            return self._get_redirect_response(self._get_redirect_url(environ), session_id)

        # handle incoming Keycloak redirect
        if 'code' in query:

            redirect_url = self._get_redirect_url(environ)

            token_response = requests.post(
                self.token_url,
                data={
                    'client_id': self.client_id,
                    'grant_type': 'authorization_code',
                    'code': query['code'][0],
                    'redirect_uri': redirect_url
                })
            token_response.raise_for_status()

            access_token = token_response.json()['access_token']
            access_token = jwt.decode(access_token, options={'verify_signature': False})

            cache_value = {
                'display_name': rget(access_token, *self.display_name_keys) if self.display_name_keys else None,
                'roles': list(self._get_roles(access_token)),
                'access_token': access_token
            }

            self.cache.put(cache_key, json.dumps(cache_value).encode('UTF-8'))
            return self._get_redirect_response(redirect_url, session_id)

        cache_value = self.cache.get(cache_key)
        if cache_value:  # TODO and not expired
            cache_value = json.loads(cache_value)
            cache_value['roles'] = set(cache_value['roles'])
            environ['auth']['authenticated'] = cache_value

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
        return self.config.get('access', 'auth', 'redirect_url') + (environ['PATH_INFO'] or '/')

    @staticmethod
    def _get_redirect_response(location: str, session_id):
        return Response(
            '302 Found', [
                ('Set-Cookie', f'session={session_id}'),
                ('Location', str(location))
            ], iter([]))

    def _get_roles(self, access_token):
        roles = set()
        for roles_keys in self.roles_keys:
            value = rget(access_token, *roles_keys)
            if isinstance(value, list):
                roles.update(value)
            else:
                roles.add(value)
        return roles
