from http.cookies import BaseCookie
from typing import Optional
from urllib.parse import parse_qs
from uuid import uuid4

import jwt
import requests
from yarl import URL

from markdownup.auth.auth_provider import AuthProvider
from markdownup.markdownup import MarkdownUp
from markdownup.response import Response


class Keycloak(AuthProvider):

    def __init__(self, context: MarkdownUp):

        self.cache = context.cache
        self.config = context.config
        self.auth_config = context.config.get('access', 'auth')

        base_url = \
            URL(self.auth_config['auth_url']) / \
            'realms' / \
            self.auth_config['realm'] / \
            'protocol/openid-connect'

        self.auth_url = base_url / 'auth' % {
            'client_id': self.auth_config['client_id'],
            'response_type': 'code'
        }

        self.token_url = base_url / 'token'

    def handle_request(self, environ) -> Optional[Response]:

        # handle session cookie
        cookies = BaseCookie(environ.get('HTTP_COOKIE', None))
        session_id = cookies['session'].value if 'session' in cookies else None
        if not session_id:
            while True:
                session_id = str(uuid4())
                if not self.cache.get('session/' + session_id):
                    break
        cache_key = 'session/' + session_id

        # build redirect url
        redirect_url = self.auth_config['redirect_url'] + (environ['PATH_INFO'] or '/')  # TODO include query params

        # handle incoming Keycloak redirect
        query = parse_qs(environ['QUERY_STRING'])
        if 'code' in query:

            token_response = requests.post(
                self.token_url,
                data={
                    'client_id': self.auth_config['client_id'],
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
            # set cookie and redirect to auth url
            location = self.auth_url % {'redirect_uri': redirect_url}
            return self._get_redirect_response(location, session_id)

        access_token = jwt.decode(access_token, verify=False)
        environ['roles'] = set(access_token['realm_access']['roles'])

        return None

    def _get_redirect_response(self, location: URL, session_id):
        return Response(
            '302 Found', [
                ('Set-Cookie', f'session={session_id}'),
                ('Location', str(location))
            ], iter([]))

