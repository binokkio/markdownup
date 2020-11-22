import os
import sys
from pathlib import Path

import yaml
from markdownup.config import extend_default_config
from markdownup.wsgi_application import WsgiApplication


def _main():

    if len(sys.argv) == 1:
        print('Usage option 1: <path-to-markdown-root-directory>\n'
              'Usage option 2: <path-to-config-file>\n'
              'Usage option 3: --start-config <path-to-new-file (will be overwritten if exists)>')
        exit(1)

    if len(sys.argv) == 2:
        as_path = Path(sys.argv[1])
        if as_path.is_dir():
            config = extend_default_config({'content': {'root': sys.argv[1]}})
            WsgiApplication(config).run()
            exit(0)
        elif as_path.is_file():
            os.chdir(as_path.parent)
            config = yaml.load(as_path.read_text(), yaml.FullLoader)
            config = extend_default_config(config)
            WsgiApplication(config).run()
            exit(0)

    if len(sys.argv) == 3:
        if sys.argv[1] == '--start-config':
            config = extend_default_config({'content': {'root': ''}})
            config = yaml.dump(config)
            with open(sys.argv[2], 'w') as file:
                file.write(config)


if __name__ == '__main__':
    _main()
