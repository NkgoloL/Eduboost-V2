#!/usr/bin/env python3
"""Validate that local/CI test environment variables are safe and parseable."""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from dataclasses import dataclass


PLACEHOLDER_TOKENS = {
    "",
    "changeme",
    "change_me",
    "change-me",
    "secret",
    "placeholder",
    "todo",
    "password",
    "example",
}


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    message: str


def _is_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    normalized = value.strip().lower()
    if normalized in PLACEHOLDER_TOKENS:
        return True
    return any(token in normalized for token in ("change_me", "changeme", "placeholder"))


def _parse_allowed_origins(value: str | None) -> list[str]:
    if not value:
        return []
    raw = value.strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
            return parsed
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in raw.split(",") if item.strip()]


def _valid_fernetish_key(value: str | None) -> bool:
    if not value:
        return False
    try:
        decoded = base64.urlsafe_b64decode(value.encode("utf-8"))
    except Exception:
        return False
    return len(decoded) == 32


def _db_url_is_test_safe(url: str | None) -> bool:
    if not url:
        return False
    lower = url.lower()
    return (
        "sqlite" in lower
        or "test" in lower
        or "eduboost_test" in lower
        or re.search(r"[/_]test(?:[/?#]|$)", lower) is not None
    )


def run_checks(strict: bool = False) -> list[CheckResult]:
    env = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "test")).lower()
    database_url = os.getenv("DATABASE_URL", "")
    allowed_origins = os.getenv("ALLOWED_ORIGINS", '["http://localhost:3000","http://localhost:8000","http://test"]')
    encryption_key = os.getenv("ENCRYPTION_KEY", "")
    jwt_secret = os.getenv("JWT_SECRET", os.getenv("JWT_SECRET_KEY", ""))

    return [
        CheckResult("environment_not_production", env not in {"production", "prod"}, f"ENVIRONMENT/APP_ENV={env!r}"),
        CheckResult("database_url_test_safe", _db_url_is_test_safe(database_url) or not strict, "DATABASE_URL is test-like or strict mode is disabled"),
        CheckResult("allowed_origins_parse", bool(_parse_allowed_origins(allowed_origins)), "ALLOWED_ORIGINS parses as JSON list or comma-separated list"),
        CheckResult("encryption_key_valid", _valid_fernetish_key(encryption_key) or not strict, "ENCRYPTION_KEY decodes to 32 bytes or strict mode is disabled"),
        CheckResult("jwt_secret_not_placeholder", (not _is_placeholder(jwt_secret)) or not strict, "JWT secret is non-placeholder or strict mode is disabled"),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Fail on missing/non-test env values.")
    args = parser.parse_args(argv)

    failures = []
    print("EduBoost test environment check")
    for result in run_checks(strict=args.strict):
        status = "PASS" if result.passed else "FAIL"
        print(f"- {status} [{result.name}] {result.message}")
        if not result.passed:
            failures.append(result.name)

    if failures:
        print("Failed checks: " + ", ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

