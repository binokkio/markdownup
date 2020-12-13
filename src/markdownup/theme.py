from pathlib import Path


class Theme:

    def __init__(self, config):
        self.path = self._resolve_path(config.get('main', 'theme'))
        self.document = self._read_document()
        self.search_results = self._read_search_results()
        self.error_404 = self._read_404()
        self.partials = self._read_partials()

    @staticmethod
    def _resolve_path(theme: str):
        path = Path(theme)
        if not path.is_dir():
            path = Path(__file__).parent / 'themes' / theme
            if not path.is_dir():
                raise ValueError(f'Theme "{theme}" not found')  # TODO improve feedback
        return path

    def _read_document(self):
        path = self.path / 'document.html'
        if not path.is_file():
            raise ValueError('Theme does not contain a file named "document.html"')
        return path.read_text()

    def _read_search_results(self):
        path = self.path / 'search-results.html'
        if not path.is_file():
            raise ValueError('Theme does not contain a file named "search-results.html"')
        return path.read_text()

    def _read_404(self):
        path = self.path / '404.html'
        if not path.is_file():
            return None
        return path.read_text()

    def _read_partials(self):
        result = {}
        for partial in self.path.glob('*.html'):
            if partial.name != 'document.html':
                result[partial.name[:-5]] = partial.read_text()
        return result
