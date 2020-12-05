from uuid import uuid4
from pathlib import Path
from typing import List, Optional

from markdownup.file.asset_file import AssetFile
from markdownup.file.file import File
from markdownup.file.markdown_file import MarkdownFile


class Directory:

    def __init__(self, context, path: Path = None, depth: int = 0):

        path = path or context.root_path

        self.context = context
        self.path = path
        self.name = path.name
        self.depth = depth
        self.uid = uuid4()
        self.directory_map = {}
        self.file_map = {}
        self.index = None
        self.directories: List[Directory] = MustacheList()
        self.files: List[MarkdownFile] = MustacheList()
        self.traversed = False  # keeps track of having been traversed during the most recent resolve call

        for entry in path.iterdir():
            abs_path = '/' / entry.relative_to(context.root_path)
            if context.global_access_control.get_audience(abs_path) is False:
                continue
            name = entry.name
            if entry.is_file() and name.endswith('.md'):
                if name in context.config.get('content', 'indices') and not self.index:
                    self.index = MarkdownFile(context, entry, depth, is_index=True)
                else:
                    markdown_file = MarkdownFile(context, entry, depth)
                    self.file_map[name] = markdown_file
                    self.files.append(markdown_file)
            elif entry.is_dir():
                sub_directory = Directory(context, entry, depth + 1)
                # TODO add to map but not list if no markdown inside
                if sub_directory.directories or sub_directory.files or sub_directory.index:
                    self.directory_map[name] = sub_directory
                    self.directories.append(sub_directory)

        self.directories.sort(key=lambda directory: directory.index.title if directory.index else directory.name)
        self.files.sort(key=lambda file: file.title)

        print(f'Processed {path}')

    def resolve(self, path: Path) -> Optional[File]:
        abs_path = '/' / path
        if self.context.global_access_control.get_audience(abs_path) is False:
            print(f'Access denied through global rules for {abs_path}')
            return None
        self._reset()
        return self._resolve(list(path.parts))

    def _resolve(self, parts: List[str]) -> Optional[File]:
        self.traversed = True
        if len(parts) == 0:
            return self.index
        next_part = parts.pop(0)
        if next_part in self.file_map:
            return self.file_map[next_part]
        elif next_part in self.directory_map:
            return self.directory_map[next_part]._resolve(parts)
        else:
            asset_file_path = self.path / next_part
            if asset_file_path.is_file():
                return AssetFile(asset_file_path)
            else:
                return None

    def _reset(self):
        if self.traversed:
            for directory in self.directories:
                if directory.traversed:
                    directory._reset()
        self.traversed = False


class MustacheList(list):
    _CHEVRON_return_scope_when_falsy = True
