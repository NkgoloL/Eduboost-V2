#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "app/api_v2_routers/auth.py"
SERVICE = ROOT / "app/services/auth_application_service.py"


def main() -> int:
    failures: list[str] = []
    print("Auth lifecycle method extraction check")

    source = AUTH.read_text(encoding="utf-8")
    service_source = SERVICE.read_text(encoding="utf-8")

    if "from __future__ import annotations" in source:
        failures.append("auth.py still has future annotations")
    else:
        print("- PASS no future annotations in auth.py")

    if "from app.repositories" in source:
        failures.append("auth.py imports app.repositories")
    else:
        print("- PASS no direct app.repositories import in auth.py")

    for constructor in ("UserRepository(", "GuardianRepository(", "LearnerRepository(", "ConsentRepository("):
        if constructor in source:
            failures.append(f"direct constructor remains: {constructor}")
        else:
            print(f"- PASS {constructor} absent")

    for method in ("register", "login", "refresh"):
        if f"auth_service.{method}(" in source:
            print(f"- PASS route delegates {method}")
        else:
            failures.append(f"auth_service.{method} missing")

    for helper in ("_auth_lifecycle_legacy_register_impl", "_auth_lifecycle_legacy_login_impl", "_auth_lifecycle_legacy_refresh_impl"):
        if helper in source:
            print(f"- PASS preserved helper {helper}")
        else:
            failures.append(f"missing preserved helper {helper}")

    for marker in ("AuthApplicationService.register", "AuthApplicationService.login", "AuthApplicationService.refresh"):
        if marker in service_source:
            print(f"- PASS service marker {marker}")
        else:
            failures.append(f"missing service marker {marker}")

    try:
        auth_module = importlib.import_module("app.api_v2_routers.auth")
        print("- PASS app.api_v2_routers.auth imports")
        if hasattr(auth_module, "RegisterRequest"):
            print("- PASS RegisterRequest available in auth globals")
        else:
            failures.append("RegisterRequest missing in auth globals")
    except Exception as exc:
        failures.append(f"auth import failed: {exc!r}")

    try:
        api_v2 = importlib.import_module("app.api_v2")
        app = getattr(api_v2, "app")
        print(f"- PASS app.api_v2 imports with {len(getattr(app, 'routes', []))} routes")
    except Exception as exc:
        failures.append(f"app.api_v2 import failed: {exc!r}")

    for path in (AUTH, SERVICE):
        ast.parse(path.read_text(encoding="utf-8"))

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
        print("- PASS focused auth lifecycle ruff check")
    else:
        failures.append("focused ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS auth lifecycle method extraction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
