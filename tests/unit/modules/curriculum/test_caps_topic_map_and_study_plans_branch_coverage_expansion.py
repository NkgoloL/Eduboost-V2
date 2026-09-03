"""Batch 237 — CAPSTopicMap and Study Plans router branch coverage expansion.

Tests:
- app/services/curriculum/caps_topic_map.py:
  - Normalisation & slugification helpers
  - CAPSTopic dataclass and reference string composition
  - CAPSTopicMap:
    - subjects_for_grade across grades
    - topics_for canonical matching
    - find_topic: exact match, substring topic match, substring subtopic match, not found
    - get by reference: found vs None
    - suggest_topic: empty candidates (None), close match, fallback
    - coverage_summary: nested grade/subject count verification
- app/api_v2_routers/study_plans.py:
  - generate_study_plan: end-to-end execution, runtime KG payload creation, durable enqueue, JobAcceptedResponse
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api_v2_deps.auth import AuthContext
from app.api_v2_routers.study_plans import generate_study_plan
from app.domain.api_v2_models import StudyPlanGenerateRequest
from app.models import UserRole
from app.services.curriculum.caps_topic_map import (
    CURRICULUM_MAP_VERSION,
    CAPSTopic,
    CAPSTopicMap,
    _normalise,
    _slug,
)


# ---------------------------------------------------------------------------
# CAPSTopicMap Unit Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_caps_topic_map_helpers_and_reference():
    assert _normalise("Maths & Science/Tech_1") == "maths and science tech 1"
    assert _slug("Maths & Science") == "maths-and-science"

    topic = CAPSTopic(
        phase="intermediate",
        grade=4,
        subject="mathematics",
        term=1,
        topic="whole numbers",
        subtopic="addition and subtraction",
    )
    ref = topic.reference
    assert ref.startswith(f"CAPS:{CURRICULUM_MAP_VERSION}:G4:mathematics:T1:")
    assert "whole-numbers" in ref


@pytest.mark.unit
def test_caps_topic_map_queries_and_suggestions():
    custom_topics = [
        CAPSTopic("intermediate", 4, "mathematics", 1, "fractions", "equivalent fractions"),
        CAPSTopic("intermediate", 4, "mathematics", 2, "decimals", "tenths and hundredths"),
        CAPSTopic("intermediate", 4, "english", 1, "grammar", "nouns and verbs"),
    ]
    tmap = CAPSTopicMap(topics=custom_topics, version="custom-2026")

    # subjects_for_grade
    assert set(tmap.subjects_for_grade(4)) == {"mathematics", "english"}
    assert tmap.subjects_for_grade(9) == ()

    # topics_for
    assert len(tmap.topics_for(4, "MATHEMATICS")) == 2
    assert len(tmap.topics_for(4, "Science")) == 0

    # find_topic branches
    # 1. Exact topic and subtopic match
    t_exact = tmap.find_topic(4, "mathematics", "fractions", "equivalent fractions")
    assert t_exact is not None and t_exact.subtopic == "equivalent fractions"

    # 2. Substring topic match
    t_sub = tmap.find_topic(4, "mathematics", "fractions review")
    assert t_sub is not None and t_sub.topic == "fractions"

    # 3. Substring subtopic match
    t_subtopic = tmap.find_topic(4, "mathematics", "unknown", "tenths")
    assert t_subtopic is not None and t_subtopic.topic == "decimals"

    # 4. Miss
    assert tmap.find_topic(4, "mathematics", "calculus") is None

    # get by reference
    ref_first = custom_topics[0].reference
    assert tmap.get(ref_first) == custom_topics[0]
    assert tmap.get("CAPS:missing:ref") is None

    # suggest_topic
    assert tmap.suggest_topic(9, "mathematics", "fractions") is None  # no candidates
    sugg_close = tmap.suggest_topic(4, "mathematics", "fraction")
    assert sugg_close is not None and sugg_close.topic == "fractions"
    sugg_fallback = tmap.suggest_topic(4, "mathematics", "completely unrelated query")
    assert sugg_fallback is not None  # returns candidate[0]

    # coverage_summary
    summary = tmap.coverage_summary()
    assert summary["version"] == "custom-2026"
    assert summary["topic_count"] == 3
    assert summary["grades"][4]["mathematics"] == 2


# ---------------------------------------------------------------------------
# Study Plans Router Unit Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_study_plan_router_flow():
    mock_db = AsyncMock()
    user = AuthContext(
        user_id=str(uuid.uuid4()),
        roles=[UserRole.STUDENT],
        token_type="access",
        raw_claims={},
        jti=str(uuid.uuid4()),
    )
    learner_id = str(uuid.uuid4())
    req = StudyPlanGenerateRequest(gap_ratio=0.4)

    with patch("app.api_v2_routers.study_plans.require_learner_write_for_current_user") as mock_write_auth, \
         patch("app.api_v2_routers.study_plans.require_active_consent_for_current_user", new_callable=AsyncMock) as mock_consent, \
         patch("app.api_v2_routers.study_plans.build_runtime_kg_study_plan_payload", new_callable=AsyncMock) as mock_kg, \
         patch("app.api_v2_routers.study_plans.enqueue_durable", new_callable=AsyncMock) as mock_enqueue:

        mock_kg.return_value = {"kg_nodes": ["node-1"]}
        mock_enqueue.return_value = "job-study-plan-999"

        response = await generate_study_plan(
            learner_id=learner_id,
            request=req,
            current_user=user,
            db=mock_db,
        )

        assert response.job_id == "job-study-plan-999"
        assert response.operation == "study_plan_generation"
        assert response.status == "queued"

        mock_write_auth.assert_called_once_with(user, learner_id)
        mock_consent.assert_called_once_with(mock_db, user, learner_id)
        mock_kg.assert_called_once_with(mock_db, learner_id=learner_id, subject_code="Mathematics")
        mock_enqueue.assert_called_once()
