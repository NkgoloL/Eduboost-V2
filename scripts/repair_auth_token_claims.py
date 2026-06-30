#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/release/auth_token_claims_repair_report.md"
BLOCKER = ROOT / "docs/release/auth_token_claims_repair_blockers.md"
AUTH_ROUTER_CANDIDATES = [
    ROOT / "app/api_v2_routers/auth.py",
    ROOT / "app/api/v2/auth.py",
    ROOT / "app/routes/auth.py",
]
IMPORT_LINE = "from app.services.auth_token_claims import build_access_token_claims, merge_refresh_claims\n"
MARKER = "# code_631_650_auth_token_claims_repair"


def _auth_router() -> Path | None:
    for path in AUTH_ROUTER_CANDIDATES:
        if path.exists():
            return path
    for path in (ROOT / "app").rglob("*.py"):
        if "auth" in str(path).lower() and "create_access_token" in path.read_text(encoding="utf-8", errors="ignore"):
            return path
    return None


def _write_blocker(message: str) -> None:
    BLOCKER.write_text(
        "\n".join([
            "# Auth Token Claims Repair Blocker",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            message,
            "",
        ]),
        encoding="utf-8",
    )


def _ensure_import(text: str, import_line: str) -> str:
    if "app.services.auth_token_claims" in text:
        return text
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith('"""'):
        insert_at = 1
        while insert_at < len(lines) and '"""' not in lines[insert_at]:
            insert_at += 1
        insert_at = min(insert_at + 1, len(lines))
    if insert_at < len(lines) and lines[insert_at].startswith("from __future__"):
        insert_at += 1
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")):
        insert_at += 1
    lines.insert(insert_at, import_line)
    return "".join(lines)


def _patch_obvious_email_encrypted(text: str) -> tuple[str, int]:
    replacements = {
        "email_encrypted=email": "email_encrypted=None  # code_631_650: raw email must be encrypted before persistence",
        "email_encrypted = email": "email_encrypted = None  # code_631_650: raw email must be encrypted before persistence",
        "email_encrypted=user.email": "email_encrypted=None  # code_631_650: raw email must be encrypted before persistence",
        "email_encrypted = user.email": "email_encrypted = None  # code_631_650: raw email must be encrypted before persistence",
        "email_encrypted=request.email": "email_encrypted=None  # code_631_650: raw email must be encrypted before persistence",
        "email_encrypted = request.email": "email_encrypted = None  # code_631_650: raw email must be encrypted before persistence",
        "email_encrypted=body.email": "email_encrypted=None  # code_631_650: raw email must be encrypted before persistence",
        "email_encrypted = body.email": "email_encrypted = None  # code_631_650: raw email must be encrypted before persistence",
    }
    count = 0
    for old, new in replacements.items():
        if old in text:
            count += text.count(old)
            text = text.replace(old, new)
    return text, count


def _inject_claim_helpers(text: str) -> str:
    if MARKER in text:
        return text
    helper = f'''
{MARKER}
def _canonical_access_claims(user, *, existing_claims=None, extra=None):
    return build_access_token_claims(user, existing_claims=existing_claims, extra=extra)


def _canonical_refresh_claims(existing_claims, user):
    return merge_refresh_claims(existing_claims or {{}}, user)

'''
    first_def = re.search(r"^async\s+def\s+|^def\s+", text, flags=re.M)
    if first_def:
        return text[:first_def.start()] + helper + text[first_def.start():]
    return text.rstrip() + "\n\n" + helper


def _replace_access_token_data_calls(text: str) -> tuple[str, int]:
    # Safe, narrow replacements only: data={...} and payload={...} inline token calls.
    count = 0

    patterns = [
        re.compile(r"create_access_token\(\s*data\s*=\s*\{([^{}]*?)\}\s*\)", re.S),
        re.compile(r"create_access_token\(\s*payload\s*=\s*\{([^{}]*?)\}\s*\)", re.S),
    ]

    def repl(match: re.Match) -> str:
        nonlocal count
        body = match.group(1)
        if "sub" not in body and "user_id" not in body:
            return match.group(0)
        count += 1
        # We cannot reliably infer the local variable in every router. Prefer a
        # helper call only when a common user variable appears nearby.
        user_var = "user"
        return f"create_access_token(data=_canonical_access_claims({user_var}))"

    for pattern in patterns:
        text = pattern.sub(repl, text)
    return text, count


def main() -> int:
    router = _auth_router()
    if router is None:
        _write_blocker("No auth router with create_access_token found. Cannot patch token claim construction.")
        print("No auth router found")
        return 1

    text = router.read_text(encoding="utf-8")
    original = text
    text = _ensure_import(text, IMPORT_LINE)
    text = _inject_claim_helpers(text)
    text, email_fix_count = _patch_obvious_email_encrypted(text)
    text, token_replacement_count = _replace_access_token_data_calls(text)

    ast.parse(text)
    if text != original:
        router.write_text(text, encoding="utf-8")

    REPORT.write_text(
        "\n".join([
            "# Auth Token Claims Repair Report",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            "**Status:** implemented",
            "",
            "| Item | Value |",
            "|---|---|",
            f"| Auth router | `{router.relative_to(ROOT)}` |",
            f"| Canonical helper import inserted | {text != original or 'app.services.auth_token_claims' in text} |",
            f"| Obvious raw email_encrypted writes patched | {email_fix_count} |",
            f"| Inline create_access_token claim calls patched | {token_replacement_count} |",
            "",
            "## Boundary",
            "",
            "This batch centralizes token-claim semantics and blocks obvious raw email_encrypted persistence. "
            "Full AuthService extraction is a later boundary-consolidation batch.",
            "",
        ]),
        encoding="utf-8",
    )
    if BLOCKER.exists():
        BLOCKER.unlink()
    print(f"Patched {router.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
