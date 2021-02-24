import os
import re
import subprocess
from pathlib import Path

import chevron
import markdown
from markdownup.filesystem.entry import Entry
from markdownup.filesystem.file import File
from markdownup.response import Response


class MarkdownFile(Entry, File):

    _title_pattern = re.compile(r'^#\s?(.*)', re.MULTILINE)
    _search_term_pattern = re.compile(r'\w{2,}')

    def __init__(self, context, path: Path, depth: int):

        super().__init__(context, path, depth)

        self.name = self._get_title(path.read_text()) or self.name
        self.request_path = '/' + '/'.join(path.parts[len(path.parts) - depth - 1:])
        self.version = self._get_version_details()
        self.search_index = self._get_search_index()
        self.cache_mode = self.config.get('markdown', 'cache')
        self.cache_value = None

        if self.cache_mode == 'shared':
            context.cache.put(self.request_path, self._get_content().encode('UTF-8'))
        elif self.cache_mode == 'worker':
            self.cache_value = self._get_content()
        elif self.cache_mode is not False:
            raise ValueError(f'Unsupported value for markdown.cache: {self.cache_mode}')

    def get_response(self, environ):

        if self.cache_mode == 'shared':
            content = self.context.cache.get(self.request_path).decode('UTF-8')
        elif self.cache_mode == 'worker':
            content = self.cache_value
        else:
            content = self._get_content()

        self.context.root.apply_access(environ)

        html = chevron.render(
            template=self.context.theme.html['document'],
            partials_dict=self.context.theme.html,
            data={
                'title': self.name,
                'file': self,
                'content': content,
                'root': self.context.root,
                'auth': environ.get('auth', None),
                'config': self.context.config.get('render')
            }
        )

        return Response(
            '200 OK',
            [('Content-Type', 'text/html')],
            (bytes(b, 'UTF-8') for b in html.splitlines(keepends=True))
        )

    def _get_content(self):
        # relying on the fact that no process handles multiple requests at the same time, we can safely do this
        return_dir = os.getcwd()
        try:
            os.chdir(self.path.parent)
            return markdown.markdown(
                self.path.read_text(),
                extensions=self.config.get('markdown', 'extensions').keys(),
                extension_configs=self.config.get('markdown', 'extensions')
            )
        finally:
            os.chdir(return_dir)

    @staticmethod
    def _get_title(md: str) -> str:
        match = MarkdownFile._title_pattern.search(md)
        return match.group(1) if match else None

    def _get_version_details(self):

        # define the cwd and arg for the git call assuming .git is not external
        cwd = self.path.parent
        arg = self.path.name

        # update cwd and arg if we match a configured external .git
        root = self.context.root_path
        relative = self.path.relative_to(root)
        for root_path, git_path in self.config.get('content', 'gits').items():
            try:
                possible_arg = relative.relative_to(root_path)
                cwd = git_path
                arg = possible_arg
                break
            except ValueError:
                pass

        result = subprocess.run(
            ['git', 'log', '-1', '--format=%an%n%ae%n%cI%n%h%n%H', '--', arg],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            lines = result.stdout.decode('UTF-8').splitlines()
            if lines:
                return {
                    'author': {
                        'name': lines[0],
                        'email': lines[1]
                    },
                    'date': lines[2],
                    'short_hash': lines[3],
                    'hash': lines[4]
                }
            return lines
        else:
            return None

    def _get_search_index(self):
        search_index = {}
        haystack = self.path.read_text()
        index = 0
        for needle in self._search_term_pattern.finditer(haystack):
            index += 1
            search_term = needle.group(0).lower()
            if search_term not in search_index:
                search_index[search_term] = index
        return search_index
