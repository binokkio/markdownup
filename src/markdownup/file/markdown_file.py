import os
import re
import subprocess
from pathlib import Path

import chevron
import markdown
from markdownup.file.file import File
from markdownup.response import Response


class MarkdownFile(File):

    _title_pattern = re.compile(r'^#\s?(.*)', re.MULTILINE)

    def __init__(self, context, path: Path, depth: int, is_index: bool = False):

        self.context = context
        self.config = context.config
        self.path = path
        self.name = path.name
        self.depth = depth
        self.title = self._get_title(path.read_text()) or self.name
        self.request_path = '/' + '/'.join(path.parts[len(path.parts) - depth - 1:-1 if is_index else len(path.parts)])
        self.version = self._get_version_details()

        print(f'Processed {path}')

    def get_response(self):

        # relying on the fact that no process handles multiple requests at the same time, we can safely change wd
        os.chdir(self.path.parent)

        html = chevron.render(
            template=self.context.theme.frame,
            partials_path=str(self.context.theme.path),
            partials_ext='html',
            data={
                'title': self.title,
                'file': self,
                'content': markdown.markdown(
                    self.path.read_text(),
                    extensions=self.config.get('markdown', 'extensions').keys(),
                    extension_configs=self.config.get('markdown', 'extensions')
                ),
                'root': self.context.root
            }
        )

        return Response(
            '200 OK',
            [('Content-Type', 'text/html')],
            (bytes(b, 'UTF-8') for b in html.splitlines(keepends=True))
        )

    @staticmethod
    def _get_title(md: str) -> str:
        match = MarkdownFile._title_pattern.search(md)
        return match.group(1) if match else None

    def _get_version_details(self):

        # define the cwd and arg for the git call assuming .git is not external
        cwd = self.path.parent
        arg = self.name

        # update cwd and arg if we match a configured external .git
        root = Path(self.config.get('content', 'root')).resolve()  # TODO reuse the one from MarkdownUp
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