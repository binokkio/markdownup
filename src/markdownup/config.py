from pathlib import Path

import yaml

from markdownup.helpers import rget

default_config = {
    'theme': 'default',
    'wsgi': {
        'bind': '0.0.0.0:8080',
        'workers': 4
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
        'indices': [
            'README.md',
            'index.md'
        ],
        'gits': {}
    },
    'access': {
        'filename': '.upaccess'
    },
    'markdown': {
        'extensions': {
            'extra': {},
            'codehilite': {
                'guess_lang': False
            }
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
