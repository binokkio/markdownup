from base64 import b64decode
from typing import Optional
from urllib.parse import parse_qs, urlencode

from markdownup.auth.auth_provider import AuthProvider
from markdownup.markdownup import MarkdownUp
from markdownup.response import Response


class BasicAuth(AuthProvider):

    def __init__(self, context: MarkdownUp):
        self.config = context.config
        self.realm = self.config.get('access', 'auth', 'realm')
        self.users = {}

        for username, details in self.config.get('access', 'auth', 'users').items():
            self.users[username] = {
                'password': details['password'],
                'roles': set(details['roles'])
            }

    def handle_request(self, environ) -> Optional[Response]:

        authorization = environ.get('HTTP_AUTHORIZATION', None)

        if authorization:

            authorization = authorization[6:]  # drop the "Basic " prefix
            authorization = b64decode(authorization)
            authorization = authorization.decode('UTF-8')
            user, password = authorization.split(':', 1)
            if user in self.users and self.users[user]['password'] == password:
                environ['auth']['authenticated'] = {
                    'display_name': user,
                    'roles': self.users[user]['roles']
                }

        query = parse_qs(environ['QUERY_STRING'])

        login_response = self.logx('login', environ, query)
        if login_response:
            return login_response

        logout_response = self.logx('logout', environ, query)
        if logout_response:
            return logout_response

        return None

    def logx(self, x: str, environ, query):

        if x in query:

            # step one, add current path to query as redirect path and redirect to /
            # this ensures the browser associates the auth credentials with the whole site
            if 'redirect_path' not in query:
                return Response(
                    '303 See Other',
                    [('Location', '/?' + urlencode({
                        x: 'yes',
                        'redirect_path': environ['PATH_INFO'] or '/'
                    }))]
                )

            # step two, as long as the presence of the authorization header does not match
            # the state described by `x` we respond with 401 Unauthorized
            if ('authenticated' not in environ['auth']) == (x == 'login'):
                return Response(
                    '401 Unauthorized',
                    [('WWW-Authenticate', f'Basic realm="{self.realm}"')]
                )

            # step three, redirect back to the redirect_path from step one
            return Response(
                '303 See Other',
                [('Location', query['redirect_path'][0])]
            )

        return None
