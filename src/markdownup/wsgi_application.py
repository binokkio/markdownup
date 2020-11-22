from typing import Dict

from gunicorn.app.base import BaseApplication
from markdownup.markdownup import MarkdownUp


class WsgiApplication(BaseApplication):

    def __init__(self, config: Dict):
        self.config = config
        super().__init__()

    def init(self, parser, options, args):
        pass

    def load_config(self):
        for key, value in self.config['wsgi'].items():
            self.cfg.set(key, value)

    def load(self):
        return MarkdownUp(self.config).wsgi_app