from pathlib import Path


class Theme:

    def __init__(self, config):
        self.path = self._resolve_path(config['main']['theme'])
        self.frame = self._read_frame()
        self.partials = self._read_partials()

    @staticmethod
    def _resolve_path(theme: str):
        path = Path(theme)
        if not path.is_dir():
            path = Path(__file__).parent / 'themes' / theme
            if not path.is_dir():
                raise ValueError(f'Theme "{theme}" not found')  # TODO improve feedback
        return path

    def _read_frame(self):
        path = self.path / 'frame.html'
        if not path.is_file():
            raise ValueError('Theme does not contain a file named "frame.html"')
        return path.read_text()

    def _read_partials(self):
        result = {}
        for partial in self.path.glob('*_partial.html'):
            result[partial.name[:-10]] = partial.read_text()
        return result
