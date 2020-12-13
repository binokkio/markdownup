from pathlib import Path


class Theme:

    def __init__(self, config):
        self.path = self._resolve_path(config.get('theme'))
        self.html = {html.name[:-5]: html.read_text() for html in self.path.glob('*.html')}

    @staticmethod
    def _resolve_path(theme: str):
        path = Path(theme)
        if not path.is_dir():
            path = Path(__file__).parent / 'themes' / theme
            if not path.is_dir():
                raise ValueError(f'Theme "{theme}" not found')  # TODO improve feedback
        return path
