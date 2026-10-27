"""Recognise a package that lives inside an installed game client.

Loose mode may overwrite a package in place, but a package inside the client
install directory is the one copy a player cannot regenerate. The editor asks
for an explicit confirmation there and stays silent elsewhere; this module is
the only place that decision is made, so it can be tested without Qt.
"""

from __future__ import annotations

from pathlib import Path

#: Files that exist in an installed client but would be pointless to fake in a
#: scratch directory. Both are measured facts of this client (see docs/STATUS).
CLIENT_MARKERS = ("mx.exe", "mxmain.dll")

#: ``data/script.fls`` is two levels below the install root; allow two ancestors.
MAX_PARENT_LEVELS = 2


def client_root_for(path: str | Path) -> Path | None:
    """Return the install directory holding ``path``, or ``None``.

    Only real files count: a directory named ``data`` next to a stray ``mx.exe``
    is still a client, but a *file* named ``mx.exe`` inside a package tree is
    not. Nothing is opened or executed; only ``is_file`` is consulted.
    """
    try:
        start = Path(path).resolve(strict=True).parent
    except (OSError, RuntimeError):
        return None
    candidates = [start]
    walker = start
    for _ in range(MAX_PARENT_LEVELS):
        if walker.parent == walker:
            break
        walker = walker.parent
        candidates.append(walker)
    for directory in candidates:
        try:
            if any((directory / marker).is_file() for marker in CLIENT_MARKERS):
                return directory
        except OSError:
            continue
    return None


def is_client_install(path: str | Path) -> bool:
    return client_root_for(path) is not None
