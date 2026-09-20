#!/usr/bin/env python3
"""Write sandbox (spec 3, 37): task writes must stay inside the
rc3-3-2-microvalidation directory. All construction scripts route
writes through this module."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK_DIR = HERE.parent


class WriteGuardError(PermissionError):
    pass


def check(path):
    p = Path(path).resolve()
    td = TASK_DIR.resolve()
    if p != td and td not in p.parents:
        raise WriteGuardError(f"write outside task sandbox: {p}")


def open_w(path, mode="w", **kw):
    if mode.startswith(("w", "a", "x")):
        check(path)
    return open(path, mode, **kw)


def write_text(path, text, encoding="utf-8"):
    check(path)
    Path(path).write_text(text, encoding=encoding)


def write_bytes(path, data):
    check(path)
    Path(path).write_bytes(data)
