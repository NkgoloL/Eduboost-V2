#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRITICAL = [
    "app/services/jwt_keyring.py",
    "scripts/repair_jwt_production_guard.py",
    "scripts/check_jwt_production_guard.py",
    "tests/unit/test_jwt_keyring_production_guard.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _run_case(label: str, code: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        check=False,
    )
    return result.returncode == 0, result.stdout


def main() -> int:
    failures: list[str] = []
    print("JWT production guard check")

    source = read("app/services/jwt_keyring.py")
    for token in ("settings.JWT_SECRET", "JWT_SECRET", "JWT_SECRET_KEY", "validate_jwt_keyring_environment", "dev-insecure-secret-change-me"):
        if token in source:
            print(f"- PASS jwt_keyring.py contains {token}")
        else:
            failures.append(f"jwt_keyring.py missing {token}")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    cases = [
        ("JWT_SECRET canonical fallback", "import os; os.environ['JWT_SECRET']='configured-secret'; from app.services.jwt_keyring import current_jwt_signing_key; assert current_jwt_signing_key() == 'configured-secret'"),
        ("JWT_SECRET_KEY legacy fallback", "import os; os.environ.pop('JWT_SECRET', None); os.environ['JWT_SECRET_KEY']='legacy-secret'; from app.services.jwt_keyring import current_jwt_signing_key; assert current_jwt_signing_key() == 'legacy-secret'"),
        ("production placeholder rejected", "import os; os.environ['ENVIRONMENT']='production'; os.environ.pop('JWT_SECRET', None); os.environ.pop('JWT_SECRET_KEY', None); from app.services.jwt_keyring import validate_jwt_keyring_environment, JWTKeyringError; raised=False\ntry:\n validate_jwt_keyring_environment()\nexcept JWTKeyringError:\n raised=True\nassert raised"),
    ]
    for label, code in cases:
        ok, output = _run_case(label, code)
        if ok:
            print(f"- PASS {label}")
        else:
            failures.append(label)
            print(output)

    pytest_result = subprocess.run(
        [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_jwt_keyring_production_guard.py", "-q", "--no-cov", "--tb=short"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(pytest_result.stdout)
    if pytest_result.returncode == 0:
        print("- PASS JWT production guard tests")
    else:
        failures.append("JWT production guard tests failed")

    import_result = subprocess.run(
        [sys.executable, "-c", "import os; os.environ['JWT_SECRET']='safe-import-secret-32chars-padded!!'; import app.api_v2; print('OK')"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        check=False,
    )
    if import_result.returncode == 0:
        print("- PASS app.api_v2 imports with safe JWT secret")
    else:
        failures.append("app.api_v2 import failed with safe JWT secret")
        print(import_result.stdout)

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused ruff JWT guard check")
    else:
        failures.append("focused ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS JWT production guard check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
