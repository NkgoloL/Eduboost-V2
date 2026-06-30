#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON_AUTH = ROOT / "app/services/lesson_authorization.py"
LESSONS_ROUTER = ROOT / "app/api_v2_routers/lessons.py"
CRITICAL = [
    "app/services/lesson_authorization.py",
    "app/api_v2_routers/lessons.py",
    "scripts/patch_lesson_authorization_hardening.py",
    "scripts/check_lesson_authorization_hardening.py",
    "tests/unit/test_lesson_authorization_hardening.py",
    "tests/integration/test_lesson_authorization_negative_contract.py",
]


def _read(path: Path | str) -> str:
    target = ROOT / path if isinstance(path, str) else path
    return target.read_text(encoding="utf-8")


def _function_block(source: str, function_name: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno or node.lineno])
    return ""


def main() -> int:
    failures: list[str] = []
    print("Lesson authorization hardening check")

    lesson_auth_source = _read(LESSON_AUTH)
    owner_lookup = _function_block(lesson_auth_source, "lesson_owner_learner_id")
    if "except Exception" in owner_lookup:
        failures.append("lesson_owner_learner_id still swallows broad Exception")
        print("- FAIL broad Exception handler remains in owner lookup")
    else:
        print("- PASS owner lookup does not swallow broad Exception")

    if "except (TypeError, AttributeError, RuntimeError, ValueError)" in owner_lookup:
        print("- PASS compatibility fallback exceptions are narrowed")
    else:
        failures.append("expected narrowed compatibility exceptions missing")

    router_source = _read(LESSONS_ROUTER)
    required_router_tokens = [
        "require_lesson_read_access_for_current_user",
        "require_lesson_write_access_for_current_user",
        "iter_sync_lesson_ids",
        "# code_611_630_lesson_read_authz",
        "# code_611_630_lesson_write_authz",
        "# code_611_630_lesson_sync_authz",
    ]
    for token in required_router_tokens:
        if token in router_source:
            print(f"- PASS lessons router contains {token}")
        else:
            print(f"- FAIL lessons router missing {token}")
            failures.append(f"missing router token {token}")

    for path in CRITICAL:
        ast.parse(_read(path))
        print(f"- PASS syntax {path}")

    pytest_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_lesson_authorization_hardening.py",
            "tests/integration/test_lesson_authorization_negative_contract.py",
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
        print("- PASS lesson authorization hardening tests")
    else:
        failures.append("lesson authorization hardening tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff lesson authorization hardening check")
    else:
        print(ruff.stdout)
        failures.append("focused Ruff failed")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS lesson authorization hardening check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
