"""Marker script for PRD-2.0-2.3 runtime KG persistence foundation.

The distributable bundle uses a shell wrapper to copy files into a repository.
This module remains in-tree so PRD verifiers and CI can compile the PRD-2 apply
entrypoint consistently with earlier production-readiness slices.
"""
from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path.cwd()
    required = root / "app/services/runtime_kg/service.py"
    if not required.exists():
        raise SystemExit("PRD-2 runtime KG files are not present; apply the bundle first")
    print("PRD-2.0-2.3 runtime KG persistence foundation files are present")


if __name__ == "__main__":
    main()
