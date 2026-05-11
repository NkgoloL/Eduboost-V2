#!/usr/bin/env python3
"""Validate privacy/legal evidence for the release PR series."""
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "legal" / "privacy_legal_evidence_2026-05-11.md"
DIAGNOSTICS = REPO_ROOT / "app" / "api_v2_routers" / "diagnostics.py"
GENERATOR = REPO_ROOT / "scripts" / "generate_consent_gate_inventory.py"

REQUIRED_DOC_SNIPPETS = (
    "Privacy And Legal Evidence",
    "codex/pr20-privacy-legal-evidence",
    "diagnostic session recovery, next-item, and response routes",
    "make popia-consent-gate-check",
    "make popia-consent-boundary-check",
    "python3 scripts/check_popia_legal_evidence.py",
    "0 new unallowlisted missing markers",
    "0 stale allowlist entries",
    "Legal documents remain templates/evidence artifacts",
    "does not claim external legal sign-off",
)

REQUIRED_DIAGNOSTICS_SNIPPETS = (
    "recover_diagnostic_session",
    "diagnostic_next_item",
    "diagnostic_respond",
    "require_learner_read_for_current_user",
    "require_learner_write_for_current_user",
    "await require_active_consent_for_current_user",
)

REQUIRED_GENERATOR_SNIPPETS = (
    'file_path.name.startswith("test_")',
    'file_path.name.endswith("_test.py")',
    "parents = {",
)


def _check(label: str, text: str, snippets: tuple[str, ...]) -> bool:
    ok = True
    for snippet in snippets:
        if snippet in text:
            print(f"- PASS {label}: contains {snippet!r}")
            continue
        print(f"- FAIL {label}: missing {snippet!r}")
        ok = False
    return ok


def main() -> int:
    print("Privacy/legal release evidence check")
    ok = True

    if DOC.exists():
        print(f"- PASS {DOC.relative_to(REPO_ROOT)}: document present")
    else:
        print(f"- FAIL {DOC.relative_to(REPO_ROOT)}: document missing")
        ok = False

    ok = _check(str(DOC.relative_to(REPO_ROOT)), DOC.read_text(encoding="utf-8") if DOC.exists() else "", REQUIRED_DOC_SNIPPETS) and ok
    ok = _check(str(DIAGNOSTICS.relative_to(REPO_ROOT)), DIAGNOSTICS.read_text(encoding="utf-8"), REQUIRED_DIAGNOSTICS_SNIPPETS) and ok
    ok = _check(str(GENERATOR.relative_to(REPO_ROOT)), GENERATOR.read_text(encoding="utf-8"), REQUIRED_GENERATOR_SNIPPETS) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
