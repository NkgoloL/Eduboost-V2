"""Deep unit tests for Content Review Governance, Source Context, and Diagnostics router serialization."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.content_review_governance import (
    ReviewGovernancePolicy,
    ReviewConflictError,
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
)
from app.services.content_generation.source_context import (
    source_rows_for_chunks,
)
from app.services.content_generation.prompt_payloads import (
    SourceContextChunk,
)
from app.api_v2_routers.diagnostics import (
    _subject_code,
    _option_payload,
    _serialise_item_bank_item,
)
from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum


# ---------------------------------------------------------------------------
# Review Governance Policy Tests
# ---------------------------------------------------------------------------

class TestReviewGovernancePolicyDeep:
    def test_required_criteria_constants(self):
        assert "caps_alignment" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "factual_accuracy" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "answer_key_correctness" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert len(REQUIRED_APPROVAL_RUBRIC_CRITERIA) == 10

    def test_policy_from_environment_valid(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "4", "CONTENT_CONSENSUS_TIMEOUT_HOURS": "48"}):
            policy = ReviewGovernancePolicy.from_environment()
            assert policy.quorum_threshold == 4
            assert policy.stale_after_hours == 48

    def test_policy_from_environment_invalid_threshold_low(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "1"}):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_THRESHOLD must be between 2 and 10"):
                ReviewGovernancePolicy.from_environment()

    def test_policy_from_environment_invalid_threshold_high(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "15"}):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_THRESHOLD must be between 2 and 10"):
                ReviewGovernancePolicy.from_environment()

    def test_policy_from_environment_invalid_timeout(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_TIMEOUT_HOURS": "0"}):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_TIMEOUT_HOURS must be positive"):
                ReviewGovernancePolicy.from_environment()

    def test_review_conflict_error(self):
        err = ReviewConflictError("State conflict on artifact approval")
        assert "State conflict" in str(err)
        assert isinstance(err, ValueError)


# ---------------------------------------------------------------------------
# Source Rows for Chunks Tests
# ---------------------------------------------------------------------------

class TestSourceContextHelpers:
    def test_source_rows_for_chunks_empty(self):
        result = source_rows_for_chunks([], caps_ref="4.M.1.1", grade=4, subject_code="MATH", language="en")
        assert result == []

    def test_source_rows_for_chunks_with_data(self):
        chunk = SourceContextChunk(
            source_document_id=str(uuid.uuid4()),
            source_chunk_id=str(uuid.uuid4()),
            text="Grounded source material on whole numbers.",
            source_title="Grade 4 Math CAPS Guide",
            source_hash="sha256:abcd1234",
            curriculum_mapping_id=str(uuid.uuid4()),
            source_quality_score=0.95,
            license_status="open_access",
            document_status="indexed",
        )

        rows = source_rows_for_chunks([chunk], caps_ref="4.M.1.1", grade=4, subject_code="MATH", language="en")
        assert len(rows) == 1
        assert rows[0]["source_document_id"] == chunk.source_document_id
        assert rows[0]["source_title"] == "Grade 4 Math CAPS Guide"
        assert rows[0]["grade"] == 4
        assert rows[0]["subject_code"] == "MATH"
        assert rows[0]["language"] == "en"
        assert rows[0]["source_quality_score"] == 0.95


# ---------------------------------------------------------------------------
# Diagnostics Serialization Helper Tests
# ---------------------------------------------------------------------------

class TestDiagnosticsHelpers:
    def test_subject_code_mapping(self):
        assert _subject_code("Mathematics") == "MATH"
        assert _subject_code("math") == "MATH"
        assert _subject_code("english") == "ENG"
        assert _subject_code("Natural Sciences") == "NS"
        assert _subject_code("Social Sciences") == "SS"
        assert _subject_code("Life Orientation") == "LIFE"
        assert _subject_code("PHYSICS") == "PHYSICS"

    def test_option_payload_dict(self):
        opts = {"A": "First option", "B": "Second option"}
        payload = _option_payload(opts)
        assert len(payload) == 2
        assert payload[0] == {"key": "A", "label": "First option"}
        assert payload[1] == {"key": "B", "label": "Second option"}

    def test_option_payload_list_of_strings(self):
        opts = ["Alpha", "Beta", "Gamma"]
        payload = _option_payload(opts)
        assert len(payload) == 3
        assert payload[0] == {"key": "A", "label": "Alpha"}
        assert payload[1] == {"key": "B", "label": "Beta"}
        assert payload[2] == {"key": "C", "label": "Gamma"}

    def test_option_payload_empty(self):
        assert _option_payload(None) == []
        assert _option_payload([]) == []

    def test_serialise_item_bank_item(self):
        item_id = uuid.uuid4()
        item = MagicMock(spec=DiagnosticItem)
        item.item_id = item_id
        item.stem = "What is 2 + 2?"
        item.options = ["3", "4", "5", "6"]
        item.subject = "mathematics"
        item.topic = "Addition"
        item.skill = "Arithmetic"
        item.difficulty_b = 0.25
        item.discrimination_a = 1.15
        item.caps_ref = "4.M.1.1"
        item.review_status = ReviewStatusEnum.APPROVED

        serialized = _serialise_item_bank_item(item)
        assert serialized["id"] == str(item_id)
        assert serialized["question"] == "What is 2 + 2?"
        assert serialized["subject"] == "MATH"
        assert serialized["difficulty"] == 0.25
        assert serialized["discrimination"] == 1.15
        assert len(serialized["options"]) == 4
