from __future__ import annotations

import pytest

from scripts.audit_remediation.verify_backend_fast_phase02i import run_checks
from scripts.curriculum.build_topic_map_worklist import build_worklist


pytestmark = pytest.mark.unit


def test_phase02i_verifier_reports_valid_topic_map_provenance() -> None:
    payload = run_checks()

    assert payload["valid"] is True
    assert {check["name"] for check in payload["checks"]} >= {
        "senior_mathematics_text_hash",
        "worklist_text_sha256",
        "worklist_text_extract_path",
        "worklist_no_outstanding_tasks",
    }


def test_grade7_mathematics_worklist_uses_reviewed_text_extract_hash() -> None:
    worklist = build_worklist()
    grade7_math = next(item for item in worklist["items"] if item["scope_id"] == "grade7_mathematics_en")

    assert grade7_math["source_sha256"] == ["64dcd19ee1d67109ff4172d9b098259954a2e77a55aeae0d11ee7ec033b0d8f8"]
    assert grade7_math["text_sha256"] == ["881f88f60186856703767333a0c3f2331b8aeebb52dd11fcf46c2f25c90d3c33"]
    assert grade7_math["text_sha256"] != grade7_math["source_sha256"]
    assert grade7_math["text_extract_paths"] == ["data/caps/source_documents/text/caps_senior_mathematics_en.txt"]
