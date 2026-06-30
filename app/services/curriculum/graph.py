"""Phase 02R Gate 2R.4 curriculum graph and reviewed mapping controls.

This module is deliberately self-contained and deterministic.  It models the
Gate 2R.4 control layer only: curriculum node versions, reviewed edges,
source-to-curriculum mapping proposals, review events, Tier 1 support readiness,
language authority labels, and stable graph exports.  It does **not** activate a
corpus, rebuild retrieval projections, create embeddings, or alter learner-facing
behaviour.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Iterable, Mapping, Sequence


class Gate2R4ValidationError(ValueError):
    """Raised when a Gate 2R.4 graph or mapping rule is violated."""


class MappingRejectedError(Gate2R4ValidationError):
    """Backward-compatible error used by existing Phase 02R verifiers."""


class ReviewStatus(StrEnum):
    PROPOSED = "proposed"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class NodeStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class EdgeType(StrEnum):
    PREREQUISITE_OF = "prerequisite_of"
    SEQUENCE_BEFORE = "sequence_before"
    SUPPORTS = "supports"
    ASSESSES = "assesses"
    SAME_CONCEPT_AS = "same_concept_as"
    TRANSLATION_OF = "translation_of"


class LanguageAuthorityStatus(StrEnum):
    OFFICIAL_SOURCE = "official_source"
    APPROVED_HUMAN_TRANSLATION = "approved_human_translation"
    MACHINE_TRANSLATION_DRAFT = "machine_translation_draft"
    GENERATED_LEARNER_EXPLANATION = "generated_learner_explanation"


class SupportType(StrEnum):
    DIRECT_SUPPORT = "direct_support"
    EXAMPLE = "example"
    ASSESSMENT_EVIDENCE = "assessment_evidence"
    TEACHING_GUIDANCE = "teaching_guidance"
    BACKGROUND_CONTEXT = "background_context"


NODE_TYPES = frozenset(
    {
        "curriculum",
        "phase",
        "grade",
        "subject",
        "term",
        "strand",
        "topic",
        "subtopic",
        "skill",
        "learning_objective",
        "assessment_requirement",
        "assessment_statement",
        "prerequisite",
        "vocabulary",
    }
)

# Existing Gate 2R.2-2R.8 static verifier imported uppercase relationship names.
LEGACY_RELATIONSHIP_TYPES = frozenset(
    {
        "CONTAINS",
        "REQUIRES",
        "PRECEDES",
        "DEPENDS_ON",
        "ASSESSED_BY",
        "EXEMPLIFIED_BY",
        "DEFINED_IN",
        "AMENDED_BY",
        "SUPERSEDES",
        "TRANSLATION_OF",
    }
)

ALLOWED_LANGUAGES = frozenset({"en", "af", "nso", "zu", "xh"})
AUTHORITY_TIERS = frozenset({"tier_1", "tier_2", "tier_3"})
CORPUS_ELIGIBLE_REVIEW_STATUS = frozenset({ReviewStatus.APPROVED.value})
APPEND_ONLY_REVIEW_EVENT_TYPES = frozenset(
    {
        "proposed",
        "moved_to_review",
        "approved",
        "rejected",
        "needs_revision",
        "withdrawn",
        "superseded",
        "single_developer_exception_recorded",
    }
)


@dataclass(frozen=True)
class GraphNodeDraft:
    """Backward-compatible node draft used by older Phase 02R verifiers."""

    node_type: str
    code: str
    label: str
    curriculum: str = "CAPS"
    grade: int | None = 4
    subject: str | None = "Mathematics"
    language: str | None = "en"
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.node_type not in NODE_TYPES:
            raise MappingRejectedError(f"invalid node_type: {self.node_type}")
        if self.language is not None and self.language not in ALLOWED_LANGUAGES:
            raise MappingRejectedError(f"invalid language: {self.language}")
        if self.grade is not None and not (0 <= self.grade <= 12):
            raise MappingRejectedError("grade must be between 0 and 12")
        if not self.code.strip() or not self.label.strip():
            raise MappingRejectedError("node code and label are required")


@dataclass(frozen=True)
class MappingDraft:
    """Backward-compatible mapping draft used by older Phase 02R verifiers."""

    chunk_version_id: str
    node_id: str
    relationship_type: str
    proposal_method: str
    review_status: str
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    def validate_for_retrieval(self) -> None:
        if self.relationship_type not in LEGACY_RELATIONSHIP_TYPES and self.relationship_type not in {edge.value for edge in EdgeType}:
            raise MappingRejectedError(f"invalid relationship_type: {self.relationship_type}")
        if self.review_status != ReviewStatus.APPROVED.value:
            raise MappingRejectedError("mapping must be human-reviewed and approved")
        if not self.reviewed_by or not self.reviewed_at:
            raise MappingRejectedError("approved mapping requires reviewer metadata")


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _coerce_review_status(value: str | ReviewStatus) -> ReviewStatus:
    try:
        return value if isinstance(value, ReviewStatus) else ReviewStatus(value)
    except ValueError as exc:  # pragma: no cover - covered by caller validation tests
        raise Gate2R4ValidationError(f"invalid review_status: {value}") from exc


def _coerce_language_status(value: str | LanguageAuthorityStatus) -> LanguageAuthorityStatus:
    try:
        return value if isinstance(value, LanguageAuthorityStatus) else LanguageAuthorityStatus(value)
    except ValueError as exc:
        raise Gate2R4ValidationError(f"invalid language authority status: {value}") from exc


def _coerce_edge_type(value: str | EdgeType) -> EdgeType:
    try:
        return value if isinstance(value, EdgeType) else EdgeType(value)
    except ValueError as exc:
        raise Gate2R4ValidationError(f"invalid edge_type: {value}") from exc


@dataclass(frozen=True)
class CurriculumNodeVersion:
    curriculum_node_id: str
    curriculum_node_version_id: str
    curriculum_code: str
    grade: int
    subject_code: str
    strand: str
    term: str | None
    topic: str
    subtopic: str | None
    skill: str | None
    learning_objective: str
    assessment_statement: str | None
    language: str
    status: str = NodeStatus.DRAFT.value
    effective_from: str | None = None
    effective_to: str | None = None
    supersedes_version_id: str | None = None
    created_by: str = "system"
    created_at: str = field(default_factory=lambda: _now().isoformat())
    node_type: str = "learning_objective"
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.node_type not in NODE_TYPES:
            raise Gate2R4ValidationError(f"invalid node_type: {self.node_type}")
        if self.language not in ALLOWED_LANGUAGES:
            raise Gate2R4ValidationError(f"invalid language: {self.language}")
        if not 0 <= self.grade <= 12:
            raise Gate2R4ValidationError("grade must be between 0 and 12")
        if not self.curriculum_code.strip() or not self.subject_code.strip():
            raise Gate2R4ValidationError("curriculum_code and subject_code are required")
        if not self.strand.strip() or not self.topic.strip():
            raise Gate2R4ValidationError("strand and topic are required")
        if not self.learning_objective.strip():
            raise Gate2R4ValidationError("learning_objective is required")
        try:
            NodeStatus(self.status)
        except ValueError as exc:
            raise Gate2R4ValidationError(f"invalid node status: {self.status}") from exc
        if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
            raise Gate2R4ValidationError("effective_to cannot be before effective_from")
        if self.supersedes_version_id == self.curriculum_node_version_id:
            raise Gate2R4ValidationError("node version cannot supersede itself")

    @property
    def is_caps_requirement(self) -> bool:
        return self.curriculum_code.upper() == "CAPS" and self.node_type in {
            "learning_objective",
            "assessment_requirement",
            "assessment_statement",
        }

    @property
    def is_approved(self) -> bool:
        return self.status == NodeStatus.APPROVED.value

    def with_changes(self, **changes: Any) -> "CurriculumNodeVersion":
        """Return a changed copy unless this approved version is immutable."""
        if self.is_approved:
            raise Gate2R4ValidationError("approved curriculum node versions are immutable; create a superseding version")
        updated = replace(self, **changes)
        updated.validate()
        return updated

    def approved(self, *, effective_from: str, reviewer_id: str) -> "CurriculumNodeVersion":
        if not reviewer_id:
            raise Gate2R4ValidationError("reviewer_id is required to approve a node version")
        updated = replace(self, status=NodeStatus.APPROVED.value, effective_from=effective_from)
        updated.validate()
        return updated

    def export(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["metadata"] = dict(sorted(self.metadata.items()))
        return payload


@dataclass(frozen=True)
class CurriculumEdgeVersion:
    edge_version_id: str
    from_curriculum_node_version_id: str
    to_curriculum_node_version_id: str
    edge_type: str
    review_status: str = ReviewStatus.PROPOSED.value
    proposed_by: str = "system"
    proposed_at: str = field(default_factory=lambda: _now().isoformat())
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    review_notes: str | None = None
    supersedes_edge_version_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self, existing_node_version_ids: Iterable[str] | None = None) -> None:
        _coerce_edge_type(self.edge_type)
        _coerce_review_status(self.review_status)
        if self.from_curriculum_node_version_id == self.to_curriculum_node_version_id:
            raise Gate2R4ValidationError("edge endpoints must be different")
        if existing_node_version_ids is not None:
            known = set(existing_node_version_ids)
            missing = {
                self.from_curriculum_node_version_id,
                self.to_curriculum_node_version_id,
            } - known
            if missing:
                raise Gate2R4ValidationError(f"edge references unknown node versions: {sorted(missing)}")
        if self.review_status == ReviewStatus.APPROVED.value and not (self.reviewed_by and self.reviewed_at):
            raise Gate2R4ValidationError("approved edge requires reviewed_by and reviewed_at")
        if self.supersedes_edge_version_id == self.edge_version_id:
            raise Gate2R4ValidationError("edge version cannot supersede itself")

    @property
    def is_approved(self) -> bool:
        return self.review_status == ReviewStatus.APPROVED.value

    def approve(self, *, reviewer_id: str, reviewed_at: str | None = None, exception_id: str | None = None) -> "CurriculumEdgeVersion":
        if reviewer_id == self.proposed_by and not exception_id:
            raise Gate2R4ValidationError("edge proposer cannot be sole approver without an explicit exception record")
        updated = replace(
            self,
            review_status=ReviewStatus.APPROVED.value,
            reviewed_by=reviewer_id,
            reviewed_at=reviewed_at or _now().isoformat(),
            metadata={**self.metadata, **({"maker_checker_exception_id": exception_id} if exception_id else {})},
        )
        updated.validate()
        return updated

    def export(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["metadata"] = dict(sorted(self.metadata.items()))
        return payload


@dataclass(frozen=True)
class SourceCurriculumMappingVersion:
    mapping_id: str
    mapping_version_id: str
    source_chunk_version_id: str
    curriculum_node_version_id: str
    support_type: str
    authority_tier: str
    language: str
    mapping_rationale: str
    proposed_by: str
    proposed_at: str
    review_status: str = ReviewStatus.PROPOSED.value
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    review_notes: str | None = None
    source_page_id: str | None = None
    source_section_id: str | None = None
    language_status: str = LanguageAuthorityStatus.OFFICIAL_SOURCE.value
    supersedes_mapping_version_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(
        self,
        *,
        existing_source_chunk_version_ids: Iterable[str] | None = None,
        existing_curriculum_node_version_ids: Iterable[str] | None = None,
    ) -> None:
        _coerce_review_status(self.review_status)
        _coerce_language_status(self.language_status)
        try:
            SupportType(self.support_type)
        except ValueError as exc:
            raise Gate2R4ValidationError(f"invalid support_type: {self.support_type}") from exc
        if self.authority_tier not in AUTHORITY_TIERS:
            raise Gate2R4ValidationError(f"invalid authority_tier: {self.authority_tier}")
        if self.language not in ALLOWED_LANGUAGES:
            raise Gate2R4ValidationError(f"invalid language: {self.language}")
        if not self.mapping_rationale.strip():
            raise Gate2R4ValidationError("mapping_rationale is required")
        if not self.proposed_by.strip():
            raise Gate2R4ValidationError("proposed_by is required")
        if self.review_status == ReviewStatus.APPROVED.value and not (self.reviewed_by and self.reviewed_at):
            raise Gate2R4ValidationError("approved mapping requires reviewed_by and reviewed_at")
        if self.review_status == ReviewStatus.APPROVED.value and self.reviewed_by == self.proposed_by and not self.metadata.get("maker_checker_exception_id"):
            raise Gate2R4ValidationError("mapping proposer cannot be sole approver without explicit exception")
        if self.language_status == LanguageAuthorityStatus.MACHINE_TRANSLATION_DRAFT.value and self.authority_tier == "tier_1":
            raise Gate2R4ValidationError("machine translation draft cannot provide Tier 1 authority")
        if self.supersedes_mapping_version_id == self.mapping_version_id:
            raise Gate2R4ValidationError("mapping version cannot supersede itself")
        if existing_source_chunk_version_ids is not None and self.source_chunk_version_id not in set(existing_source_chunk_version_ids):
            raise Gate2R4ValidationError(f"mapping references unknown source chunk: {self.source_chunk_version_id}")
        if existing_curriculum_node_version_ids is not None and self.curriculum_node_version_id not in set(existing_curriculum_node_version_ids):
            raise Gate2R4ValidationError(f"mapping references unknown curriculum node version: {self.curriculum_node_version_id}")

    @property
    def corpus_eligible(self) -> bool:
        return self.review_status in CORPUS_ELIGIBLE_REVIEW_STATUS

    @property
    def tier1_approved(self) -> bool:
        return self.authority_tier == "tier_1" and self.review_status == ReviewStatus.APPROVED.value

    def move_to_review(self) -> "SourceCurriculumMappingVersion":
        if self.review_status not in {ReviewStatus.PROPOSED.value, ReviewStatus.NEEDS_REVISION.value}:
            raise Gate2R4ValidationError("only proposed or needs_revision mappings may move to review")
        return replace(self, review_status=ReviewStatus.IN_REVIEW.value)

    def approve(
        self,
        *,
        reviewer_id: str,
        reviewed_at: str | None = None,
        review_notes: str | None = None,
        exception_id: str | None = None,
    ) -> "SourceCurriculumMappingVersion":
        if reviewer_id == self.proposed_by and not exception_id:
            raise Gate2R4ValidationError("mapping proposer cannot be sole approver without explicit exception")
        metadata = dict(self.metadata)
        if exception_id:
            metadata["maker_checker_exception_id"] = exception_id
        updated = replace(
            self,
            review_status=ReviewStatus.APPROVED.value,
            reviewed_by=reviewer_id,
            reviewed_at=reviewed_at or _now().isoformat(),
            review_notes=review_notes,
            metadata=metadata,
        )
        updated.validate()
        return updated

    def reject(self, *, reviewer_id: str, review_notes: str, reviewed_at: str | None = None) -> "SourceCurriculumMappingVersion":
        if not review_notes.strip():
            raise Gate2R4ValidationError("rejection requires review_notes")
        return replace(
            self,
            review_status=ReviewStatus.REJECTED.value,
            reviewed_by=reviewer_id,
            reviewed_at=reviewed_at or _now().isoformat(),
            review_notes=review_notes,
        )

    def export(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["metadata"] = dict(sorted(self.metadata.items()))
        return payload


@dataclass(frozen=True)
class MappingReviewEvent:
    review_event_id: str
    mapping_version_id: str
    event_type: str
    actor_id: str
    occurred_at: str
    notes: str | None = None
    previous_status: str | None = None
    next_status: str | None = None
    exception_id: str | None = None
    per_item_trace_id: str | None = None

    def validate(self) -> None:
        if self.event_type not in APPEND_ONLY_REVIEW_EVENT_TYPES:
            raise Gate2R4ValidationError(f"invalid mapping review event_type: {self.event_type}")
        if not self.mapping_version_id or not self.actor_id:
            raise Gate2R4ValidationError("mapping review event requires mapping_version_id and actor_id")
        if self.event_type == "approved" and not self.per_item_trace_id:
            raise Gate2R4ValidationError("approval event requires a per-item trace id")

    def export(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CurriculumLanguageLink:
    language_link_id: str
    source_node_version_id: str
    target_node_version_id: str
    language_status: str
    created_by: str
    created_at: str = field(default_factory=lambda: _now().isoformat())
    review_status: str = ReviewStatus.PROPOSED.value
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    def validate(self, existing_node_version_ids: Iterable[str] | None = None) -> None:
        _coerce_language_status(self.language_status)
        _coerce_review_status(self.review_status)
        if self.source_node_version_id == self.target_node_version_id:
            raise Gate2R4ValidationError("language link endpoints must differ")
        if existing_node_version_ids is not None:
            known = set(existing_node_version_ids)
            missing = {self.source_node_version_id, self.target_node_version_id} - known
            if missing:
                raise Gate2R4ValidationError(f"language link references unknown node versions: {sorted(missing)}")
        if self.language_status == LanguageAuthorityStatus.MACHINE_TRANSLATION_DRAFT.value and self.review_status == ReviewStatus.APPROVED.value:
            raise Gate2R4ValidationError("machine translation draft cannot be approved as official authority")

    def export(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Gate2R4CurriculumGraph:
    source_chunk_version_ids: set[str] = field(default_factory=set)
    source_page_ids: set[str] = field(default_factory=set)
    source_section_ids: set[str] = field(default_factory=set)
    node_versions: dict[str, CurriculumNodeVersion] = field(default_factory=dict)
    edge_versions: list[CurriculumEdgeVersion] = field(default_factory=list)
    mapping_versions: dict[str, SourceCurriculumMappingVersion] = field(default_factory=dict)
    review_events: list[MappingReviewEvent] = field(default_factory=list)
    language_links: list[CurriculumLanguageLink] = field(default_factory=list)

    def add_source_chunk(self, chunk_version_id: str, *, page_id: str | None = None, section_id: str | None = None) -> None:
        if not chunk_version_id:
            raise Gate2R4ValidationError("chunk_version_id is required")
        self.source_chunk_version_ids.add(chunk_version_id)
        if page_id:
            self.source_page_ids.add(page_id)
        if section_id:
            self.source_section_ids.add(section_id)

    def add_node_version(self, node: CurriculumNodeVersion) -> None:
        node.validate()
        if node.curriculum_node_version_id in self.node_versions:
            raise Gate2R4ValidationError(f"duplicate node version: {node.curriculum_node_version_id}")
        self.node_versions[node.curriculum_node_version_id] = node

    def add_edge_version(self, edge: CurriculumEdgeVersion) -> None:
        edge.validate(self.node_versions.keys())
        self.edge_versions.append(edge)

    def propose_mapping_from_client(self, **payload: Any) -> SourceCurriculumMappingVersion:
        """Create a mapping proposal while rejecting client-supplied final approval state."""
        forbidden = {"approved", "reviewed_by", "reviewed_at"} & set(payload)
        if forbidden:
            raise Gate2R4ValidationError(f"client cannot supply approval fields: {sorted(forbidden)}")
        mapping = SourceCurriculumMappingVersion(
            mapping_id=payload.get("mapping_id") or _uuid(),
            mapping_version_id=payload.get("mapping_version_id") or _uuid(),
            source_chunk_version_id=payload["source_chunk_version_id"],
            source_page_id=payload.get("source_page_id"),
            source_section_id=payload.get("source_section_id"),
            curriculum_node_version_id=payload["curriculum_node_version_id"],
            support_type=payload.get("support_type", SupportType.DIRECT_SUPPORT.value),
            authority_tier=payload.get("authority_tier", "tier_1"),
            language=payload.get("language", "en"),
            language_status=payload.get("language_status", LanguageAuthorityStatus.OFFICIAL_SOURCE.value),
            mapping_rationale=payload["mapping_rationale"],
            proposed_by=payload["proposed_by"],
            proposed_at=payload.get("proposed_at") or _now().isoformat(),
            review_status=ReviewStatus.PROPOSED.value,
            metadata=payload.get("metadata", {}),
        )
        self.add_mapping_version(mapping)
        return mapping

    def add_mapping_version(self, mapping: SourceCurriculumMappingVersion) -> None:
        mapping.validate(
            existing_source_chunk_version_ids=self.source_chunk_version_ids,
            existing_curriculum_node_version_ids=self.node_versions.keys(),
        )
        if mapping.mapping_version_id in self.mapping_versions:
            raise Gate2R4ValidationError(f"duplicate mapping version: {mapping.mapping_version_id}")
        self.mapping_versions[mapping.mapping_version_id] = mapping
        self.review_events.append(
            MappingReviewEvent(
                review_event_id=_uuid(),
                mapping_version_id=mapping.mapping_version_id,
                event_type="proposed",
                actor_id=mapping.proposed_by,
                occurred_at=mapping.proposed_at,
                next_status=mapping.review_status,
                per_item_trace_id=f"proposal:{mapping.mapping_version_id}",
            )
        )

    def review_mapping(
        self,
        mapping_version_id: str,
        *,
        reviewer_id: str,
        decision: str,
        review_notes: str | None = None,
        exception_id: str | None = None,
        per_item_trace_id: str | None = None,
    ) -> SourceCurriculumMappingVersion:
        if decision not in {"approved", "rejected", "needs_revision", "withdrawn"}:
            raise Gate2R4ValidationError(f"unsupported mapping review decision: {decision}")
        current = self.mapping_versions[mapping_version_id]
        if decision == "approved":
            updated = current.approve(reviewer_id=reviewer_id, review_notes=review_notes, exception_id=exception_id)
        elif decision == "rejected":
            updated = current.reject(reviewer_id=reviewer_id, review_notes=review_notes or "Rejected")
        else:
            updated = replace(
                current,
                review_status=decision,
                reviewed_by=reviewer_id,
                reviewed_at=_now().isoformat(),
                review_notes=review_notes,
            )
            updated.validate(
                existing_source_chunk_version_ids=self.source_chunk_version_ids,
                existing_curriculum_node_version_ids=self.node_versions.keys(),
            )
        self.mapping_versions[mapping_version_id] = updated
        event = MappingReviewEvent(
            review_event_id=_uuid(),
            mapping_version_id=mapping_version_id,
            event_type=decision,
            actor_id=reviewer_id,
            occurred_at=updated.reviewed_at or _now().isoformat(),
            notes=review_notes,
            previous_status=current.review_status,
            next_status=updated.review_status,
            exception_id=exception_id,
            per_item_trace_id=per_item_trace_id or f"review:{mapping_version_id}:{decision}",
        )
        event.validate()
        self.review_events.append(event)
        return updated

    def add_language_link(self, link: CurriculumLanguageLink) -> None:
        link.validate(self.node_versions.keys())
        self.language_links.append(link)

    def approved_mappings_for_node(self, curriculum_node_version_id: str) -> list[SourceCurriculumMappingVersion]:
        return sorted(
            [
                mapping
                for mapping in self.mapping_versions.values()
                if mapping.curriculum_node_version_id == curriculum_node_version_id and mapping.review_status == ReviewStatus.APPROVED.value
            ],
            key=lambda mapping: mapping.mapping_version_id,
        )

    def validate_tier1_support(self) -> list[str]:
        errors: list[str] = []
        for node in sorted(self.node_versions.values(), key=lambda item: item.curriculum_node_version_id):
            if not (node.is_approved and node.is_caps_requirement):
                continue
            tier1 = [mapping for mapping in self.approved_mappings_for_node(node.curriculum_node_version_id) if mapping.authority_tier == "tier_1"]
            if not tier1:
                errors.append(
                    f"approved CAPS requirement lacks approved Tier 1 support mapping: {node.curriculum_node_version_id}"
                )
        return errors

    def validate_review_trace(self) -> list[str]:
        errors: list[str] = []
        approved_event_mapping_ids = {
            event.mapping_version_id
            for event in self.review_events
            if event.event_type == "approved" and event.per_item_trace_id
        }
        for event in self.review_events:
            try:
                event.validate()
            except Gate2R4ValidationError as exc:
                errors.append(str(exc))
        for mapping in sorted(self.mapping_versions.values(), key=lambda item: item.mapping_version_id):
            if mapping.review_status == ReviewStatus.APPROVED.value and mapping.mapping_version_id not in approved_event_mapping_ids:
                errors.append(f"approved mapping lacks per-item approval event: {mapping.mapping_version_id}")
            if mapping.review_status == ReviewStatus.APPROVED.value and mapping.reviewed_by == mapping.proposed_by and not mapping.metadata.get("maker_checker_exception_id"):
                errors.append(f"mapping self-approval lacks exception: {mapping.mapping_version_id}")
        return errors

    def validate_language_authority(self) -> list[str]:
        errors: list[str] = []
        for mapping in sorted(self.mapping_versions.values(), key=lambda item: item.mapping_version_id):
            try:
                mapping.validate(
                    existing_source_chunk_version_ids=self.source_chunk_version_ids,
                    existing_curriculum_node_version_ids=self.node_versions.keys(),
                )
            except Gate2R4ValidationError as exc:
                errors.append(str(exc))
        for link in self.language_links:
            try:
                link.validate(self.node_versions.keys())
            except Gate2R4ValidationError as exc:
                errors.append(str(exc))
        return errors

    def validate(self) -> list[str]:
        errors: list[str] = []
        for node in sorted(self.node_versions.values(), key=lambda item: item.curriculum_node_version_id):
            try:
                node.validate()
            except Gate2R4ValidationError as exc:
                errors.append(str(exc))
        for edge in self.edge_versions:
            try:
                edge.validate(self.node_versions.keys())
            except Gate2R4ValidationError as exc:
                errors.append(str(exc))
        for mapping in sorted(self.mapping_versions.values(), key=lambda item: item.mapping_version_id):
            try:
                mapping.validate(
                    existing_source_chunk_version_ids=self.source_chunk_version_ids,
                    existing_curriculum_node_version_ids=self.node_versions.keys(),
                )
            except Gate2R4ValidationError as exc:
                errors.append(str(exc))
        errors.extend(self.validate_tier1_support())
        errors.extend(self.validate_review_trace())
        errors.extend(self.validate_language_authority())
        return sorted(set(errors))

    def deterministic_export(self) -> dict[str, Any]:
        payload = {
            "schema": "edu_boost.phase02r.gate2r4.curriculum_graph_export.v1",
            "gate": "2R.4",
            "boundary": {
                "corpus_activation": False,
                "retrieval_projection_rebuild": False,
                "embeddings": False,
                "generation_or_tutor_change": False,
                "learner_facing_change": False,
            },
            "source_chunk_version_ids": sorted(self.source_chunk_version_ids),
            "source_page_ids": sorted(self.source_page_ids),
            "source_section_ids": sorted(self.source_section_ids),
            "node_versions": [node.export() for node in sorted(self.node_versions.values(), key=lambda item: item.curriculum_node_version_id)],
            "edge_versions": [edge.export() for edge in sorted(self.edge_versions, key=lambda item: item.edge_version_id)],
            "mapping_versions": [mapping.export() for mapping in sorted(self.mapping_versions.values(), key=lambda item: item.mapping_version_id)],
            "mapping_review_events": [event.export() for event in sorted(self.review_events, key=lambda item: (item.mapping_version_id, item.occurred_at, item.review_event_id))],
            "language_links": [link.export() for link in sorted(self.language_links, key=lambda item: item.language_link_id)],
        }
        payload["graph_sha256"] = _sha256_json(payload)
        return payload

    def validation_report(self) -> dict[str, Any]:
        graph_errors = self.validate()
        tier1_errors = self.validate_tier1_support()
        review_errors = self.validate_review_trace()
        language_errors = self.validate_language_authority()
        export = self.deterministic_export()
        return {
            "valid": not graph_errors,
            "gate": "2R.4",
            "graph_sha256": export["graph_sha256"],
            "counts": {
                "source_chunks": len(self.source_chunk_version_ids),
                "node_versions": len(self.node_versions),
                "edge_versions": len(self.edge_versions),
                "mapping_versions": len(self.mapping_versions),
                "review_events": len(self.review_events),
                "language_links": len(self.language_links),
            },
            "curriculum_graph_validation": {"valid": not graph_errors, "errors": graph_errors},
            "mapping_review_validation": {"valid": not review_errors, "errors": review_errors},
            "tier1_support_validation": {"valid": not tier1_errors, "errors": tier1_errors},
            "language_authority_validation": {"valid": not language_errors, "errors": language_errors},
            "boundary_validation": {
                "valid": True,
                "corpus_activation": False,
                "production_retrieval_projection": False,
                "learner_facing_change": False,
            },
        }


# Deterministic fixture IDs intentionally do not use uuid4.  The sample graph is
# evidence-friendly and stable across repeated exports.
NODE_NUMBERS_ID = "node-g4-maths-nor-001"
NODE_NUMBERS_VERSION_ID = "nodever-g4-maths-nor-001-v1"
NODE_ASSESS_ID = "node-g4-maths-nor-assess-001"
NODE_ASSESS_VERSION_ID = "nodever-g4-maths-nor-assess-001-v1"
CHUNK_NUMBERS_ID = "chunkver-caps-g4-nor-001"
MAPPING_NUMBERS_ID = "mapping-g4-maths-nor-001"
MAPPING_NUMBERS_VERSION_ID = "mappingver-g4-maths-nor-001-v1"
MAPPING_ASSESS_VERSION_ID = "mappingver-g4-maths-nor-assess-001-v1"


def build_grade4_mathematics_skeleton() -> list[GraphNodeDraft]:
    """Return the Grade 4 Mathematics CAPS skeleton used by legacy verifiers."""
    strands = [
        ("numbers_operations_relationships", "Numbers, operations and relationships"),
        ("patterns_functions_algebra", "Patterns, functions and algebra"),
        ("space_shape_geometry", "Space and shape"),
        ("measurement", "Measurement"),
        ("data_handling", "Data handling"),
    ]
    nodes = [
        GraphNodeDraft("curriculum", "CAPS", "CAPS"),
        GraphNodeDraft("grade", "GRADE_4", "Grade 4"),
        GraphNodeDraft("subject", "GRADE_4_MATHEMATICS", "Grade 4 Mathematics"),
    ]
    nodes.extend(GraphNodeDraft("strand", code.upper(), label) for code, label in strands)
    return nodes


def build_gate2r4_reference_graph() -> Gate2R4CurriculumGraph:
    """Build a deterministic, reviewed Gate 2R.4 reference graph."""
    graph = Gate2R4CurriculumGraph()
    graph.add_source_chunk(CHUNK_NUMBERS_ID, page_id="page-caps-g4-001", section_id="section-caps-g4-nor")

    objective = CurriculumNodeVersion(
        curriculum_node_id=NODE_NUMBERS_ID,
        curriculum_node_version_id=NODE_NUMBERS_VERSION_ID,
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATHEMATICS",
        strand="Numbers, operations and relationships",
        term="1",
        topic="Whole numbers",
        subtopic="Number range and place value",
        skill="Compare, order and represent whole numbers",
        learning_objective="Learners compare, order and represent whole numbers in the Grade 4 range.",
        assessment_statement="Learner can compare and order whole numbers using place value.",
        language="en",
        status=NodeStatus.APPROVED.value,
        effective_from="2026-06-22",
        created_by="phase02r_gate2r4_reference",
        created_at="2026-06-22T00:00:00+00:00",
        node_type="learning_objective",
    )
    assessment = CurriculumNodeVersion(
        curriculum_node_id=NODE_ASSESS_ID,
        curriculum_node_version_id=NODE_ASSESS_VERSION_ID,
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATHEMATICS",
        strand="Numbers, operations and relationships",
        term="1",
        topic="Whole numbers",
        subtopic="Number range and place value",
        skill="Assess place-value comparison",
        learning_objective="Assess whether learners compare and order whole numbers correctly.",
        assessment_statement="Use ordered number sets and comparison prompts as assessment evidence.",
        language="en",
        status=NodeStatus.APPROVED.value,
        effective_from="2026-06-22",
        created_by="phase02r_gate2r4_reference",
        created_at="2026-06-22T00:00:00+00:00",
        node_type="assessment_statement",
    )
    graph.add_node_version(objective)
    graph.add_node_version(assessment)
    graph.add_edge_version(
        CurriculumEdgeVersion(
            edge_version_id="edgever-g4-maths-nor-assesses-001-v1",
            from_curriculum_node_version_id=NODE_ASSESS_VERSION_ID,
            to_curriculum_node_version_id=NODE_NUMBERS_VERSION_ID,
            edge_type=EdgeType.ASSESSES.value,
            review_status=ReviewStatus.APPROVED.value,
            proposed_by="curriculum_mapper",
            proposed_at="2026-06-22T00:00:00+00:00",
            reviewed_by="curriculum_reviewer",
            reviewed_at="2026-06-22T00:05:00+00:00",
            review_notes="Assessment statement traces to the approved learning objective.",
        )
    )
    mapping = SourceCurriculumMappingVersion(
        mapping_id=MAPPING_NUMBERS_ID,
        mapping_version_id=MAPPING_NUMBERS_VERSION_ID,
        source_chunk_version_id=CHUNK_NUMBERS_ID,
        source_page_id="page-caps-g4-001",
        source_section_id="section-caps-g4-nor",
        curriculum_node_version_id=NODE_NUMBERS_VERSION_ID,
        support_type=SupportType.DIRECT_SUPPORT.value,
        authority_tier="tier_1",
        language="en",
        language_status=LanguageAuthorityStatus.OFFICIAL_SOURCE.value,
        mapping_rationale="CAPS source chunk directly supports the Grade 4 whole-number comparison objective.",
        proposed_by="curriculum_mapper",
        proposed_at="2026-06-22T00:10:00+00:00",
        review_status=ReviewStatus.APPROVED.value,
        reviewed_by="curriculum_reviewer",
        reviewed_at="2026-06-22T00:15:00+00:00",
        review_notes="Approved as Tier 1 CAPS support for Gate 2R.4 readiness only.",
    )
    assessment_mapping = SourceCurriculumMappingVersion(
        mapping_id="mapping-g4-maths-nor-assess-001",
        mapping_version_id=MAPPING_ASSESS_VERSION_ID,
        source_chunk_version_id=CHUNK_NUMBERS_ID,
        source_page_id="page-caps-g4-001",
        source_section_id="section-caps-g4-nor",
        curriculum_node_version_id=NODE_ASSESS_VERSION_ID,
        support_type=SupportType.ASSESSMENT_EVIDENCE.value,
        authority_tier="tier_1",
        language="en",
        language_status=LanguageAuthorityStatus.OFFICIAL_SOURCE.value,
        mapping_rationale="CAPS source chunk supports assessment evidence for whole-number comparison.",
        proposed_by="curriculum_mapper",
        proposed_at="2026-06-22T00:11:00+00:00",
        review_status=ReviewStatus.APPROVED.value,
        reviewed_by="curriculum_reviewer",
        reviewed_at="2026-06-22T00:16:00+00:00",
        review_notes="Approved as Tier 1 assessment support for Gate 2R.4 readiness only.",
    )
    graph.add_mapping_version(mapping)
    graph.add_mapping_version(assessment_mapping)
    # Replace proposal-only events with deterministic approval events for evidence.
    graph.review_events = [
        MappingReviewEvent(
            review_event_id="review-g4-maths-nor-001-proposed",
            mapping_version_id=MAPPING_NUMBERS_VERSION_ID,
            event_type="proposed",
            actor_id="curriculum_mapper",
            occurred_at="2026-06-22T00:10:00+00:00",
            next_status=ReviewStatus.PROPOSED.value,
            per_item_trace_id=f"proposal:{MAPPING_NUMBERS_VERSION_ID}",
        ),
        MappingReviewEvent(
            review_event_id="review-g4-maths-nor-001-approved",
            mapping_version_id=MAPPING_NUMBERS_VERSION_ID,
            event_type="approved",
            actor_id="curriculum_reviewer",
            occurred_at="2026-06-22T00:15:00+00:00",
            previous_status=ReviewStatus.PROPOSED.value,
            next_status=ReviewStatus.APPROVED.value,
            per_item_trace_id=f"review:{MAPPING_NUMBERS_VERSION_ID}:approved",
            notes="Approved as Tier 1 CAPS support.",
        ),
        MappingReviewEvent(
            review_event_id="review-g4-maths-nor-assess-001-proposed",
            mapping_version_id=MAPPING_ASSESS_VERSION_ID,
            event_type="proposed",
            actor_id="curriculum_mapper",
            occurred_at="2026-06-22T00:11:00+00:00",
            next_status=ReviewStatus.PROPOSED.value,
            per_item_trace_id=f"proposal:{MAPPING_ASSESS_VERSION_ID}",
        ),
        MappingReviewEvent(
            review_event_id="review-g4-maths-nor-assess-001-approved",
            mapping_version_id=MAPPING_ASSESS_VERSION_ID,
            event_type="approved",
            actor_id="curriculum_reviewer",
            occurred_at="2026-06-22T00:16:00+00:00",
            previous_status=ReviewStatus.PROPOSED.value,
            next_status=ReviewStatus.APPROVED.value,
            per_item_trace_id=f"review:{MAPPING_ASSESS_VERSION_ID}:approved",
            notes="Approved as Tier 1 assessment support.",
        ),
    ]
    return graph


def validate_gate2r4_reference_graph() -> dict[str, Any]:
    """Return the deterministic validation report used by Gate 2R.4 scripts."""
    graph = build_gate2r4_reference_graph()
    return graph.validation_report()


def export_gate2r4_reference_graph() -> dict[str, Any]:
    """Return the deterministic Gate 2R.4 graph export."""
    return build_gate2r4_reference_graph().deterministic_export()


def ensure_no_gate2r5_scope(paths_changed: Sequence[str]) -> list[str]:
    """Return forbidden path changes that would indicate Gate 2R.5+ leakage."""
    forbidden_markers = (
        "semantic_retrieval/",
        "retrieval_projection",
        "embedding",
        "corpus_activation",
        "tutor_grounding",
        "generation_grounding",
    )
    allowed_gate2r4_paths = (
        "app/services/curriculum/graph.py",
        "app/models/curriculum_graph.py",
        "scripts/curriculum/validate_phase02r_gate2r4_graph.py",
        "scripts/curriculum/export_phase02r_curriculum_graph.py",
        "scripts/verify_phase02r_gate2r4.py",
        "scripts/verify_phase02r_gate2r4_postgres.sh",
        "scripts/collect_phase02r_gate2r4_evidence.sh",
        "tests/unit/phase02r/test_gate2r4_curriculum_graph.py",
        "docs/roadmap/execution/atlas/phase_02r_gate_2r4_implementation_note.md",
        "alembic/versions/20260622_1200_phase02r_gate2r4_curriculum_graph.py",
    )
    violations: list[str] = []
    for path in paths_changed:
        normalized = path.replace("\\", "/")
        if normalized.startswith(allowed_gate2r4_paths):
            continue
        if any(marker in normalized for marker in forbidden_markers):
            violations.append(normalized)
    return sorted(set(violations))
