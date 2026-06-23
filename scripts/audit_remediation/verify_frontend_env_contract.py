#!/usr/bin/env python3
"""Verify frontend API environment contract fails closed in production."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = ROOT / "app/frontend/next.config.js"
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if "https://eduboost-api.onrender.com/api/v2" in content:
        errors.append("next.config.js still contains hosted production API fallback")
    if "NEXT_PUBLIC_API_URL is required outside development/test" not in content:
        errors.append("next.config.js must fail closed when NEXT_PUBLIC_API_URL is missing outside development/test")
    if "process.env.NODE_ENV === \"development\"" not in content or "process.env.NODE_ENV === \"test\"" not in content:
        errors.append("next.config.js must restrict empty API fallback to development/test")
    if "http://localhost:8000/api/v2" not in content:
        errors.append("next.config.js should keep localhost fallback for development/test only")

    result = {"valid": not errors, "errors": errors, "checked": str(path.relative_to(ROOT))}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("FRONTEND ENV CONTRACT PASSED" if not errors else "FRONTEND ENV CONTRACT FAILED")
        for error in errors:
            print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
