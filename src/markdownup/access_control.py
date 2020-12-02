import re
from collections import OrderedDict
from pathlib import Path
from typing import Pattern


class AccessControl:

    def __init__(self, config):
        self.rules: OrderedDict[Pattern, any] = OrderedDict((
            (re.compile(pattern), audience)
            for pattern, audience in config['access'].items()))

    def is_access_allowed(self, path: Path):
        audience = self.get_audience(path)
        return audience

    def get_audience(self, path: Path):
        for pattern, audience in self.rules.items():
            if pattern.search(str(path)):
                return audience
        return False
