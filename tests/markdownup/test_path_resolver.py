from pathlib import Path

import pytest
from markdownup.path_resolver import resolve


def test_resolve_relative():
    root = Path('/dev')
    offset = Path('null')
    result = resolve(root, offset)
    assert result == Path('/dev/null')


def test_resolve_absolute():
    root = Path('/dev')
    offset = Path('/null')
    result = resolve(root, offset)
    assert result == Path('/dev/null')


def test_resolve_dot_dot():
    root = Path('/tmp')
    offset = Path('../etc/passwd')
    with pytest.raises(ValueError):
        resolve(root, offset)


def test_resolve_dot_dot_return():
    # even though the result would be inside `root` allowing this would
    # allow the discovery of directory names outside of `root`
    root = Path('/home/user')
    offset = Path('../user/index.md')
    with pytest.raises(ValueError):
        resolve(root, offset)
