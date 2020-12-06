from pathlib import Path
from uuid import uuid4

from markdownup.config import Config


class Entry:

    def __init__(self, context, path: Path = None, depth: int = 0):

        path = path or context.root_path

        print(f'Processing {path}')

        self.context = context
        self.config: Config = context.config
        self.path: Path = path
        self.depth = depth
        self.uid = uuid4()
        self.name = path.name
        self.request_path = None
        self.has_children = False
