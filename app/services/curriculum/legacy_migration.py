"""Gate 2R.8 legacy migration and disposition controls."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable


LEGACY_MIGRATION_POLICY_VERSION = "phase02r-gate2r8-legacy-migration-v1"
ALLOWED_DISPOSITIONS = {
    "grounded_verified",
    "quarantine_requires_review",
    "retire_legacy_ungrounded",
    "synthetic_fixture_excluded",
}


class LegacyDispositionError(ValueError):
    """Raised when a legacy artifact cannot be classified safely."""


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LegacyArtifactView:
    artifact_id: str
    artifact_type: str
    published: bool
    source_snapshot_hash: str | None
    source_chunk_ids: tuple[str, ...] = field(default_factory=tuple)
    answer_key_verified: bool | None = None
    generation_policy_version: str | None = None
    tutor_grounding_trace_id: str | None = None
    synthetic_fixture: bool = False
    learner_serving_reference: str | None = None

    def normalized(self) -> "LegacyArtifactView":
        if not self.artifact_id or not self.artifact_type:
            raise LegacyDispositionError("artifact_id and artifact_type are required")
        return LegacyArtifactView(
            artifact_id=self.artifact_id.strip(),
            artifact_type=self.artifact_type.strip(),
            published=bool(self.published),
            source_snapshot_hash=(self.source_snapshot_hash or None),
            source_chunk_ids=tuple(self.source_chunk_ids),
            answer_key_verified=self.answer_key_verified,
            generation_policy_version=self.generation_policy_version,
            tutor_grounding_trace_id=self.tutor_grounding_trace_id,
            synthetic_fixture=bool(self.synthetic_fixture),
            learner_serving_reference=self.learner_serving_reference,
        )


@dataclass(frozen=True)
class LegacyDispositionDecision:
    artifact_id: str
    artifact_type: str
    disposition: str
    learner_serving_allowed: bool
    requires_human_review: bool
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class LegacyMigrationClassifier:
    """Classifies legacy artifacts without migrating or publishing them."""

    def classify(self, artifact: LegacyArtifactView) -> LegacyDispositionDecision:
        item = artifact.normalized()
        if item.synthetic_fixture:
            return LegacyDispositionDecision(
                item.artifact_id,
                item.artifact_type,
                "synthetic_fixture_excluded",
                False,
                False,
                "Synthetic fixture is excluded from production serving and audit closure.",
            )

        grounded = bool(item.source_snapshot_hash and item.source_chunk_ids)
        answer_verified = item.answer_key_verified is True or item.artifact_type not in {
            "assessment_item",
            "diagnostic_item",
            "quiz_item",
        }
        generation_tag_ok = item.generation_policy_version in {
            None,
            "phase02r-gate2r6-generation-v1",
        }
        tutor_tag_ok = item.tutor_grounding_trace_id is None or item.tutor_grounding_trace_id.startswith("tutor-trace-")

        if grounded and answer_verified and generation_tag_ok and tutor_tag_ok:
            return LegacyDispositionDecision(
                item.artifact_id,
                item.artifact_type,
                "grounded_verified",
                True,
                False,
                "Artifact has Phase 02R source grounding and required answer/provenance verification.",
            )

        if item.published:
            return LegacyDispositionDecision(
                item.artifact_id,
                item.artifact_type,
                "quarantine_requires_review",
                False,
                True,
                "Published legacy artifact is not fully Phase 02R verified and must be quarantined pending review.",
            )

        return LegacyDispositionDecision(
            item.artifact_id,
            item.artifact_type,
            "retire_legacy_ungrounded",
            False,
            False,
            "Unpublished legacy artifact lacks complete Phase 02R provenance and is retired from learner serving.",
        )

    def build_manifest(self, artifacts: Iterable[LegacyArtifactView]) -> dict[str, Any]:
        decisions = [self.classify(artifact) for artifact in artifacts]
        if not decisions:
            raise LegacyDispositionError("legacy migration manifest requires at least one artifact")
        dispositions = Counter(decision.disposition for decision in decisions)
        if set(dispositions) - ALLOWED_DISPOSITIONS:
            raise LegacyDispositionError("unknown disposition emitted")
        payload = {
            "gate": "2R.8",
            "policy_version": LEGACY_MIGRATION_POLICY_VERSION,
            "status": "ready_for_review",
            "summary": dict(sorted(dispositions.items())),
            "artifact_count": len(decisions),
            "learner_serving_allowed_count": sum(1 for decision in decisions if decision.learner_serving_allowed),
            "requires_human_review_count": sum(1 for decision in decisions if decision.requires_human_review),
            "decisions": [decision.as_dict() for decision in sorted(decisions, key=lambda item: item.artifact_id)],
            "gate_boundary": {
                "migration_executed": False,
                "production_activation_performed": False,
                "phase_02r_completion_declared": False,
            },
        }
        payload["manifest_sha256"] = sha256_json(payload)
        return payload


def build_gate2r8_legacy_fixture_artifacts() -> tuple[LegacyArtifactView, ...]:
    return (
        LegacyArtifactView(
            artifact_id="lesson-g4math-place-value-v1",
            artifact_type="lesson",
            published=True,
            source_snapshot_hash="source-snapshot-001",
            source_chunk_ids=("chunk-g4math-numbers_operations_relationships-00",),
            generation_policy_version="phase02r-gate2r6-generation-v1",
        ),
        LegacyArtifactView(
            artifact_id="assessment-g4math-place-value-v1",
            artifact_type="assessment_item",
            published=True,
            source_snapshot_hash="source-snapshot-001",
            source_chunk_ids=("chunk-g4math-numbers_operations_relationships-00",),
            answer_key_verified=True,
            generation_policy_version="phase02r-gate2r6-generation-v1",
        ),
        LegacyArtifactView(
            artifact_id="legacy-published-ungrounded-001",
            artifact_type="lesson",
            published=True,
            source_snapshot_hash=None,
            source_chunk_ids=(),
        ),
        LegacyArtifactView(
            artifact_id="legacy-draft-ungrounded-001",
            artifact_type="lesson",
            published=False,
            source_snapshot_hash=None,
            source_chunk_ids=(),
        ),
        LegacyArtifactView(
            artifact_id="fixture-synthetic-demo-001",
            artifact_type="lesson",
            published=False,
            source_snapshot_hash="fixture-source",
            source_chunk_ids=("fixture-chunk",),
            synthetic_fixture=True,
        ),
    )


def build_gate2r8_legacy_migration_manifest() -> dict[str, Any]:
    return LegacyMigrationClassifier().build_manifest(build_gate2r8_legacy_fixture_artifacts())


__all__ = [
    "ALLOWED_DISPOSITIONS",
    "LEGACY_MIGRATION_POLICY_VERSION",
    "LegacyArtifactView",
    "LegacyDispositionDecision",
    "LegacyDispositionError",
    "LegacyMigrationClassifier",
    "build_gate2r8_legacy_fixture_artifacts",
    "build_gate2r8_legacy_migration_manifest",
    "sha256_json",
]
