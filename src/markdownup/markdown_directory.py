from pathlib import Path
from typing import List

from markdownup.markdown_file import MarkdownFile


class MarkdownDirectory:

    def __init__(self, config, path: Path = None, depth: int = 0):

        path = path or Path(config['content']['root']).resolve()

        self.config = config
        self.path = path
        self.name = path.name
        self.depth = depth
        self.directory_map = {}
        self.file_map = {}
        self.index = None
        self.directories = MustacheList()
        self.files = MustacheList()

        for entry in path.iterdir():
            if entry.name.startswith('.'):
                continue
            name = entry.name
            if entry.is_file() and name.endswith('.md'):
                if name in config['content']['indices'] and not self.index:
                    self.index = MarkdownFile(config, entry, depth, is_index=True)
                else:
                    markdown_file = MarkdownFile(config, entry, depth)
                    self.file_map[name] = markdown_file
                    self.files.append(markdown_file)
            elif entry.is_dir():
                sub_directory = MarkdownDirectory(config, entry, depth + 1)
                if sub_directory.directories or sub_directory.files or sub_directory.index:
                    self.directory_map[name] = sub_directory
                    self.directories.append(sub_directory)

        print(f'Processed {path}')

    def resolve(self, path: str):
        return self._resolve(list(Path(path).parts))

    def _resolve(self, parts: List[str]):
        if len(parts) == 0:
            return self.index
        next_part = parts.pop(0)
        if next_part in self.file_map:
            return self.file_map[next_part]
        elif next_part in self.directory_map:
            return self.directory_map[next_part]._resolve(parts)
        else:
            return None


class MustacheList(list):
    _CHEVRON_return_scope_when_falsy = True
