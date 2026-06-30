#!/usr/bin/env python3
"""Verify Phase 02I topic-map provenance remediation contracts."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.curriculum.build_topic_map_worklist import build_worklist

TEXT_EXTRACT_MANIFEST = ROOT / "data" / "content_factory" / "source_text_extracts_manifest.json"
EXPECTED_SCOPE_ID = "grade7_mathematics_en"
EXPECTED_DOCUMENT_ID = "caps_senior_mathematics_en"
EXPECTED_SOURCE_SHA256 = "64dcd19ee1d67109ff4172d9b098259954a2e77a55aeae0d11ee7ec033b0d8f8"
EXPECTED_TEXT_SHA256 = "881f88f60186856703767333a0c3f2331b8aeebb52dd11fcf46c2f25c90d3c33"
EXPECTED_TEXT_PATH = "data/caps/source_documents/text/caps_senior_mathematics_en.txt"
EXPECTED_OBJECT_URI = (
    "https://eduboostcaps06022047.blob.core.windows.net/caps-sources/"
    "senior/mathematics/en/caps_senior_mathematics_en-64dcd19ee1d67109.pdf"
)


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _load_manifest() -> dict[str, Any]:
    if not TEXT_EXTRACT_MANIFEST.exists():
        return {}
    return json.loads(TEXT_EXTRACT_MANIFEST.read_text(encoding="utf-8"))


def run_checks(*, static_only: bool = False) -> dict[str, Any]:
    checks: list[Check] = []
    manifest = _load_manifest()
    records = manifest.get("records", []) if isinstance(manifest, dict) else []
    senior_math_records = [record for record in records if record.get("document_id") == EXPECTED_DOCUMENT_ID]

    checks.append(Check(
        "text_extract_manifest_exists",
        TEXT_EXTRACT_MANIFEST.exists(),
        f"{TEXT_EXTRACT_MANIFEST.relative_to(ROOT)} exists",
    ))
    checks.append(Check(
        "senior_mathematics_record_present",
        len(senior_math_records) == 1,
        "Exactly one caps_senior_mathematics_en text-extract provenance record is tracked.",
    ))
    if senior_math_records:
        record = senior_math_records[0]
        checks.append(Check(
            "senior_mathematics_text_hash",
            record.get("text_sha256") == EXPECTED_TEXT_SHA256,
            "Senior Phase Mathematics text-extract SHA-256 matches the reviewed provenance contract.",
        ))
        checks.append(Check(
            "senior_mathematics_source_hash",
            record.get("source_sha256") == EXPECTED_SOURCE_SHA256,
            "Text-extract provenance remains bound to the immutable PDF source hash.",
        ))
        checks.append(Check(
            "senior_mathematics_text_path",
            record.get("text_extract_path") == EXPECTED_TEXT_PATH,
            "Text-extract path is stable and clean-checkout safe as metadata.",
        ))
        checks.append(Check(
            "phase02i_scope_binding",
            EXPECTED_SCOPE_ID in set(record.get("scope_ids", [])),
            "Text-extract provenance is explicitly linked to the Grade 7 Mathematics scope.",
        ))

    if not static_only:
        worklist = build_worklist()
        grade7_math = next((item for item in worklist["items"] if item["scope_id"] == EXPECTED_SCOPE_ID), None)
        checks.append(Check(
            "worklist_scope_present",
            grade7_math is not None,
            "Grade 7 Mathematics is present in the topic-map worklist.",
        ))
        if grade7_math is not None:
            checks.extend([
                Check(
                    "worklist_source_document_id",
                    grade7_math.get("source_document_ids") == [EXPECTED_DOCUMENT_ID],
                    "Grade 7 Mathematics keeps the Senior Phase Mathematics source document binding.",
                ),
                Check(
                    "worklist_source_sha256",
                    grade7_math.get("source_sha256") == [EXPECTED_SOURCE_SHA256],
                    "Worklist preserves immutable source PDF hash.",
                ),
                Check(
                    "worklist_text_sha256",
                    grade7_math.get("text_sha256") == [EXPECTED_TEXT_SHA256],
                    "Worklist preserves reviewed text-extract hash instead of falling back to the PDF hash.",
                ),
                Check(
                    "worklist_text_extract_path",
                    grade7_math.get("text_extract_paths") == [EXPECTED_TEXT_PATH],
                    "Worklist exposes the reviewed text-extract path metadata.",
                ),
                Check(
                    "worklist_object_store_uri",
                    grade7_math.get("object_store_uris") == [EXPECTED_OBJECT_URI],
                    "Worklist preserves the object-store source URI.",
                ),
                Check(
                    "worklist_no_outstanding_tasks",
                    grade7_math.get("outstanding_tasks") == [],
                    "Grade 7 Mathematics remains generation-ready with no topic-map worklist tasks.",
                ),
                Check(
                    "worklist_generation_ready",
                    grade7_math.get("generation_ready") is True,
                    "Grade 7 Mathematics remains generation-ready but not learner-visible active scope.",
                ),
            ])

    payload = {
        "phase": "02I",
        "slice": "topic-map-provenance-final-backend-fast-repair",
        "checks": [asdict(check) for check in checks],
        "valid": all(check.passed for check in checks),
        "policy": "Phase 02I focused evidence only; backend-fast candidate evidence requires make test-fast exit 0.",
        "kg_boundary": "No runtime knowledge-graph implementation is included; KG remains a future architectural north star.",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--static-only", action="store_true", help="Validate static files without building the worklist.")
    args = parser.parse_args()
    payload = run_checks(static_only=args.static_only)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Backend Fast Phase 02I verification")
        for check in payload["checks"]:
            marker = "PASS" if check["passed"] else "FAIL"
            print(f"  [{marker}] {check['name']}: {check['detail']}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
