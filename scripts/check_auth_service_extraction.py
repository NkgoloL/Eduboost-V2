#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
AUTH = ROOT / "app/api_v2_routers/auth.py"
REPOSITORY_TOKENS = (
    "UserRepository",
    "GuardianRepository",
    "LearnerRepository",
    "ConsentRepository",
    "AuditRepository",
    "RefreshTokenRepository",
    "PasswordResetRepository",
)


def main() -> int:
    failures: list[str] = []
    print("Auth service extraction check")

    repair = subprocess.run(
        [sys.executable, "scripts/repair_auth_service_extraction.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(repair.stdout)
    if repair.returncode != 0:
        failures.append("repair_auth_service_extraction.py failed")

    source = AUTH.read_text(encoding="utf-8") if AUTH.exists() else ""
    try:
        ast.parse(source)
        print("- PASS auth.py syntax")
    except SyntaxError as exc:
        failures.append(f"auth.py syntax error: {exc}")

    if "from app.api_v2_deps.auth_service import" in source:
        print("- PASS auth router imports AuthApplicationService dependency")
    else:
        failures.append("auth router missing AuthApplicationService dependency import")

    if "from app.repositories" in source:
        failures.append("auth router still imports app.repositories")
        print("- FAIL auth router still imports app.repositories")
    else:
        print("- PASS auth router has no direct app.repositories import")

    for token in REPOSITORY_TOKENS:
        if f"{token}(" in source:
            failures.append(f"auth router still directly constructs {token}")
            print(f"- FAIL direct constructor remains: {token}")

    if "from __future__ import annotations" in source:
        failures.append("auth.py future annotations can reintroduce FastAPI forward-ref failures")
        print("- FAIL auth.py contains future annotations")
    else:
        print("- PASS auth.py has no future annotations")

    try:
        importlib.import_module("app.api_v2_routers.auth")
        print("- PASS app.api_v2_routers.auth imports")
    except Exception as exc:
        failures.append(f"auth router import failed: {exc!r}")

    try:
        api_v2 = importlib.import_module("app.api_v2")
        app = getattr(api_v2, "app")
        if len(getattr(app, "routes", [])) > 0:
            print("- PASS app.api_v2 imports and registers routes")
        else:
            failures.append("app.api_v2 has no routes")
    except Exception as exc:
        failures.append(f"app.api_v2 import failed: {exc!r}")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "app/api_v2_routers/auth.py",
            "app/services/auth_application_service.py",
            "app/api_v2_deps/auth_service.py",
            "--select",
            "F821,F401,F811,E402",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused ruff auth service extraction check")
    else:
        failures.append("focused ruff auth service extraction check failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS auth service extraction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
