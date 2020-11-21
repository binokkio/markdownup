import mimetypes
from pathlib import Path
from typing import List

from markdownup.markdown_file import MarkdownFile


class MarkdownDirectory:

    def __init__(self, config, path: Path, depth: int = 0):

        self.config = config
        self.path = path
        self.depth = depth
        self.directory_map = {}
        self.file_map = {}
        self.index_file = None
        self.name = path.name
        self.directories = []
        self.files = []

        # index
        for entry in path.iterdir():
            name = entry.name
            if entry.is_file() and mimetypes.guess_type(name)[0] == 'text/markdown':
                markdown_file = MarkdownFile(entry, depth)
                if name in config['content']['indices'] and not self.index_file:
                    self.index_file = markdown_file
                else:
                    self.file_map[name] = markdown_file
                    self.files.append(markdown_file)
            elif entry.is_dir():
                sub_directory = MarkdownDirectory(config, entry, depth + 1)
                if sub_directory.directories or sub_directory.files or sub_directory.index_file:
                    self.directory_map[name] = sub_directory
                    self.directories.append(sub_directory)

    def resolve(self, path: str):
        return self._resolve(list(Path(path).parts))

    def _resolve(self, parts: List[str]):
        if len(parts) == 0:
            return self.index_file
        next_part = parts.pop(0)
        if next_part in self.file_map:
            return self.file_map[next_part]
        elif next_part in self.directory_map:
            return self.directory_map[next_part]._resolve(parts)
        else:
            return None