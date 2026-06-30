#!/usr/bin/env python3
"""Validate browser-exposed frontend environment variables.

Only NEXT_PUBLIC_* variables are shipped to browsers by Next.js. This script
fails when a secret-looking key is exposed through that namespace.
"""
from __future__ import annotations

import os
import re

ALLOWLIST = {"NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_APP_ENV", "NEXT_PUBLIC_ENABLE_DEV_SESSION"}
SECRET_PATTERN = re.compile(r"(SECRET|TOKEN|KEY|PASSWORD|PRIVATE|DATABASE_URL|REDIS_URL)", re.I)


def main() -> int:
    bad = sorted(
        key for key in os.environ
        if key.startswith("NEXT_PUBLIC_") and SECRET_PATTERN.search(key) and key not in ALLOWLIST
    )
    if bad:
        print("Secret-like browser environment variables are not allowed:")
        for key in bad:
            print(f"- {key}")
        return 1
    print("Frontend environment exposure OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
