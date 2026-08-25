#!/usr/bin/env python3
"""Verify the Python environment required to run the backend fast gate.

The important detail is that the imports must be checked in the same Python
interpreter that the backend-fast authority command uses. The script therefore
spawns `--python-bin` for each import check instead of importing modules in the
verifier process by default.
"""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
import platform
from scripts._subprocess import run
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

# module, reason, requirement hint
REQUIRED_IMPORTS: tuple[tuple[str, str, str], ...] = (
    ("fastapi", "backend runtime import", "requirements/base.txt"),
    ("sqlalchemy", "model/repository imports", "requirements/base.txt"),
    ("alembic", "migration graph verification", "requirements/base.txt"),
    ("asyncpg", "PostgreSQL async SQLAlchemy URL imports", "requirements/base.txt"),
    ("jwt", "JWT/token tests", "requirements/base.txt"),
    ("passlib.context", "password/auth tests", "requirements/base.txt"),
    ("redis", "quota/session/token revocation tests", "requirements/base.txt"),
    ("structlog", "runtime logging imports", "requirements/base.txt"),
    ("anthropic", "LLM gateway import contracts", "requirements/base.txt"),
    ("groq", "LLM gateway import contracts", "requirements/base.txt"),
    ("openai", "LLM gateway import contracts", "requirements/base.txt"),
    ("posthog", "analytics imports", "requirements/base.txt"),
    ("sklearn", "diagnostic/IRT tests", "requirements/base.txt"),
    ("numpy", "diagnostic/IRT tests", "requirements/base.txt"),
    ("pandas", "data/reporting imports", "requirements/base.txt"),
    ("scipy", "diagnostic/IRT tests", "requirements/base.txt"),
    ("sendgrid", "notification imports", "requirements/base.txt"),
    ("jinja2", "template/rendering imports", "requirements/base.txt"),
    ("boto3", "storage integration imports", "requirements/base.txt"),
    ("stripe", "billing router imports", "requirements/base.txt"),
    ("prometheus_fastapi_instrumentator", "metrics imports", "requirements/base.txt"),
    ("sentry_sdk", "observability imports", "requirements/base.txt"),
    ("azure.identity", "Azure secret/key-vault imports", "requirements/base.txt"),
    ("dotenv", "environment loading imports", "requirements/base.txt"),
    ("httpx", "API/client tests", "requirements/base.txt"),
    ("tenacity", "retry-policy imports", "requirements/base.txt"),
    ("bleach", "content sanitisation imports", "requirements/base.txt"),
    ("phonenumbers", "profile validation imports", "requirements/base.txt"),
    ("dateutil", "date/time utilities", "requirements/base.txt"),
    ("babel", "locale/reporting imports", "requirements/base.txt"),
    ("reportlab", "PDF/report generation imports", "requirements/base.txt"),
    ("pypdf", "PDF extraction imports", "requirements/base.txt"),
    ("arq", "worker dependency imports", "requirements/base.txt"),
    ("pytest", "test runner", "requirements/dev.txt"),
    ("pytest_asyncio", "async unit tests", "requirements/dev.txt"),
    ("pytest_cov", "pytest --no-cov option registration", "requirements/dev.txt"),
    ("xdist", "pytest -n auto option registration", "requirements/dev.txt"),
    ("pytest_mock", "mocking fixtures", "requirements/dev.txt"),
    ("hypothesis", "property tests", "requirements/dev.txt"),
    ("factory", "factory-boy tests", "requirements/dev.txt"),
    ("faker", "test data generation", "requirements/dev.txt"),
    ("aiosqlite", "SQLite async test paths", "requirements/dev.txt"),
)


def _resolve_python_bin(root: Path, python_bin: str) -> Path:
    candidate = Path(python_bin)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def _python_version(python_bin: Path) -> str:
    completed = run(
        [str(python_bin), "-c", "import platform; print(platform.python_version())"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else f"unavailable: {completed.stdout.strip()}"


def import_status(python_bin: Path, root: Path = ROOT) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for module_name, reason, hint in REQUIRED_IMPORTS:
        completed = run(
            [str(python_bin), "-c", f"import {module_name}; print('ok')"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            results.append({
                "module": module_name,
                "valid": False,
                "reason": reason,
                "requirement_hint": hint,
                "error": (completed.stderr or completed.stdout).strip(),
            })
        else:
            version_completed = run(
                [str(python_bin), "-c", f"import {module_name} as m; print(getattr(m, '__version__', ''))"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            version = version_completed.stdout.strip() if version_completed.returncode == 0 else None
            results.append({
                "module": module_name,
                "valid": True,
                "reason": reason,
                "requirement_hint": hint,
                "version": version or None,
            })
    return results


def run_pip_check(python_bin: Path) -> dict[str, Any]:
    completed = run(
        [str(python_bin), "-m", "pip", "check"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "valid": completed.returncode == 0,
        "returncode": completed.returncode,
        "output": completed.stdout.strip(),
    }


def verify(root: Path = ROOT, *, run_pip: bool = False, python_bin: str = sys.executable) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    resolved_python = _resolve_python_bin(root, python_bin)
    if not resolved_python.exists():
        errors.append(f"python interpreter not found: {resolved_python}")

    for rel_path in ["requirements/base.txt", "requirements/dev.txt", "Makefile", "pytest.ini"]:
        path = root / rel_path
        if path.exists():
            checked.append(rel_path)
        else:
            errors.append(f"missing {rel_path}")

    imports: list[dict[str, Any]] = []
    if resolved_python.exists():
        imports = import_status(resolved_python, root)
    else:
        imports = [
            {
                "module": module_name,
                "valid": False,
                "reason": reason,
                "requirement_hint": hint,
                "error": "authority interpreter missing",
            }
            for module_name, reason, hint in REQUIRED_IMPORTS
        ]

    missing = [item for item in imports if not item["valid"]]
    if missing:
        errors.append(f"{len(missing)} backend-fast Python import requirement(s) missing")

    pip_check = None
    if run_pip and resolved_python.exists():
        pip_check = run_pip_check(resolved_python)
        checked.append("python -m pip check")
        if not pip_check["valid"]:
            errors.append("pip check failed")

    version = _python_version(resolved_python) if resolved_python.exists() else "missing"
    version_parts = tuple(int(part) for part in version.split(".")[:2] if part.isdigit()) if resolved_python.exists() else ()
    if version_parts and version_parts not in {(3, 11), (3, 12), (3, 13)}:
        warnings.append(f"Python {version} is outside the expected 3.11-3.13 range")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "python": {
            "executable": str(resolved_python),
            "version": version,
        },
        "imports": imports,
        "missing_modules": [item["module"] for item in missing],
        "install_hint": f"{resolved_python} -m pip install -r requirements/dev.txt",
        "pip_check": pip_check,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--run-pip-check", action="store_true")
    parser.add_argument("--python-bin", default=sys.executable)
    args = parser.parse_args()
    result = verify(args.root.resolve(), run_pip=args.run_pip_check, python_bin=args.python_bin)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST ENVIRONMENT PASSED" if result["valid"] else "BACKEND FAST ENVIRONMENT FAILED")
        for error in result["errors"]:
            print(f"- {error}")
        for module in result["missing_modules"]:
            print(f"missing: {module}")
        print(f"install hint: {result['install_hint']}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
