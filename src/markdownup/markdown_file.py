import re
from pathlib import Path


class MarkdownFile:

    _title_pattern = re.compile(r'^#\s?(.*)', re.MULTILINE)

    def __init__(self, path: Path, depth: int):
        self.path = path
        self.name = path.name
        self.title = self.get_title(path.read_text())
        self.request_path = '/' + '/'.join(path.parts[len(path.parts) - depth - 1:])
        self.index_request_path = '/' + '/'.join(path.parts[len(path.parts) - depth - 1:-1])

    @staticmethod
    def get_title(md: str):
        match = MarkdownFile._title_pattern.search(md)
        return match.group(1) if match else None
