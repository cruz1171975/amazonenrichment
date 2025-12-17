from __future__ import annotations

import os
from pathlib import Path


def load_env_files(
    *,
    filenames: list[str] | None = None,
    overwrite: bool = False,
) -> list[Path]:
    """
    Load KEY=VALUE lines from local env files into os.environ.

    - Does not print values.
    - Ignores blank lines and comments.
    - Does not strip quotes beyond removing a single pair of matching ' or " around the value.
    """
    filenames = filenames or [".env", ".env.local", ".emv.local"]
    loaded: list[Path] = []
    for name in filenames:
        path = Path(name)
        if not path.exists() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            key, value = s.split("=", 1)
            key = key.strip()
            if not key:
                continue
            value = value.strip()
            if len(value) >= 2 and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")):
                value = value[1:-1]
            if not overwrite and key in os.environ:
                continue
            os.environ[key] = value
        loaded.append(path)
    return loaded

