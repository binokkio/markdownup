from pathlib import Path
from typing import List, Optional, Dict, Set

from markdownup.filesystem.asset_file import AssetFile
from markdownup.filesystem.entry import Entry
from markdownup.filesystem.file import File
from markdownup.filesystem.markdown_file import MarkdownFile
from markdownup.response import ResponseException


class Directory(Entry):

    def __init__(self, context, path: Path = None, depth: int = 0):

        super().__init__(context, path, depth)

        self.index: Optional[MarkdownFile] = None
        self.directory_map: Dict[str, Directory] = {}
        self.file_map: Dict[str, MarkdownFile] = {}
        self.access_roles: Optional[Set[str]] = self._read_access_file()

        for index_filename in self.config.get('content', 'indices'):
            index_path = self.path / index_filename
            if index_path.is_file():
                self.index = MarkdownFile(context, index_path, depth)
                self.name = self.index.name
                self.request_path = self.index.request_path
                break

        for entry in self.path.iterdir():
            if self.index and self.index.path == entry:
                continue
            str_path = str('/' / entry.relative_to(context.root_path))
            exclusion = next((exclusion for exclusion in context.exclusions if exclusion.search(str_path)), None)
            if exclusion:
                print(f'Excluding {entry} due to configured exclusion pattern  {exclusion.pattern}')
                continue
            name = entry.name
            if entry.is_dir():
                self.directory_map[name] = Directory(context, entry, depth + 1)
            elif entry.is_file() and name.endswith('.md'):
                self.file_map[name] = MarkdownFile(context, entry, depth)

        # these are updated for every request
        self.children = ChrevronList()
        self.traversed = False  # keeps track of having been traversed during the most recent resolve call

    def _read_access_file(self) -> Optional[Set[str]]:
        access_file_name = self.config.get('access', 'filename')
        if access_file_name:
            access_file_path = self.path / access_file_name
            if access_file_path.is_file():
                return set(access_file_path.read_text('UTF-8').splitlines())
        return None

    def resolve(self, environ, path: Path) -> Optional[File]:
        str_path = str('/' / path)
        exclusion = next((exclusion for exclusion in self.context.exclusions if exclusion.search(str_path)), None)
        if exclusion:
            print(f'Not resolving {str_path} because it matched configured exclusion pattern {exclusion.pattern}')
            return None
        self._reset()
        return self._resolve(environ, list(path.parts))

    def _resolve(self, environ, parts: List[str]) -> Optional[File]:
        if not self.is_accessible(environ):
            return None
        self.traversed = True
        if len(parts) == 0 and self.request_path:
            raise ResponseException('302 Found', [('Location', self.request_path)])
        next_part = parts.pop(0)
        if self.index and next_part == self.index.path.name:
            return self.index
        if next_part in self.file_map:
            return self.file_map[next_part]
        elif next_part in self.directory_map:
            return self.directory_map[next_part]._resolve(environ, parts)
        else:
            asset_file_path = self.path / next_part
            if asset_file_path.is_file():
                return AssetFile(asset_file_path)
        return None

    def _reset(self):
        if self.traversed:
            for directory in self.directory_map.values():
                if directory.traversed:
                    directory._reset()
        self.traversed = False

    def apply_access(self, environ):

        def propagate(d: Directory):
            if d.is_accessible(environ):
                d.apply_access(environ)
                if d.index or d.children:
                    return d

        self.children = ChrevronList()
        self.children.extend(filter(propagate, self.directory_map.values()))
        self.children.extend(self.file_map.values())
        self.children.sort(key=lambda e: e.name)
        self.has_children = len(self.children) > 0

    def is_accessible(self, environ):
        if self.access_roles is None:
            return True  # no access rules defined, access allowed
        if 'authenticated' not in environ['auth']:
            return False  # access rules defined but user has no roles, access denied
        if self.access_roles & environ['auth']['authenticated']['roles']:  # TODO find first match is probably a faster
            return True  # overlap between access roles and user roles, access allowed
        else:
            return False  # no intersect between access roles and user roles, access denied

    def get_markdown_files(self, environ):
        if self.is_accessible(environ):
            self.apply_access(environ)
            yield from Directory._get_markdown_files(self)

    @staticmethod
    def _get_markdown_files(directory: 'Directory'):
        if directory.index:
            yield directory.index
        for child in directory.children:
            if isinstance(child, MarkdownFile):
                yield child
            if isinstance(child, Directory):
                yield from Directory._get_markdown_files(child)


class ChrevronList(list):
    _CHEVRON_return_scope_when_falsy = True
