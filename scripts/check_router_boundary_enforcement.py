#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/architecture/router_repository_boundary_matrix.json"
P0_FAIL_ROUTERS = {"app/api_v2_routers/popia.py", "app/api_v2_routers/lessons.py"}


def main() -> int:
    print("Router boundary enforcement check")
    subprocess.run([sys.executable, "scripts/generate_router_boundary_matrix.py"], cwd=ROOT, check=True)

    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    failures = []
    for row in data["rows"]:
        router = row["router"]
        violations = row["violations"]
        if router in P0_FAIL_ROUTERS and violations:
            failures.append(f"{router}: {violations}")
            print(f"- FAIL {router}: direct repository imports {violations}")
        elif router in P0_FAIL_ROUTERS:
            print(f"- PASS {router}: no direct repository imports")
        elif violations:
            print(f"- INFO {router}: remaining boundary debt {violations}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS repaired P0 router repository boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
