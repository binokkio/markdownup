import sys
from pathlib import Path
from typing import Dict

import gunicorn.app.base
from markdownup.config import extend_default_config
from markdownup.markdownup import MarkdownUp


class WsgiApplication(gunicorn.app.base.BaseApplication):

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


def _main():

    if len(sys.argv) == 1:
        print('\nUsage option 1: <path-to-markdown-root-directory> [-b <bind>]'
              'Future option 2: <path-to-markdownup-config-file>'
              'Future option 3: --create-config-file <path-for-new-config-file>')
        exit(1)

    if len(sys.argv) == 2:
        as_path = Path(sys.argv[1])
        if as_path.is_dir():
            config = extend_default_config({'content': {'root': sys.argv[1]}})
            WsgiApplication(config).run()


if __name__ == '__main__':
    _main()
