from __future__ import annotations

from scripts.true_state_remediation.core import (
    record_manual_evidence,
    require_reviewed_artifact,
)


def test_reviewed_artifact_fails_closed_for_missing_mismatched_and_matching_records(tmp_path):
    artifact = tmp_path / "contract.json"
    artifact.write_text('{"state": "reviewed"}', encoding="utf-8")

    missing = require_reviewed_artifact(tmp_path, "B01", "PRD-11.TEST", artifact)
    assert missing["valid"] is False
    assert missing["missing"] == ["PRD-11.TEST"]

    record_manual_evidence(
        tmp_path,
        "B01",
        "PRD-11.TEST",
        reviewer="Test Reviewer",
        reviewer_role="independent reviewer",
        decision="approved",
        artifact_path="contract.json",
    )
    matching = require_reviewed_artifact(tmp_path, "B01", "PRD-11.TEST", artifact)
    assert matching["valid"] is True

    artifact.write_text('{"state": "changed-after-review"}', encoding="utf-8")
    mismatched = require_reviewed_artifact(tmp_path, "B01", "PRD-11.TEST", artifact)
    assert mismatched["valid"] is False
    assert any("digest mismatch" in item for item in mismatched["invalid"])
