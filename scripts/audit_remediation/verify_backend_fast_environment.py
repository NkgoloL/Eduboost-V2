#!/usr/bin/env python3
"""Verify the Python environment required to run the backend fast gate."""
from __future__ import annotations

import argparse
import importlib
import json
import platform
import subprocess
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
    ("jose", "JWT/token tests", "requirements/base.txt"),
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


def import_status() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for module_name, reason, hint in REQUIRED_IMPORTS:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001 - diagnostic tool must report all import failures
            results.append({
                "module": module_name,
                "valid": False,
                "reason": reason,
                "requirement_hint": hint,
                "error": f"{type(exc).__name__}: {exc}",
            })
        else:
            version = getattr(module, "__version__", None)
            results.append({
                "module": module_name,
                "valid": True,
                "reason": reason,
                "requirement_hint": hint,
                "version": str(version) if version is not None else None,
            })
    return results


def run_pip_check(python_bin: str) -> dict[str, Any]:
    completed = subprocess.run(
        [python_bin, "-m", "pip", "check"],
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

    for rel_path in ["requirements/base.txt", "requirements/dev.txt", "Makefile", "pytest.ini"]:
        path = root / rel_path
        if path.exists():
            checked.append(rel_path)
        else:
            errors.append(f"missing {rel_path}")

    imports = import_status()
    missing = [item for item in imports if not item["valid"]]
    if missing:
        errors.append(f"{len(missing)} backend-fast Python import requirement(s) missing")

    pip_check = None
    if run_pip:
        pip_check = run_pip_check(python_bin)
        checked.append("python -m pip check")
        if not pip_check["valid"]:
            errors.append("pip check failed")

    if sys.version_info[:2] not in {(3, 11), (3, 12), (3, 13)}:
        warnings.append(f"Python {platform.python_version()} is outside the expected 3.11-3.13 range")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "python": {
            "executable": python_bin,
            "version": platform.python_version(),
        },
        "imports": imports,
        "missing_modules": [item["module"] for item in missing],
        "install_hint": f"{python_bin} -m pip install -r requirements/dev.txt",
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
