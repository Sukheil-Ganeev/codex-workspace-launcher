"""Project discovery: register folders from CODEX_WORKSPACE_ROOTS.

CODEX_WORKSPACE_ROOTS is a platform-separated list of parent directories.
Every existing subdirectory of a root is registered as a project (unless it
is already registered under that exact path). No personal paths are baked
into the code — everything comes from the user's environment.
"""

from __future__ import annotations

import os
from pathlib import Path

from .registry import Registry, label_for_path


def discover(registry: Registry) -> int:
    """Seed missing projects from the environment. Returns how many added."""
    roots = os.environ.get("CODEX_WORKSPACE_ROOTS", "")
    added = 0
    for root in roots.split(os.pathsep):
        root = root.strip()
        if not root:
            continue
        base = Path(root).expanduser()
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            if registry.get_by_path(child) is None:
                registry.upsert(child, label_for_path(child))
                added += 1
    return added
