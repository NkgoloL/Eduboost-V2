#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    args = sys.argv[1:]
    if "--root" in args:
        idx = args.index("--root")
        if idx + 1 < len(args):
            root = Path(args[idx + 1]).resolve()
    command = [
        sys.executable,
        str(root / "scripts/maintenance/check_doc_stage3_strict_scope.py"),
        "--root",
        str(root),
        "--scope",
        "docs/documentation/stage_6_strict_scope.json",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())

