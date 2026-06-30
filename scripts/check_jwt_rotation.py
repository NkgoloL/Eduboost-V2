#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / "app/core/security.py"


def main() -> int:
    failures: list[str] = []
    print("JWT rotation check")
    subprocess.run([sys.executable, "scripts/inspect_jwt_rotation.py"], cwd=ROOT, check=True)
    security_text = SECURITY.read_text(encoding="utf-8") if SECURITY.exists() else ""

    if (ROOT / "app/services/jwt_keyring.py").exists():
        print("- PASS jwt keyring helper exists")
    else:
        failures.append("missing keyring helper")
        print("- FAIL jwt keyring helper missing")

    if "app.services.jwt_keyring" in security_text:
        print("- PASS security.py imports jwt keyring helper")
    else:
        failures.append("security.py missing keyring import")
        print("- FAIL security.py missing keyring import")

    if "current_jwt_headers()" in security_text or (ROOT / "docs/security/jwt_rotation_repair_blockers.md").exists():
        print("- PASS kid header path present or explicit blocker exists")
    else:
        failures.append("no kid header path or blocker")
        print("- FAIL no kid header path or blocker")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS JWT rotation check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
