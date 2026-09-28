"""safe_io — atomic writes for data/catalog tools (temp then os.replace). stdlib only."""
from __future__ import annotations

import os
import tempfile


def safe_write(path: str, content: str, encoding: str = "utf-8") -> str:
    """Write content to path atomically (mkstemp + os.replace). Returns path."""
    if not path:
        raise ValueError("path required")
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    fd, _tmp = tempfile.mkstemp(dir=parent, prefix=".cat-", suffix=".tmp")
    os.close(fd)
    try:
        with open(_tmp, "w", encoding=encoding) as fh:
            fh.write(content)
        os.replace(_tmp, path)
    except Exception:
        if os.path.exists(_tmp):
            os.unlink(_tmp)
        raise
    return path
