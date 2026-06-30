#!/usr/bin/env python3
"""Validate CAPS and AI-safety evidence for the release PR series."""
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "caps_ai_safety_evidence_2026-05-11.md"
LESSON_BANK_CHECK = REPO_ROOT / "scripts" / "ci" / "ci_lesson_bank_check.py"

REQUIRED_DOC_SNIPPETS = (
    "CAPS And AI Safety Evidence",
    "codex/pr21-caps-ai-safety-evidence",
    "make caps-ai-safety-release-evidence-check caps-learning-proof-check caps-alignment-contract-check learning-evidence-check ai-safety-release-check",
    "The nested `scripts/ci` import path is now repo-root aware",
    "The check now uses the async lesson repository and current validator result fields",
    "PostgreSQL authentication failed for user `postgres`",
    "fewer than 8 approved items per launch CAPS reference",
    "121 Grade 4 Mathematics items",
    "14 `approved` items",
    "1 `human_reviewed` item",
    "106 `ai_generated` items",
    "14 approved starter items",
    "approval gate remains open",
    "No live external LLM provider staging run was executed",
    "DB-backed `lesson-bank-check` remains blocked until a valid staging/test database is available",
    "does not claim full CAPS coverage, live-provider AI readiness, educator sign-off, or production AI safety certification",
)

REQUIRED_LESSON_BANK_SNIPPETS = (
    "REPO_ROOT = Path(__file__).resolve().parents[2]",
    "sys.path.insert(0, str(REPO_ROOT))",
    "await repo.count_approved_by_caps_ref_async(caps_ref)",
    "await repo.list_approved_lessons_async()",
    "if not result.passed:",
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
    print("CAPS/AI safety release evidence check")
    ok = True

    if DOC.exists():
        print(f"- PASS {DOC.relative_to(REPO_ROOT)}: document present")
    else:
        print(f"- FAIL {DOC.relative_to(REPO_ROOT)}: document missing")
        ok = False

    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    lesson_bank_text = LESSON_BANK_CHECK.read_text(encoding="utf-8")
    ok = _check(str(DOC.relative_to(REPO_ROOT)), doc_text, REQUIRED_DOC_SNIPPETS) and ok
    ok = _check(str(LESSON_BANK_CHECK.relative_to(REPO_ROOT)), lesson_bank_text, REQUIRED_LESSON_BANK_SNIPPETS) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
