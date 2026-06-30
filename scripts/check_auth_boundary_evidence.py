#!/usr/bin/env python3
"""Validate auth, token, cookie, RBAC, rate-limit, and object-auth evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "app/api_v2_routers/auth.py",
    "app/core/rbac.py",
    "app/core/refresh_tokens.py",
    "app/core/token_revocation.py",
    "app/core/rate_limit.py",
    "app/security/object_authorization.py",
    "docs/security/auth_session_policy.md",
    "docs/security/operational_auth_boundaries.md",
    "docs/security/object_authorization.md",
    "docs/security/auth_boundary_evidence.md",
    "tests/unit/test_v2_auth.py",
    "tests/unit/test_refresh_token_rotation.py",
    "tests/unit/test_token_denylist.py",
    "tests/unit/test_auth_cookie_policy.py",
    "tests/unit/test_object_authorization.py",
    "tests/unit/test_authorization_policy.py",
    "tests/integration/test_rbac.py",
    "tests/integration/test_rate_limits.py",
)

CONTENT_REQUIREMENTS = {
    "docs/security/auth_boundary_evidence.md": (
        "Authentication",
        "Token Rotation And Revocation",
        "Cookie Policy",
        "RBAC",
        "Object Authorization",
        "Rate Limiting",
        "make auth-boundary-check",
        "Verification Gaps",
    ),
    "Makefile": ("auth-boundary-check",),
}


@dataclass(frozen=True)
class EvidenceResult:
    target: str
    ok: bool
    detail: str


def check_all() -> list[EvidenceResult]:
    results: list[EvidenceResult] = []
    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))
    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8") if (REPO_ROOT / rel_path).exists() else ""
        for snippet in snippets:
            results.append(EvidenceResult(rel_path, snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))
    return results


def main() -> int:
    results = check_all()
    print("Auth boundary evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
