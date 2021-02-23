import os
import shutil
import signal
import sys
from multiprocessing.context import Process
from pathlib import Path

import yaml

from markdownup.cache.builtin.server import BuiltinCacheServer
from markdownup.config import Config, default_config
from markdownup.markdownup import MarkdownUp
from markdownup.wsgi_application import WsgiApplication


def _main():

    if len(sys.argv) == 2:

        # initialize config based on argv
        config = None
        as_path = Path(sys.argv[1])
        if as_path.is_dir():
            config = Config.from_dict({'content': {'root': sys.argv[1]}})
        elif as_path.is_file():
            config = Config.from_file(as_path)
            os.chdir(as_path.parent)  # pretend to run from the config's parent dir
        else:
            print(f'No such file or directory: {as_path}')
            exit(1)

        # launch a new process for the built in cache server if configured
        if config.get('cache', 'type') == 'builtin':
            Process(daemon=True, target=BuiltinCacheServer(config).serve_forever).start()

        # TODO if configured process and cache all markdown files

        # launch the main MarkdownUp WSGI application
        markdownup = MarkdownUp(config)
        Process(target=WsgiApplication(markdownup).run).start()
        signal.pause()  # sleep indefinitely, makes for a cleaner ctrl+c termination

        # if the above returns we exit normally
        exit(0)

    if len(sys.argv) > 2:
        if sys.argv[1] == '--start-config':
            config = yaml.dump(default_config)
            target_file = Path(sys.argv[2])
            if target_file.exists():
                print('Target file exists, not doing anything')
                exit(2)
            target_file.write_text(config)
            exit(0)
        elif sys.argv[1] == '--start-theme':
            target_dir = Path(sys.argv[2])
            if target_dir.exists():
                print('Target dir exists, not doing anything')
                exit(3)
            theme_name = 'default' if len(sys.argv) == 3 else sys.argv[3]
            theme_dir = Path(__file__).parent / 'themes' / theme_name
            if not theme_dir.exists():
                theme_names = ', '.join(theme.name for theme in theme_dir.parent.iterdir() if theme.is_dir())
                print(f'No such theme "{theme_name}", themes: {theme_names}')
                exit(4)
            shutil.copytree(theme_dir, target_dir)
            exit(0)

    print('Usage option 1: <path-to-markdown-root-directory>\n'
          'Usage option 2: <path-to-config-file>\n'
          'Usage option 3: --start-config <path-to-new-file>\n'
          'Usage option 4: --start-theme <path-to-new-theme> [<seed-theme>]')
    exit(5)


if __name__ == '__main__':
    _main()
