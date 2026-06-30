#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH_ROUTER_CANDIDATES = [
    ROOT / "app/api_v2_routers/auth.py",
    ROOT / "app/api/v2/auth.py",
    ROOT / "app/routes/auth.py",
]
REPORT_JSON = ROOT / "docs/release/auth_token_claims_introspection.json"
REPORT_MD = ROOT / "docs/release/auth_token_claims_introspection.md"


def _auth_router() -> Path | None:
    for path in AUTH_ROUTER_CANDIDATES:
        if path.exists():
            return path
    for path in (ROOT / "app").rglob("*.py"):
        if "auth" in str(path).lower() and "router" in path.read_text(encoding="utf-8", errors="ignore").lower():
            return path
    return None


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rows: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            rows.append(node.module or "")
        elif isinstance(node, ast.Import):
            rows.extend(alias.name for alias in node.names)
    return sorted(set(rows))


def _functions(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))


def main() -> int:
    router = _auth_router()
    text = router.read_text(encoding="utf-8") if router else ""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "auth_router": str(router.relative_to(ROOT)) if router else None,
        "router_exists": router is not None,
        "canonical_claim_helper_imported": "app.services.auth_token_claims" in text,
        "local_token_claim_markers": text.count("guardian_learner_ids") + text.count("create_access_token"),
        "raw_email_encrypted_assignment": any(
            item in text
            for item in (
                "email_encrypted=email",
                "email_encrypted = email",
                "email_encrypted=user.email",
                "email_encrypted = user.email",
                "email_encrypted=request.email",
                "email_encrypted = request.email",
                "email_encrypted=body.email",
                "email_encrypted = body.email",
            )
        ),
        "imports": _imports(router) if router else [],
        "functions": _functions(router) if router else [],
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Auth Token Claims Introspection",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Check | Value |",
        "|---|---|",
        f"| Auth router | {payload['auth_router'] or 'MISSING'} |",
        f"| Canonical claim helper imported | {payload['canonical_claim_helper_imported']} |",
        f"| Raw email_encrypted assignment | {payload['raw_email_encrypted_assignment']} |",
        f"| Local token claim marker count | {payload['local_token_claim_markers']} |",
        "",
        "## Functions",
        "",
        *(f"- `{name}`" for name in payload["functions"]),
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_JSON.relative_to(ROOT)}")
    print(f"Wrote {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
