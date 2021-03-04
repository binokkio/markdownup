import os
import re
from pathlib import Path

import chevron
import markdown

from markdownup.filesystem.file import File
from markdownup.response import Response


class MarkdownFile(File):

    _title_pattern = re.compile(r'^#\s?(.*)', re.MULTILINE)
    _search_term_pattern = re.compile(r'\w{2,}')

    def __init__(self, context, path: Path):

        super().__init__(context, path)

        self.name = self._get_title(path.read_text()) or self.name
        self.request_path = f'/{path.relative_to(self.context.root_path)}'
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
        ).encode('UTF-8')

        return Response(
            '200 OK',
            [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', str(len(html)))
            ],
            [html]
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
