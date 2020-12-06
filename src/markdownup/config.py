from pathlib import Path
from typing import List

import yaml

default_config = {
    'main': {
        'theme': 'default'
    },
    'wsgi': {
        'bind': '127.0.0.1:8080',
        'workers': 1
    },
    'content': {
        'root': '.',
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
    },
    'access': {
        'fileName': '.upaccess',
        'global': {
            r'.*/\.': False,  # nobody has access to hidden files and directories
            r'.*': True  # everybody has access to everything else
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
            return self._get_from(self.config or default_config, list(args))
        except KeyError:
            try:
                return self._get_from(default_config, list(args))
            except KeyError:
                return None

    def _get_from(self, pointer, args: List[str]):
        pointer = pointer[args.pop(0)]
        if len(args):
            return self._get_from(pointer, args)
        else:
            return pointer
