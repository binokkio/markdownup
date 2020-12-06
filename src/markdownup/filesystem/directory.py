from pathlib import Path
from typing import List, Optional, Dict, Set

from markdownup.filesystem.asset_file import AssetFile
from markdownup.filesystem.entry import Entry
from markdownup.filesystem.file import File
from markdownup.filesystem.markdown_file import MarkdownFile


class Directory(Entry):

    def __init__(self, context, path: Path = None, depth: int = 0):

        super().__init__(context, path, depth)

        self.index: Optional[MarkdownFile] = None
        self.directory_map: Dict[str, Directory] = {}
        self.file_map: Dict[str, MarkdownFile] = {}
        self.access_roles: Optional[Set[str]] = self.read_access_file()

        for entry in self.path.iterdir():
            abs_path = '/' / entry.relative_to(context.root_path)
            if context.global_access_control.get_audience(abs_path) is False:
                continue
            name = entry.name
            if entry.is_file() and name.endswith('.md'):
                if not self.index and name in context.config.get('content', 'indices'):
                    self.index = MarkdownFile(context, entry, depth, is_index=True)
                    self.name = self.index.name
                    self.request_path = self.index.request_path
                else:
                    self.file_map[name] = MarkdownFile(context, entry, depth)
            elif entry.is_dir():
                sub_directory = Directory(context, entry, depth + 1)
                if sub_directory.directory_map or sub_directory.file_map or sub_directory.index:
                    self.directory_map[name] = sub_directory

        # these are updated for every request
        self.children = ChrevronList()
        self.traversed = False  # keeps track of having been traversed during the most recent resolve call

    def read_access_file(self) -> Optional[Set[str]]:
        access_file_path = self.path / self.config.get('access', 'fileName')
        if access_file_path.is_file():
            return set(access_file_path.read_text('UTF-8').splitlines())
        return None

    def resolve(self, environ, path: Path) -> Optional[File]:
        abs_path = '/' / path
        if self.context.global_access_control.get_audience(abs_path) is False:
            print(f'Access denied through global rules for {abs_path}')
            return None
        self._reset()
        return self._resolve(environ, list(path.parts))

    def _resolve(self, environ, parts: List[str]) -> Optional[File]:
        if not self.is_accessible(environ):
            return None
        self.traversed = True
        if len(parts) == 0:
            return self.index
        next_part = parts.pop(0)
        if next_part in self.file_map:
            return self.file_map[next_part]
        elif next_part in self.directory_map:
            return self.directory_map[next_part]._resolve(environ, parts)
        else:
            asset_file_path = self.path / next_part
            if asset_file_path.is_file():
                return AssetFile(asset_file_path)
            else:
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
        if not self.access_roles:
            return True  # no access rules defined, access allowed
        if 'roles' not in environ:
            return False  # access rules defined but user has no roles, access denied
        if self.access_roles & environ['roles']:
            return True  # overlap between access roles and user roles, access allowed
        else:
            return False  # no intersect between access roles and user roles, access denied


class ChrevronList(list):
    _CHEVRON_return_scope_when_falsy = True
