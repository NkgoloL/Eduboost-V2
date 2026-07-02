from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_remediation.verify_backend_fast_phase02j import run_checks
from scripts.curriculum.build_topic_map_worklist import build_worklist

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "data" / "content_factory" / "source_text_extracts_manifest.json"
EXPECTED_TEXT_PATH = "data/caps/source_documents/text/caps_senior_mathematics_en.txt"
EXPECTED_TEXT_SHA = "881f88f60186856703767333a0c3f2331b8aeebb52dd11fcf46c2f25c90d3c33"


def test_phase02j_verifier_passes() -> None:
    payload = run_checks()
    assert payload["valid"] is True
    assert {check["name"] for check in payload["checks"]} >= {
        "gitignore_allows_manifest",
        "manifest_not_gitignored",
        "manifest_exists",
        "worklist_text_hash",
        "worklist_text_path",
    }


def test_source_text_manifest_is_trackable_by_gitignore_contract() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/content_factory/*" in gitignore
    assert "!data/content_factory/source_text_extracts_manifest.json" in gitignore
    assert MANIFEST.exists()


def test_source_text_manifest_records_clean_checkout_path() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    record = next(entry for entry in payload["records"] if entry["document_id"] == "caps_senior_mathematics_en")

    assert record["scope_ids"] == ["grade7_mathematics_en"]
    assert record["text_extract_path"] == EXPECTED_TEXT_PATH
    assert record["text_sha256"] == EXPECTED_TEXT_SHA


def test_worklist_uses_tracked_text_extract_manifest() -> None:
    worklist = build_worklist()
    grade7_math = next(item for item in worklist["items"] if item["scope_id"] == "grade7_mathematics_en")

    assert grade7_math["text_extract_paths"] == [EXPECTED_TEXT_PATH]
    assert grade7_math["text_sha256"] == [EXPECTED_TEXT_SHA]
