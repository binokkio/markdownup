from pathlib import Path
from typing import Optional, Dict

from markdownup.filesystem.asset_file import AssetFile


class Theme:

    def __init__(self, context):
        self._path = self._resolve_path(context.config.get('theme'))
        self.html: Dict[str, str] = {html.name[:-5]: html.read_text() for html in self._path.glob('*.html')}
        self.files: Dict[Path, AssetFile] = {}
        for path in self._path.glob("**/*"):
            if path.is_file():
                self.files[path.relative_to(self._path)] = AssetFile(context, path)

    def get_file(self, rel_path: Path) -> Optional[AssetFile]:
        return self.files.get(rel_path, None)

    @staticmethod
    def _resolve_path(theme: str):
        path = Path(theme)
        if not path.is_dir():
            path = Path(__file__).parent / 'themes' / theme
            if not path.is_dir():
                raise ValueError(f'Theme "{theme}" not found')  # TODO improve feedback
        return path
