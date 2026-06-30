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
IMPL = ROOT / "app/services/auth_lifecycle_impl.py"


def main() -> int:
    failures: list[str] = []
    print("Auth service ownership check")

    for path in (AUTH, SERVICE, IMPL):
        if not path.exists():
            failures.append(f"missing {path.relative_to(ROOT)}")
            continue
        ast.parse(path.read_text(encoding="utf-8"))
        print(f"- PASS syntax {path.relative_to(ROOT)}")

    auth_text = AUTH.read_text(encoding="utf-8") if AUTH.exists() else ""
    service_text = SERVICE.read_text(encoding="utf-8") if SERVICE.exists() else ""
    impl_text = IMPL.read_text(encoding="utf-8") if IMPL.exists() else ""

    if "_auth_lifecycle_legacy_" in auth_text:
        failures.append("auth.py still contains legacy lifecycle helpers")
    else:
        print("- PASS no legacy lifecycle helpers in auth.py")

    for method in ("register", "login", "refresh"):
        if f"auth_service.{method}(" in auth_text:
            print(f"- PASS auth.py delegates {method}")
        else:
            failures.append(f"auth.py does not delegate {method}")
        if f"AuthApplicationService.{method}" in service_text:
            print(f"- PASS service owns {method}")
        else:
            failures.append(f"AuthApplicationService.{method} assignment missing")
        if f"{method}_impl" in impl_text:
            print(f"- PASS implementation module has {method}_impl")
        else:
            failures.append(f"implementation module missing {method}_impl")

    if "from __future__ import annotations" in auth_text:
        failures.append("auth.py has future annotations")
    else:
        print("- PASS no future annotations in auth.py")

    if "from app.repositories" in auth_text:
        failures.append("auth.py imports app.repositories")
    else:
        print("- PASS no repository imports in auth.py")

    try:
        auth_module = importlib.import_module("app.api_v2_routers.auth")
        print("- PASS auth router imports")
        if hasattr(auth_module, "RegisterRequest"):
            print("- PASS RegisterRequest present")
        else:
            failures.append("RegisterRequest missing from auth module")
    except Exception as exc:
        failures.append(f"auth import failed: {exc!r}")

    try:
        api_v2 = importlib.import_module("app.api_v2")
        app = getattr(api_v2, "app")
        print(f"- PASS app.api_v2 imports with {len(getattr(app, 'routes', []))} routes")
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
            "app/services/auth_lifecycle_impl.py",
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
        print("- PASS focused auth ownership ruff check")
    else:
        failures.append("focused ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS auth service ownership")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
