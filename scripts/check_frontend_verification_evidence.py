#!/usr/bin/env python3
"""Validate frontend verification evidence for the release PR series."""
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_verification_evidence_2026-05-11.md"
PACKAGE_JSON = REPO_ROOT / "app" / "frontend" / "package.json"
GITIGNORE = REPO_ROOT / ".gitignore"

REQUIRED_DOC_SNIPPETS = (
    "Frontend Verification Evidence",
    "codex/pr18-frontend-verification",
    "npm ci",
    "npm run type-check",
    "npm run test",
    "npm run a11y-check",
    "npm run build",
    "10 test files and 41 tests",
    "6 moderate and 4 high",
    "Node.js `v18.19.1`",
    "Browser E2E against staging remains part of the staging and operations PR",
)

REQUIRED_PACKAGE_SNIPPETS = (
    '"eslint-config-next": "14.2.35"',
    '"vitest": "^1.6.1"',
    '"@vitest/coverage-v8": "^1.6.1"',
)


def _check_contains(label: str, text: str, snippets: tuple[str, ...]) -> bool:
    ok = True
    for snippet in snippets:
        if snippet in text:
            print(f"- PASS {label}: contains {snippet!r}")
            continue
        print(f"- FAIL {label}: missing {snippet!r}")
        ok = False
    return ok


def main() -> int:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    package_text = PACKAGE_JSON.read_text(encoding="utf-8") if PACKAGE_JSON.exists() else ""
    gitignore_text = GITIGNORE.read_text(encoding="utf-8") if GITIGNORE.exists() else ""

    print("Frontend verification evidence check")
    ok = True

    if DOC.exists():
        print(f"- PASS {DOC.relative_to(REPO_ROOT)}: document present")
    else:
        print(f"- FAIL {DOC.relative_to(REPO_ROOT)}: document missing")
        ok = False

    ok = _check_contains(str(DOC.relative_to(REPO_ROOT)), doc_text, REQUIRED_DOC_SNIPPETS) and ok
    ok = _check_contains(str(PACKAGE_JSON.relative_to(REPO_ROOT)), package_text, REQUIRED_PACKAGE_SNIPPETS) and ok

    if "*.tsbuildinfo" in gitignore_text:
        print("- PASS .gitignore: ignores TypeScript build info")
    else:
        print("- FAIL .gitignore: missing TypeScript build info ignore")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
