"""Shared pytest configuration for repository-local imports.

Pytest can be invoked from CI, IDEs, or local shells in modes where the
repository root is not automatically placed on ``sys.path``. The application
package lives at ``app/``, so test collection must make the repository root
importable before integration, POPIA, smoke, and unit modules import app code.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def ensure_repo_root_on_path() -> None:
    """Ensure repository-local packages are importable during pytest collection."""
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


ensure_repo_root_on_path()
