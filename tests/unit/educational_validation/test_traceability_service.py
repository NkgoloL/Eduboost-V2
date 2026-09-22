from datetime import datetime, timezone
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
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
from app.services.educational_validation.traceability import (
    EducationalTraceabilityService,
    compute_state_hash,
)


@pytest_asyncio.fixture
async def async_db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    tables = [
        LEVInteractionEvent.__table__,
        LEVMasteryStateTransition.__table__,
        LEVValidationRun.__table__,
    ]
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, tables=tables))

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


def test_compute_state_hash_deterministic():
    now_iso = "2026-09-22T10:00:00+00:00"
    pre = {"mastery_level": 0.2, "confidence": 0.1}
    post = {"mastery_level": 0.5, "confidence": 0.4}
    ev_ids = ["evt-1", "evt-2"]

    hash1 = compute_state_hash("lrn-001", "math.add", now_iso, pre, post, ev_ids)
    hash2 = compute_state_hash("lrn-001", "math.add", now_iso, pre, post, ["evt-2", "evt-1"])
    assert hash1 == hash2
    assert len(hash1) == 64

    # Different post state -> different hash
    post_diff = {"mastery_level": 0.6, "confidence": 0.4}
    hash3 = compute_state_hash("lrn-001", "math.add", now_iso, pre, post_diff, ev_ids)
    assert hash1 != hash3


@pytest.mark.asyncio
async def test_traceability_service_ingest_and_query(async_db_session):
    repo = EducationalValidationRepository()
    service = EducationalTraceabilityService(repository=repo)

    event_schema = InteractionEventSchema(
        event_id="00000000-0000-0000-0000-000000000001",
        occurred_at=datetime.now(timezone.utc),
        learner_pseudonym="lrn-test-01",
        concept_id="caps.math.gr4.add",
        item_id="item-test-01",
        first_attempt_correct=True,
        attempt_count=1,
        hint_count=0,
    )

    saved_event = await service.ingest_interaction_event(async_db_session, event_schema)
    assert saved_event.event_id is not None
    assert saved_event.learner_pseudonym == "lrn-test-01"

    events = await repo.get_learner_events(async_db_session, "lrn-test-01")
    assert len(events) == 1
    assert events[0].item_id == "item-test-01"


@pytest.mark.asyncio
async def test_traceability_service_transition_with_hash(async_db_session):
    repo = EducationalValidationRepository()
    service = EducationalTraceabilityService(repository=repo)

    trans_schema = MasteryStateTransitionSchema(
        transition_id="00000000-0000-0000-0000-000000000002",
        learner_pseudonym="lrn-test-02",
        concept_id="caps.math.gr4.add",
        occurred_at=datetime.now(timezone.utc),
        pre_state={"mastery_level": 0.1, "confidence": 0.1},
        post_state={"mastery_level": 0.5, "confidence": 0.4},
        evidence_event_ids=["00000000-0000-0000-0000-000000000001"],
        update_rationale="Initial mastery gain from quiz.",
    )

    saved_trans = await service.record_transition(async_db_session, trans_schema)
    assert saved_trans.state_hash is not None
    assert len(saved_trans.state_hash) == 64

    transitions = await repo.get_learner_transitions(async_db_session, "lrn-test-02")
    assert len(transitions) == 1
    assert transitions[0].state_hash == saved_trans.state_hash
