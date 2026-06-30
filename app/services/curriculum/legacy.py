"""Legacy-artifact disposition helpers for Phase 2R Gate 2R.8."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


class LegacyDispositionError(ValueError):
    pass


@dataclass(frozen=True)
class LegacyArtifactView:
    artifact_id: str
    artifact_type: str
    published: bool
    source_snapshot_hash: str | None
    source_chunk_ids: list[str]
    answer_key_verified: bool | None = None
    synthetic_fixture: bool = False


@dataclass(frozen=True)
class LegacyDispositionDecision:
    artifact_id: str
    disposition: str
    learner_serving_allowed: bool
    rationale: str


class LegacyMigrationClassifier:
    def classify(self, artifact: LegacyArtifactView) -> LegacyDispositionDecision:
        if artifact.synthetic_fixture:
            return LegacyDispositionDecision(artifact.artifact_id, "synthetic_fixture", False, "Synthetic fixture excluded from production serving")
        grounded = bool(artifact.source_snapshot_hash and artifact.source_chunk_ids)
        verified = artifact.answer_key_verified is True or artifact.artifact_type != "diagnostic_item"
        if grounded and verified:
            return LegacyDispositionDecision(artifact.artifact_id, "grounded_verified", True, "Artifact has source grounding and required verification")
        if grounded and not verified:
            return LegacyDispositionDecision(artifact.artifact_id, "grounded_unverified", False, "Artifact is grounded but answer verification is incomplete")
        if artifact.published:
            return LegacyDispositionDecision(artifact.artifact_id, "published_requires_review", False, "Published legacy artifact lacks Phase 2R provenance")
        return LegacyDispositionDecision(artifact.artifact_id, "legacy_ungrounded", False, "Artifact lacks Phase 2R grounding provenance")

    def summarize(self, artifacts: list[LegacyArtifactView]) -> dict[str, int]:
        decisions = [self.classify(artifact).disposition for artifact in artifacts]
        return dict(Counter(decisions))
