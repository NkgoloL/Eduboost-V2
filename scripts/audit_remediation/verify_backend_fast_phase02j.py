#!/usr/bin/env python3
"""Verify Phase 02J tracked topic-map text-extract provenance contracts."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.curriculum.build_topic_map_worklist import build_worklist

MANIFEST = ROOT / "data" / "content_factory" / "source_text_extracts_manifest.json"
GITIGNORE = ROOT / ".gitignore"
EXPECTED_DOC = "caps_senior_mathematics_en"
EXPECTED_SCOPE = "grade7_mathematics_en"
EXPECTED_SOURCE_SHA = "64dcd19ee1d67109ff4172d9b098259954a2e77a55aeae0d11ee7ec033b0d8f8"
EXPECTED_TEXT_SHA = "881f88f60186856703767333a0c3f2331b8aeebb52dd11fcf46c2f25c90d3c33"
EXPECTED_TEXT_PATH = "data/caps/source_documents/text/caps_senior_mathematics_en.txt"
UNIGNORE_LINE = "!data/content_factory/source_text_extracts_manifest.json"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _load_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        return {}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _git_check_not_ignored() -> tuple[bool, str]:
    if not (ROOT / ".git").exists():
        return True, "No .git directory available; .gitignore allowlist is checked statically."
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(MANIFEST.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    )
    if result.returncode == 0:
        return False, "git check-ignore reports source_text_extracts_manifest.json is still ignored."
    if result.returncode == 1:
        return True, "git check-ignore reports source_text_extracts_manifest.json is trackable."
    return False, f"git check-ignore returned unexpected code {result.returncode}."


def run_checks(*, static_only: bool = False) -> dict[str, Any]:
    checks: list[Check] = []
    gitignore_text = GITIGNORE.read_text(encoding="utf-8") if GITIGNORE.exists() else ""
    manifest = _load_manifest()
    records = manifest.get("records", []) if isinstance(manifest, dict) else []
    expected_records = [record for record in records if record.get("document_id") == EXPECTED_DOC]

    checks.append(Check("gitignore_allows_manifest", UNIGNORE_LINE in gitignore_text, "The source-text manifest is explicitly unignored for clean-checkout tracking."))
    not_ignored, not_ignored_detail = _git_check_not_ignored()
    checks.append(Check("manifest_not_gitignored", not_ignored, not_ignored_detail))
    checks.append(Check("manifest_exists", MANIFEST.exists(), f"{MANIFEST.relative_to(ROOT)} exists in the tracked tree."))
    checks.append(Check("manifest_single_senior_math_record", len(expected_records) == 1, "Exactly one Senior Phase Mathematics text-extract provenance record is present."))
    if expected_records:
        record = expected_records[0]
        checks.extend([
            Check("manifest_scope_binding", EXPECTED_SCOPE in set(record.get("scope_ids", [])), "The record is bound to grade7_mathematics_en."),
            Check("manifest_source_hash", record.get("source_sha256") == EXPECTED_SOURCE_SHA, "The record preserves the immutable PDF source SHA-256."),
            Check("manifest_text_hash", record.get("text_sha256") == EXPECTED_TEXT_SHA, "The record preserves the reviewed text-extract SHA-256."),
            Check("manifest_text_path", record.get("text_extract_path") == EXPECTED_TEXT_PATH, "The record uses the clean-checkout CAPS source text path."),
        ])
    if not static_only:
        worklist = build_worklist()
        item = next((entry for entry in worklist["items"] if entry.get("scope_id") == EXPECTED_SCOPE), None)
        checks.append(Check("worklist_item_present", item is not None, "Grade 7 Mathematics is present in the generated worklist."))
        if item:
            checks.extend([
                Check("worklist_text_hash", item.get("text_sha256") == [EXPECTED_TEXT_SHA], "Worklist uses reviewed text-extract hash, not the PDF hash fallback."),
                Check("worklist_text_path", item.get("text_extract_paths") == [EXPECTED_TEXT_PATH], "Worklist uses the clean-checkout CAPS text path."),
                Check("worklist_source_hash", item.get("source_sha256") == [EXPECTED_SOURCE_SHA], "Worklist still preserves the immutable PDF source hash separately."),
            ])
    return {
        "phase": "02J",
        "slice": "tracked-topic-map-text-extract-provenance",
        "checks": [asdict(check) for check in checks],
        "valid": all(check.passed for check in checks),
        "policy": "Phase 02J focused evidence only; backend-fast candidate evidence requires make test-fast exit 0.",
        "kg_boundary": "No runtime knowledge-graph implementation is included; KG remains a future architectural north star.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    payload = run_checks(static_only=args.static_only)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for check in payload["checks"]:
            print(f"{'PASS' if check['passed'] else 'FAIL'} {check['name']}: {check['detail']}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
