"""Strict Pydantic v2 schemas for Educational Validation (LEV-WS01, LEV-WS03, LEV-WS15).

Provides type-safe models for interaction telemetry, mastery state transitions,
cryptographic evidence manifests, model snapshots, and use authorizations.
Enforces evidence_type discrimination: "synthetic_fixture" vs "empirical_field".
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


EvidenceType = Literal["synthetic_fixture", "empirical_field"]
UseAuthorizationStatus = Literal[
    "unsupported",
    "research_only",
    "shadow_only",
    "restricted",
    "authorised",
    "suspended",
    "expired",
]
DecisionScope = Literal[
    "low_stakes_practice",
    "formative_hinting",
    "diagnostic_remediation",
    "formal_grading",
    "grade_progression",
    "high_stakes_streaming",
]

# Educational validity rule: maximum confidence cap prior to longitudinal sign-off
MAX_CONFIDENCE_THRESHOLD = 0.60


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class InteractionEventSchema(StrictModel):
    event_id: str
    occurred_at: datetime
    learner_pseudonym: str
    concept_id: str
    item_id: str
    item_version: str = "1.0"
    graph_version: str = "1.0.0"
    model_version: str = "lev-1.0"
    consent_state: str = "consented"
    first_attempt_correct: Optional[bool] = None
    attempt_count: int = Field(default=1, ge=0)
    hint_count: int = Field(default=0, ge=0)
    response_latency_ms: Optional[int] = Field(default=None, ge=0)
    teacher_assistance: bool = False
    evidence_type: EvidenceType = "synthetic_fixture"


class MasteryStatePayload(StrictModel):
    mastery_level: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("confidence")
    @classmethod
    def cap_confidence(cls, v: float) -> float:
        if v > MAX_CONFIDENCE_THRESHOLD:
            # Enforce mathematical bound on algorithmic confidence
            return MAX_CONFIDENCE_THRESHOLD
        return v


class MasteryStateTransitionSchema(StrictModel):
    transition_id: str
    learner_pseudonym: str
    concept_id: str
    occurred_at: datetime
    pre_state: Dict[str, Any]
    post_state: Dict[str, Any]
    evidence_event_ids: List[str] = Field(min_length=1)
    model_version: str = "lev-1.0"
    graph_version: str = "1.0.0"
    update_rationale: str = ""
    state_hash: Optional[str] = None
    evidence_type: EvidenceType = "synthetic_fixture"


class EvidenceFileEntry(StrictModel):
    path: str
    sha256: str = Field(min_length=64, max_length=64)


class EvidenceManifestSchema(StrictModel):
    manifest_id: str
    task_ids: List[str]
    created_at: datetime
    files: List[EvidenceFileEntry]
    approvals: List[str]
    evidence_type: EvidenceType = "synthetic_fixture"


class ModelSnapshotSchema(StrictModel):
    model_id: str
    version: str
    code_commit: str
    training_data_manifest: str
    feature_manifest: str
    authorised_population: List[str]
    authorised_uses: List[str]
    prohibited_uses: List[str]
    valid_until: str


class UseAuthorizationSchema(StrictModel):
    use_id: str
    status: UseAuthorizationStatus
    model_versions: List[str]
    population: Dict[str, Any]
    content_scope: Dict[str, Any]
    decision_scope: List[str]
    limitations: List[str]
    expires_at: str


class MasteryClaimDefinition(StrictModel):
    claim_id: str
    concept_id: str
    construct_name: str
    description: str
    prerequisite_concept_ids: List[str] = Field(default_factory=list)
    mastery_threshold: float = Field(default=0.75, ge=0.5, le=1.0)
    max_confidence_threshold: float = Field(default=MAX_CONFIDENCE_THRESHOLD)
    authorized_decision_scopes: List[DecisionScope] = Field(
        default_factory=lambda: ["low_stakes_practice", "formative_hinting", "diagnostic_remediation"]
    )
    prohibited_decision_scopes: List[DecisionScope] = Field(
        default_factory=lambda: ["formal_grading", "grade_progression", "high_stakes_streaming"]
    )
