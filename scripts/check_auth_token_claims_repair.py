#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

from app.services.auth_token_claims import contains_raw_email_encrypted_assignment


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/release/auth_token_claims_repair_report.md"
AUTH_ROUTER_CANDIDATES = [
    ROOT / "app/api_v2_routers/auth.py",
    ROOT / "app/api/v2/auth.py",
    ROOT / "app/routes/auth.py",
]


def _auth_router() -> Path | None:
    for path in AUTH_ROUTER_CANDIDATES:
        if path.exists():
            return path
    for path in (ROOT / "app").rglob("*.py"):
        if "auth" in str(path).lower() and "create_access_token" in path.read_text(encoding="utf-8", errors="ignore"):
            return path
    return None


def main() -> int:
    failures: list[str] = []
    print("Auth token claims repair check")

    helper = ROOT / "app/services/auth_token_claims.py"
    if helper.exists():
        print("- PASS canonical claim helper exists")
    else:
        print("- FAIL canonical claim helper missing")
        failures.append("helper missing")

    router = _auth_router()
    if router is None:
        print("- FAIL auth router missing")
        failures.append("router missing")
    else:
        source = router.read_text(encoding="utf-8")
        ast.parse(source)
        if "app.services.auth_token_claims" in source:
            print(f"- PASS auth router imports canonical helper: {router.relative_to(ROOT)}")
        else:
            print("- FAIL auth router missing canonical helper import")
            failures.append("helper import missing")
        if "# code_631_650_auth_token_claims_repair" in source:
            print("- PASS auth router has canonical claim helper marker")
        else:
            print("- FAIL auth router missing canonical claim helper marker")
            failures.append("helper marker missing")
        if contains_raw_email_encrypted_assignment(source):
            print("- FAIL auth router contains obvious raw email_encrypted assignment")
            failures.append("raw email_encrypted")
        else:
            print("- PASS no obvious raw email_encrypted assignment in auth router")

    if REPORT.exists():
        print("- PASS repair report exists")
    else:
        print("- FAIL repair report missing")
        failures.append("report missing")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS auth token claims repair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
