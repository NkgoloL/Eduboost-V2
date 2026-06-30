#!/usr/bin/env python3
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures: list[str] = []
    print("Auth forward-reference import check")

    repair = subprocess.run(
        [sys.executable, "scripts/repair_auth_forward_refs.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(repair.stdout)
    if repair.returncode != 0:
        failures.append("repair_auth_forward_refs.py failed")

    try:
        auth = importlib.import_module("app.api_v2_routers.auth")
        print("- PASS imported app.api_v2_routers.auth")
        if hasattr(auth, "RegisterRequest"):
            print("- PASS auth.RegisterRequest is present")
        else:
            failures.append("auth.RegisterRequest missing")
            print("- FAIL auth.RegisterRequest missing")
    except Exception as exc:
        failures.append(f"auth router import failed: {exc!r}")
        print(f"- FAIL auth router import failed: {exc!r}")

    try:
        api_v2 = importlib.import_module("app.api_v2")
        app = getattr(api_v2, "app")
        route_paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
        if any("/register" in path for path in route_paths):
            print("- PASS app.api_v2 imports and register route is present")
        else:
            failures.append("register route missing after app import")
            print("- FAIL register route missing after app import")
    except Exception as exc:
        failures.append(f"app.api_v2 import failed: {exc!r}")
        print(f"- FAIL app.api_v2 import failed: {exc!r}")

    report = ROOT / "docs/release/auth_forward_ref_repair_report.md"
    if report.exists():
        print("- PASS repair report exists")
    else:
        failures.append("repair report missing")
        print("- FAIL repair report missing")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS auth forward-reference import check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
