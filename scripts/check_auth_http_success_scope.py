#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
CRITICAL = [
    "app/api_v2_routers/auth.py",
    "app/services/auth_application_service.py",
    "app/services/auth_lifecycle_impl.py",
    "app/api_v2_deps/auth_service.py",
    "tests/integration/test_auth_lifecycle_http_success_scope.py",
]


def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main() -> int:
    failures: list[str] = []
    print("Auth HTTP success/scope check")

    auth = read("app/api_v2_routers/auth.py")
    if "from __future__ import annotations" in auth:
        failures.append("auth.py has future annotations")
    else:
        print("- PASS no future annotations in auth.py")

    if "from app.repositories" in auth:
        failures.append("auth.py imports app.repositories")
    else:
        print("- PASS no app.repositories import in auth.py")

    for token in ("auth_service.register(", "auth_service.login(", "auth_service.refresh("):
        if token in auth:
            print(f"- PASS auth.py contains {token}")
        else:
            failures.append(f"missing {token}")

    test_source = read("tests/integration/test_auth_lifecycle_http_success_scope.py")
    for token in (
        "test_register_http_success_path_uses_service_override",
        "test_login_http_success_path_uses_service_override",
        "test_refresh_http_success_path_preserves_guardian_scope",
        "test_duplicate_registration_failure_is_clean_non_500",
        "test_wrong_password_failure_is_clean_non_500",
        "guardian_learner_ids",
    ):
        if token in test_source:
            print(f"- PASS test contains {token}")
        else:
            failures.append(f"test missing {token}")

    for path in CRITICAL:
        if (ROOT / path).exists():
            ast.parse(read(path))
            print(f"- PASS syntax {path}")
        else:
            failures.append(f"missing {path}")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *[path for path in CRITICAL if (ROOT / path).exists()],
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
        print("- PASS focused ruff auth HTTP scope check")
    else:
        failures.append("focused ruff failed")
        print(ruff.stdout)

    pytest_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/integration/test_auth_lifecycle_http_success_scope.py",
            "-q",
            "--no-cov",
            "--tb=short",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(pytest_result.stdout)
    if pytest_result.returncode == 0:
        print("- PASS auth HTTP success/scope integration tests")
    else:
        failures.append("auth HTTP success/scope integration tests failed")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS auth HTTP success/scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
