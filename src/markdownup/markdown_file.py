import re
import subprocess
from pathlib import Path


class MarkdownFile:

    _title_pattern = re.compile(r'^#\s?(.*)', re.MULTILINE)

    def __init__(self, config, path: Path, depth: int, is_index: bool = False):

        self.config = config
        self.path = path
        self.name = path.name
        self.depth = depth
        self.title = self._get_title(path.read_text()) or self.name
        self.request_path = '/' + '/'.join(path.parts[len(path.parts) - depth - 1:-1 if is_index else len(path.parts)])
        self.version = self._get_version_details()

        print(f'Processed {path}')

    def read(self):
        return self.path.read_text()

    @staticmethod
    def _get_title(md: str) -> str:
        match = MarkdownFile._title_pattern.search(md)
        return match.group(1) if match else None

    def _get_version_details(self):

        # define the cwd and arg for the git call assuming .git is not external
        cwd = self.path.parent
        arg = self.name

        # update cwd and arg if we match a configured external .git
        root = Path(self.config['content']['root']).resolve()  # TODO reuse the one from MarkdownUp
        relative = self.path.relative_to(root)
        for root_path, git_path in self.config['content']['gits'].items():
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
