from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.domain.educational_validation_schemas import (
    InteractionEventSchema,
    MasteryClaimDefinition,
    MasteryStatePayload,
    MasteryStateTransitionSchema,
    MAX_CONFIDENCE_THRESHOLD,
    UseAuthorizationSchema,
)


def test_interaction_event_schema_valid():
    event = InteractionEventSchema(
        event_id="evt-12345",
        occurred_at=datetime.now(timezone.utc),
        learner_pseudonym="lrn-001",
        concept_id="caps.math.gr4.add",
        item_id="item-01",
        first_attempt_correct=True,
        attempt_count=1,
        hint_count=0,
        response_latency_ms=4500,
        evidence_type="synthetic_fixture",
    )
    assert event.learner_pseudonym == "lrn-001"
    assert event.evidence_type == "synthetic_fixture"


def test_mastery_state_confidence_capped():
    # Attempting confidence = 0.95 should be capped at MAX_CONFIDENCE_THRESHOLD = 0.60
    state = MasteryStatePayload(mastery_level=0.85, confidence=0.95)
    assert state.confidence == MAX_CONFIDENCE_THRESHOLD


def test_mastery_transition_schema_valid():
    transition = MasteryStateTransitionSchema(
        transition_id="trans-001",
        learner_pseudonym="lrn-001",
        concept_id="caps.math.gr4.add",
        occurred_at=datetime.now(timezone.utc),
        pre_state={"mastery_level": 0.2, "confidence": 0.1},
        post_state={"mastery_level": 0.6, "confidence": 0.5},
        evidence_event_ids=["evt-1"],
        update_rationale="Initial assessment update.",
    )
    assert transition.concept_id == "caps.math.gr4.add"
    assert len(transition.evidence_event_ids) == 1


def test_mastery_transition_schema_empty_evidence_fails():
    with pytest.raises(ValidationError):
        MasteryStateTransitionSchema(
            transition_id="trans-001",
            learner_pseudonym="lrn-001",
            concept_id="caps.math.gr4.add",
            occurred_at=datetime.now(timezone.utc),
            pre_state={},
            post_state={},
            evidence_event_ids=[],  # Min length 1 required
        )


def test_mastery_claim_definition_defaults():
    claim = MasteryClaimDefinition(
        claim_id="CLAIM-01",
        concept_id="caps.math.gr4.add",
        construct_name="Whole number addition",
        description="Addition of 3-digit whole numbers.",
    )
    assert claim.max_confidence_threshold == MAX_CONFIDENCE_THRESHOLD
    assert "formal_grading" in claim.prohibited_decision_scopes
