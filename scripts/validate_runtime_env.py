#!/usr/bin/env python3
"""Validate runtime environment variables before deploy/promotion."""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

SECRET_NAMES = {
    "JWT_SECRET",
    "ENCRYPTION_KEY",
    "ENCRYPTION_SALT",
    "DATABASE_URL",
    "REDIS_URL",
    "AUDIT_HMAC_SECRET",
    "BACKUP_ENCRYPTION_KEY",
}
OPTIONAL_PROVIDERS = {"GROQ_API_KEY", "ANTHROPIC_API_KEY", "SENDGRID_API_KEY", "STRIPE_SECRET_KEY"}
PLACEHOLDER_RE = re.compile(r"CHANGE_ME|devpassword|test-|example|placeholder", re.IGNORECASE)


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.split("#", 1)[0].strip().strip('"').strip("'")
    return values


def getenv(name: str, file_values: dict[str, str]) -> str:
    return os.getenv(name, file_values.get(name, ""))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["development", "test", "staging", "production"], default=os.getenv("APP_ENV", "development"))
    parser.add_argument("--env-file", default=".env")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    file_values = parse_env_file(root / args.env_file)
    errors: list[str] = []

    required = set(SECRET_NAMES)
    if args.env in {"staging", "production"}:
        required.update({"AZURE_KEY_VAULT_URL", "SENTRY_DSN", "ALLOWED_ORIGINS"})

    for name in sorted(required):
        value = getenv(name, file_values)
        if not value:
            errors.append(f"{name} is required for {args.env}")
            continue
        if args.env in {"staging", "production"} and PLACEHOLDER_RE.search(value):
            errors.append(f"{name} contains a placeholder/dev value")

    if args.env in {"staging", "production"}:
        jwt_secret = getenv("JWT_SECRET", file_values)
        if jwt_secret and len(jwt_secret) < 32:
            errors.append("JWT_SECRET must be at least 32 characters")
        origins = getenv("ALLOWED_ORIGINS", file_values)
        if "*" in origins:
            errors.append("ALLOWED_ORIGINS must not contain wildcard origins in staging/production")
        if not any(getenv(name, file_values) for name in OPTIONAL_PROVIDERS):
            errors.append("at least one external provider secret should be configured or explicitly mocked")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Runtime environment OK for {args.env}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
