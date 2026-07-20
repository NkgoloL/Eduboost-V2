#!/usr/bin/env python3
"""Verify backend-fast authority Python runtime dependencies.

This script checks the interpreter used by `make test-fast` and imports the
modules that the failed authority run reported as missing. It is intentionally
separate from `make test-fast`: passing this verifier only means the Python
runtime is dependency-complete enough to retry the real gate.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from scripts._subprocess import run
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"

REQUIRED_IMPORTS: dict[str, str] = {
    "anthropic": "anthropic",
    "arq": "arq",
    "fastapi": "fastapi",
    "httpx": "httpx",
    "hypothesis": "hypothesis",
    "jinja2": "jinja2",
    "jwt": "PyJWT",
    "prometheus_client": "prometheus-client",
    "psycopg2": "psycopg2-binary or psycopg2",
    "pypdf": "pypdf",
    "mcp": "mcp[cli]",
    "redis": "redis",
    "starlette": "starlette",
    "structlog": "structlog",
    "yaml": "PyYAML",
}

OPTIONAL_IMPORTS: dict[str, str] = {}


@dataclass(frozen=True)
class ImportCheck:
    module: str
    package_hint: str
    available: bool
    error: str | None = None


@dataclass(frozen=True)
class VerificationResult:
    valid: bool
    static_only: bool
    authority_interpreter: str
    interpreter_exists: bool
    makefile_pytest_line: str | None
    required_imports: list[ImportCheck]
    optional_imports: list[ImportCheck]
    missing_required_modules: list[str]
    missing_optional_modules: list[str]
    requirements_dev_exists: bool
    requirements_dev_mentions: dict[str, bool]
    recommendations: list[str]


def _extract_pytest_line(makefile_text: str) -> str | None:
    for line in makefile_text.splitlines():
        if line.startswith("PYTEST ?="):
            return line.strip()
    return None


def authority_interpreter() -> tuple[str, str | None]:
    text = MAKEFILE.read_text(encoding="utf-8") if MAKEFILE.exists() else ""
    line = _extract_pytest_line(text)
    if line:
        value = line.split("?=", 1)[1].strip()
        return value.split()[0], line
    return ".venv/bin/python", line


def _import_module(interpreter: Path, module: str, root: Path) -> ImportCheck:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root)
    proc = run(
        [str(interpreter), "-c", f"import {module}; print('ok')"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    return ImportCheck(
        module=module,
        package_hint=REQUIRED_IMPORTS.get(module, OPTIONAL_IMPORTS.get(module, module)),
        available=proc.returncode == 0,
        error=None if proc.returncode == 0 else (proc.stderr or proc.stdout).strip(),
    )


def _requirements_mentions(requirements_text: str, modules: Iterable[str]) -> dict[str, bool]:
    normalized = requirements_text.lower().replace("_", "-")
    module_to_needles = {
        "yaml": ["pyyaml"],
        "jwt": ["pyjwt"],
        "prometheus_client": ["prometheus-client"],
        "psycopg2": ["psycopg2", "psycopg2-binary"],
    }
    result: dict[str, bool] = {}
    for module in modules:
        needles = module_to_needles.get(module, [module.replace("_", "-")])
        result[module] = any(re.search(rf"(^|\n)\s*{re.escape(needle)}([=<>~!\s#]|$)", normalized) for needle in needles)
    return result


def verify(static_only: bool = False) -> VerificationResult:
    interp_rel, line = authority_interpreter()
    interpreter = (ROOT / interp_rel).resolve() if not Path(interp_rel).is_absolute() else Path(interp_rel)
    interpreter_exists = interpreter.exists()

    requirements_dev = ROOT / "requirements/dev.txt"
    requirements_text = requirements_dev.read_text(encoding="utf-8") if requirements_dev.exists() else ""
    mentions = _requirements_mentions(requirements_text, [*REQUIRED_IMPORTS, *OPTIONAL_IMPORTS])

    required: list[ImportCheck] = []
    optional: list[ImportCheck] = []
    if not static_only and interpreter_exists:
        required = [_import_module(interpreter, module, ROOT) for module in REQUIRED_IMPORTS]
        optional = [_import_module(interpreter, module, ROOT) for module in OPTIONAL_IMPORTS]
    else:
        required = [
            ImportCheck(module=module, package_hint=hint, available=False, error="not checked in static-only mode" if static_only else "authority interpreter missing")
            for module, hint in REQUIRED_IMPORTS.items()
        ]
        optional = [
            ImportCheck(module=module, package_hint=hint, available=False, error="not checked in static-only mode" if static_only else "authority interpreter missing")
            for module, hint in OPTIONAL_IMPORTS.items()
        ]

    missing_required = [] if static_only else [item.module for item in required if not item.available]
    missing_optional = [] if static_only else [item.module for item in optional if not item.available]
    missing_declared = [module for module, present in mentions.items() if module in REQUIRED_IMPORTS and not present]

    recommendations: list[str] = []
    if not interpreter_exists:
        recommendations.append("Create the repo .venv or run scripts/audit_remediation/sync_backend_fast_runtime_dependencies.sh.")
    if missing_required:
        recommendations.append("Install requirements/dev.txt into the Makefile authority interpreter, then rerun this verifier.")
    if missing_declared:
        recommendations.append("Review requirements/dev.txt declarations for missing backend-fast runtime dependencies: " + ", ".join(missing_declared))
    if missing_optional:
        recommendations.append("Optional modules missing but not release-blocking for this verifier: " + ", ".join(missing_optional))
    if not missing_required and interpreter_exists and not static_only:
        recommendations.append("Runtime dependency check passed; rerun the backend fast authority gate or proceed to application-failure remediation if it still fails.")

    valid = bool(MAKEFILE.exists() and requirements_dev.exists() and line and (static_only or (interpreter_exists and not missing_required)))
    return VerificationResult(
        valid=valid,
        static_only=static_only,
        authority_interpreter=str(interpreter),
        interpreter_exists=interpreter_exists,
        makefile_pytest_line=line,
        required_imports=required,
        optional_imports=optional,
        missing_required_modules=missing_required,
        missing_optional_modules=missing_optional,
        requirements_dev_exists=requirements_dev.exists(),
        requirements_dev_mentions=mentions,
        recommendations=recommendations,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--static-only", action="store_true", help="Validate script/config shape without importing runtime modules.")
    parser.add_argument("--output", help="Optional path to write JSON result.")
    args = parser.parse_args()

    result = verify(static_only=args.static_only)
    payload = asdict(result)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("backend fast runtime dependency verification:", "valid" if result.valid else "invalid")
        if result.missing_required_modules:
            print("missing required modules:", ", ".join(result.missing_required_modules))
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
