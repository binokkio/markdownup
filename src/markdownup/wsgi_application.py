from gunicorn.app.base import BaseApplication

from markdownup.markdownup import MarkdownUp


class WsgiApplication(BaseApplication):

    def __init__(self, markdownup: MarkdownUp):
        self.markdownup = markdownup
        super().__init__()

    def init(self, parser, options, args):
        pass

    def load_config(self):
        for key, value in self.markdownup.config.get('wsgi').items():
            self.cfg.set(key, value)

    def load(self):
        return self.markdownup.wsgi_app
