import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from markdownup.filesystem.entry import Entry
from markdownup.response import Response


class File(Entry, ABC):

    def __init__(self, context, path: Path = None):
        super().__init__(context, path)
        self.version = self._get_version_details()

    @abstractmethod
    def get_response(self, environ) -> Response:
        raise NotImplemented

    def _get_version_details(self):

        if not self.path.is_relative_to(self.context.root_path):
            return None

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
                    'timestamp': lines[2],
                    'short_hash': lines[3],
                    'hash': lines[4]
                }

        return None
