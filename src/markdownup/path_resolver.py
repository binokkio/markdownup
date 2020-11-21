from pathlib import Path


def resolve_str(root: Path, offset: str):
    return resolve(root, Path(offset))


def resolve(root: Path, offset: Path):
    root = root.resolve()
    pointer = root
    for part in offset.parts:
        if part == '/':
            pointer = root
            continue
        pointer = pointer / part
        pointer = pointer.resolve()
        if root not in pointer.parents:
            raise ValueError('Following `offset` leads outside of `root`')
    return pointer
