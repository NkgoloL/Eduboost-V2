#!/usr/bin/env python3
from __future__ import annotations

from scripts.prod_frontend_runtime import repair


def main() -> int:
    status = repair()
    print(status.status)
    if status.blockers:
        for blocker in status.blockers:
            print(f"- {blocker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
