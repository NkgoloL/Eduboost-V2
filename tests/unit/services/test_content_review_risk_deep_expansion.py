"""Comprehensive unit tests for ContentReviewRiskService scoring and risk levels."""
from __future__ import annotations

from types import SimpleNamespace
import pytest

from app.services.content_review_risk import (
    ReviewRisk,
    ContentReviewRiskService,
)


class TestContentReviewRiskService:
    def test_review_risk_dataclass(self):
        risk = ReviewRisk(
            level="critical",
            score=120,
            reasons=["missing_provenance", "validation_failed"],
        )
        assert risk.level == "critical"
        assert risk.score == 120
        assert len(risk.reasons) == 2

    def test_score_clean_deterministic_artifact(self):
        service = ContentReviewRiskService()
        source = SimpleNamespace(
            source_quality_score=0.95,
            source_metadata={"license_status": "cc-by"},
            license_status="cc-by",
        )
        artifact = SimpleNamespace(
            source_snapshot_hash="hash-1234",
            sources=[source],
            provider="deterministic",
            artifact_json={"difficulty": "medium", "answer_key_confidence": 0.99},
        )
        val_report = SimpleNamespace(passed=True, errors=[])
        prov_report = SimpleNamespace(passed=True)

        risk = service.score_artifact(
            artifact,
            validation_report=val_report,
            provenance_report=prov_report,
            prior_approved_count=10,
            duplicate_count=0,
        )
        assert risk.score < 50
        assert "invalid_provenance" not in risk.reasons

    def test_score_high_risk_missing_provenance_artifact(self):
        service = ContentReviewRiskService()
        artifact = SimpleNamespace(
            source_snapshot_hash=None,
            sources=[],
            provider="groq",
            artifact_json={"difficulty": "hard", "answer_key_confidence": 0.50},
        )
        val_report = SimpleNamespace(passed=False, errors=["Schema validation failed"])

        risk = service.score_artifact(
            artifact,
            validation_report=val_report,
            provenance_report=None,
            prior_approved_count=0,
            duplicate_count=2,
        )
        assert risk.score >= 100
        assert "missing_provenance" in risk.reasons
        assert "validation_failed" in risk.reasons
        assert "high_difficulty" in risk.reasons
