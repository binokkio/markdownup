from pathlib import Path

import yaml

from markdownup.helpers import rget

default_config = {
    'main': {
        'theme': 'default'
    },
    'wsgi': {
        'bind': '127.0.0.1:8080',
        'workers': 1
    },
    'cache': {
        'type': 'builtin',
        'bind': '127.0.0.1:8081'
    },
    'content': {
        'root': '.',
        'exclusions': [
            r'.*/\.'  # exclude hidden files and directories by default
        ],
        'accessFilename': '.upaccess',
        'indices': [
            'README.md',
            'index.md'
        ],
        'gits': {}
    },
    'markdown': {
        'extensions': {
            'extra': {},
            'codehilite': {}
        }
    }
}


class Config:

    @classmethod
    def from_dict(cls, dictionary):
        return cls(dictionary)

    @classmethod
    def from_file(cls, file: Path):
        return cls(yaml.load(file.read_text(), yaml.FullLoader))

    def __init__(self, custom_config):
        self.config = custom_config

    def get(self, *args):
        try:
            return rget(self.config or default_config, *args)
        except KeyError:
            try:
                return rget(default_config, *args)
            except KeyError:
                return None
