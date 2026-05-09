#!/usr/bin/env python3
"""Fail if learner-scoped routes lack an authorization/authentication marker."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_learner_authz_matrix import collect_rows


ALLOWLIST = {
    # Catalog/auth-boundary endpoints with separate docs/tests.
    ("assessments.py", "GET", "/"),
    ("assessments.py", "GET", ""),
    ("onboarding.py", "GET", "/questions"),
    # Development/session bootstrap is not learner-object scoped.
    ("auth.py", "POST", "/dev-session"),
    # Operational consent-renewal trigger is tracked outside learner-object route checks.
    # Public ranking endpoint; this is aggregate gamification data and not learner-object scoped.
    ("gamification.py", "GET", "/leaderboard"),
}


def _is_allowlisted(row) -> bool:
    return (row.router, row.method, row.path) in ALLOWLIST


def main() -> int:
    rows = collect_rows()
    missing = [row for row in rows if row.status == "missing" and not _is_allowlisted(row)]

    print("Learner authorization coverage check")
    for row in rows:
        status = "ALLOW" if _is_allowlisted(row) else row.status.upper()
        print(f"- {status} {row.router} {row.method} {row.path} -> {row.function} [{row.authz_marker}]")

    if missing:
        print("\nMissing learner authorization coverage:")
        for row in missing:
            print(f"- {row.router} {row.method} {row.path} -> {row.function}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
