from __future__ import annotations

from types import SimpleNamespace

from app.services.content_review_risk import ContentReviewRiskService


def _artifact(**kwargs):
    data = {
        "source_snapshot_hash": "snap",
        "sources": [SimpleNamespace(source_quality_score=0.9, source_metadata={"document_status": "approved"})],
        "provider": "deterministic",
        "artifact_json": {"difficulty": "easy", "answer_key_confidence": 0.95},
    }
    data.update(kwargs)
    return SimpleNamespace(**data)


def test_risk_scorer_marks_invalid_provenance_as_critical() -> None:
    risk = ContentReviewRiskService().score_artifact(_artifact(), provenance_report=SimpleNamespace(passed=False), validation_report=SimpleNamespace(passed=True, errors=[]), prior_approved_count=1)

    assert risk.level == "critical"
    assert "invalid_provenance" in risk.reasons


def test_risk_scorer_marks_clean_deterministic_artifacts_as_low() -> None:
    risk = ContentReviewRiskService().score_artifact(_artifact(), provenance_report=SimpleNamespace(passed=True), validation_report=SimpleNamespace(passed=True, errors=[]), prior_approved_count=1)

    assert risk.level == "low"
    assert risk.reasons == []
