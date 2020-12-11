from typing import List


def rget(d: dict, *keys):
    return _rget(d, list(keys))


def _rget(d: dict, keys: List[str]):
    d = d[keys.pop(0)]
    if len(keys):
        return _rget(d, keys)
    else:
        return d
