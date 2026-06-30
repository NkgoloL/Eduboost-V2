#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    Path("docs/release/backend_consolidation_readiness_matrix.md"),
    Path("docs/release/backend_data_retention_decision_checklist.md"),
    Path("docs/release/backend_consolidation_decision_record.md"),
    Path("docs/release/backend_deletion_candidate_inventory.md"),
]
FORBIDDEN_DOC_PHRASES = [
    "fresh-start audit acceptable: yes",
    "discard audit history",
    "drop consent history",
    "deletion approved",
    "stamp head as repair",
]

def _contains_forbidden_phrase(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8").lower()
    except UnicodeDecodeError:
        return []
    return [phrase for phrase in FORBIDDEN_DOC_PHRASES if phrase in text]

def main() -> int:
    failures: list[str] = []
    print("Backend consolidation no-op/deletion guard")
    for relative in REQUIRED_FILES:
        path = REPO_ROOT / relative
        if path.exists():
            print(f"- PASS [file] {relative}: present")
        else:
            print(f"- FAIL [file] {relative}: missing")
            failures.append(f"missing {relative}")
    decision = REPO_ROOT / "docs/release/backend_consolidation_decision_record.md"
    decision_text = decision.read_text(encoding="utf-8").lower() if decision.exists() else ""
    if "pending implementation decisions" in decision_text:
        print("- PASS [decision] implementation decisions remain pending")
    else:
        print("- FAIL [decision] pending decision marker missing")
        failures.append("pending decision marker missing")
    checklist = REPO_ROOT / "docs/release/backend_data_retention_decision_checklist.md"
    if checklist.exists():
        text = checklist.read_text(encoding="utf-8").lower()
        if "default: no" in text and "default: yes" in text:
            print("- PASS [retention] default retention/destructive-decision safeguards present")
        else:
            print("- FAIL [retention] default safeguards missing")
            failures.append("retention default safeguards missing")
    for path in [decision, checklist, REPO_ROOT / "docs/release/backend_deletion_candidate_inventory.md"]:
        for phrase in _contains_forbidden_phrase(path):
            print(f"- FAIL [phrase] {path.relative_to(REPO_ROOT)} contains forbidden phrase {phrase!r}")
            failures.append(f"forbidden phrase {phrase!r}")
        if path.exists():
            print(f"- PASS [phrase] {path.relative_to(REPO_ROOT)}: no forbidden approval phrase detected")
    inventory = REPO_ROOT / "docs/release/backend_deletion_candidate_inventory.md"
    if inventory.exists():
        text = inventory.read_text(encoding="utf-8").lower()
        if "| todo | no |" in text:
            print("- PASS [inventory] candidates default to not approved")
        else:
            print("- WARN [inventory] no default unapproved candidate rows detected")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS backend consolidation no-op/deletion guard")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
