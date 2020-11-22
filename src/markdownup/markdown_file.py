import re
from pathlib import Path


class MarkdownFile:

    _title_pattern = re.compile(r'^#\s?(.*)', re.MULTILINE)

    def __init__(self, config, path: Path, depth: int, is_index: bool = False):

        self.config = config
        self.path = path
        self.name = path.name
        self.depth = depth
        self.title = self._get_title(path.read_text())
        self.request_path = '/' + '/'.join(path.parts[len(path.parts) - depth - 1:-1 if is_index else len(path.parts)])

    def read(self):
        return self.path.read_text()

    @staticmethod
    def _get_title(md: str) -> str:
        match = MarkdownFile._title_pattern.search(md)
        return match.group(1) if match else 'Untitled document'
