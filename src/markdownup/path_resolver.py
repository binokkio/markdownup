from pathlib import Path
from typing import Optional


def resolve_str(root: Path, offset: str) -> Optional[Path]:
    return resolve(root, Path(offset))


def resolve(root: Path, offset: Path) -> Optional[Path]:
    root = root.resolve()
    pointer = root
    for part in offset.parts:
        if part == '/':
            pointer = root
            continue
        if part.startswith('.') and not part.startswith('..'):
            raise ValueError('Part of `offset` is a hidden file or directory')
        pointer = pointer / part
        pointer = pointer.resolve()
        if root not in pointer.parents:
            raise ValueError('Following `offset` leads outside of `root`')
    if pointer.exists():
        return pointer
