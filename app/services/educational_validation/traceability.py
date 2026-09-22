"""Educational Traceability & Telemetry Service (LEV-WS03).

Provides cryptographic SHA-256 state hashing for mastery state transitions,
enforces append-only immutable event sourcing, and manages persistence via
EducationalValidationRepository.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.educational_validation_schemas import (
    InteractionEventSchema,
    MasteryStateTransitionSchema,
)
from app.models.educational_validation import (
    LEVInteractionEvent,
    LEVMasteryStateTransition,
    LEVValidationRun,
)
from app.repositories.educational_validation_repository import (
    EducationalValidationRepository,
)


def compute_state_hash(
    learner_pseudonym: str,
    concept_id: str,
    occurred_at_iso: str,
    pre_state: Dict[str, Any],
    post_state: Dict[str, Any],
    evidence_event_ids: List[str],
) -> str:
    """Compute deterministic SHA-256 hash across transition components."""
    canonical_payload = {
        "learner_pseudonym": learner_pseudonym,
        "concept_id": concept_id,
        "occurred_at": occurred_at_iso,
        "pre_state": pre_state,
        "post_state": post_state,
        "evidence_event_ids": sorted(evidence_event_ids),
    }
    encoded = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class EducationalTraceabilityService:
    """Service orchestrating educational validation telemetry and state traceability."""

    def __init__(
        self,
        repository: Optional[EducationalValidationRepository] = None,
    ) -> None:
        self.repo = repository or EducationalValidationRepository()

    async def ingest_interaction_event(
        self,
        db: AsyncSession,
        event_schema: InteractionEventSchema,
    ) -> LEVInteractionEvent:
        """Validate and append an interaction event to the audit trail."""
        event_model = LEVInteractionEvent(
            event_id=uuid.UUID(event_schema.event_id) if len(event_schema.event_id) == 36 else uuid.uuid4(),
            occurred_at=event_schema.occurred_at,
            learner_pseudonym=event_schema.learner_pseudonym,
            concept_id=event_schema.concept_id,
            item_id=event_schema.item_id,
            item_version=event_schema.item_version,
            graph_version=event_schema.graph_version,
            model_version=event_schema.model_version,
            consent_state=event_schema.consent_state,
            first_attempt_correct=event_schema.first_attempt_correct,
            attempt_count=event_schema.attempt_count,
            hint_count=event_schema.hint_count,
            response_latency_ms=event_schema.response_latency_ms,
            teacher_assistance=event_schema.teacher_assistance,
            evidence_type=event_schema.evidence_type,
        )
        return await self.repo.record_interaction_event(db, event_model)

    async def record_transition(
        self,
        db: AsyncSession,
        transition_schema: MasteryStateTransitionSchema,
    ) -> LEVMasteryStateTransition:
        """Record an immutable, cryptographically hashed mastery state transition."""
        occurred_iso = transition_schema.occurred_at.isoformat()
        state_hash = compute_state_hash(
            learner_pseudonym=transition_schema.learner_pseudonym,
            concept_id=transition_schema.concept_id,
            occurred_at_iso=occurred_iso,
            pre_state=transition_schema.pre_state,
            post_state=transition_schema.post_state,
            evidence_event_ids=transition_schema.evidence_event_ids,
        )

        transition_model = LEVMasteryStateTransition(
            transition_id=uuid.UUID(transition_schema.transition_id)
            if len(transition_schema.transition_id) == 36
            else uuid.uuid4(),
            learner_pseudonym=transition_schema.learner_pseudonym,
            concept_id=transition_schema.concept_id,
            occurred_at=transition_schema.occurred_at,
            pre_state=transition_schema.pre_state,
            post_state=transition_schema.post_state,
            evidence_event_ids=transition_schema.evidence_event_ids,
            model_version=transition_schema.model_version,
            graph_version=transition_schema.graph_version,
            update_rationale=transition_schema.update_rationale,
            state_hash=state_hash,
            evidence_type=transition_schema.evidence_type,
        )
        return await self.repo.record_mastery_transition(db, transition_model)

    async def record_validation_run(
        self,
        db: AsyncSession,
        run_type: str,
        model_version: str,
        metrics: Dict[str, Any],
        manifest_id: Optional[str] = None,
        evidence_type: str = "synthetic_fixture",
    ) -> LEVValidationRun:
        """Record an analytical or psychometric validation run."""
        run_model = LEVValidationRun(
            run_id=uuid.uuid4(),
            run_type=run_type,
            model_version=model_version,
            evidence_type=evidence_type,
            status="completed",
            metrics=metrics,
            manifest_id=manifest_id,
            executed_at=datetime.now(timezone.utc),
        )
        return await self.repo.record_validation_run(db, run_model)
