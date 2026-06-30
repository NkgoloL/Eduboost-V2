"""Risk scoring for Content Factory human review prioritization."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.models.content_factory import ContentGenerationArtifact


@dataclass(frozen=True)
class ReviewRisk:
    level: str
    score: int
    reasons: list[str] = field(default_factory=list)


class ContentReviewRiskService:
    def score_artifact(
        self,
        artifact: ContentGenerationArtifact,
        *,
        validation_report: Any | None = None,
        provenance_report: Any | None = None,
        prior_approved_count: int = 0,
        duplicate_count: int = 0,
    ) -> ReviewRisk:
        score = 0
        reasons: list[str] = []

        if provenance_report is not None and not bool(getattr(provenance_report, "passed", False)):
            score += 100
            reasons.append("invalid_provenance")
        elif not getattr(artifact, "source_snapshot_hash", None):
            score += 100
            reasons.append("missing_provenance")

        sources = list(getattr(artifact, "sources", []) or [])
        if not sources:
            score += 60
            reasons.append("missing_sources")
        for source in sources:
            quality = getattr(source, "source_quality_score", None)
            if quality is not None and float(quality) < 0.5:
                score += 35
                reasons.append("low_source_quality")
                break

        if validation_report is not None:
            if not bool(getattr(validation_report, "passed", False)):
                score += 60
                reasons.append("validation_failed")
            errors = getattr(validation_report, "errors", []) or []
            if errors:
                score += min(30, 10 * len(errors))
                reasons.append("validation_warnings")

        provider = str(getattr(artifact, "provider", "") or "").lower()
        if provider and provider != "deterministic":
            score += 20
            reasons.append("non_deterministic_provider")

        difficulty = str((getattr(artifact, "artifact_json", {}) or {}).get("difficulty") or "").lower()
        if difficulty in {"hard", "advanced", "high"}:
            score += 20
            reasons.append("high_difficulty")

        confidence = (getattr(artifact, "artifact_json", {}) or {}).get("answer_key_confidence")
        if confidence is not None and float(confidence) < 0.75:
            score += 25
            reasons.append("low_confidence_answer_key")

        if duplicate_count:
            score += 30
            reasons.append("duplicate_similarity")

        if prior_approved_count == 0:
            score += 10
            reasons.append("new_caps_ref")

        for source in sources:
            metadata = getattr(source, "source_metadata", {}) or {}
            if str(metadata.get("document_status") or "").lower() in {"stale", "deprecated", "archived"}:
                score += 50
                reasons.append("stale_source_document")
                break

        if score >= 90:
            level = "critical"
        elif score >= 50:
            level = "high"
        elif score >= 20:
            level = "medium"
        else:
            level = "low"
        return ReviewRisk(level=level, score=score, reasons=sorted(set(reasons)))
