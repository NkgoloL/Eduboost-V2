"""
P1-10 — Unit tests for DiagnosticItem and ItemExposure ORM models
==================================================================
Adapted for Phase 2 schema changes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import RelationshipProperty

from app.domain.item_schema import (
    ItemCreate,
    ItemSource,
    ItemType,
    LanguageCode,
    MCQOption,
    ReviewStatus,
    SubjectCode,
)
from app.models.diagnostic_item import (
    DiagnosticItem,
    DifficultyBandEnum,
    ItemSourceEnum,
    ItemTypeEnum,
    LanguageEnum,
    ReviewStatusEnum,
    SubjectCodeEnum,
)
from app.models.item_exposure import ItemExposure

VALID_ITEM_DICT: dict[str, Any] = {
    "caps_ref": "4.M.1.1",
    "grade": 4,
    "subject": "Mathematics",
    "term": 1,
    "topic": "Whole Numbers",
    "subtopic": "Place value",
    "skill": "identify_place_value_4digit",
    "stem": "What is the value of the digit 3 in the number 2 347?",
    "answer_key": "A",
    "options": [
        {"label": "A", "text": "300"},
        {"label": "B", "text": "30"},
        {"label": "C", "text": "3"},
        {"label": "D", "text": "3 000"},
    ],
    "explanation": "In 2 347, the digit 3 is in the hundreds column, so its value is 300.",
    "distractor_rationale": {
        "B": "Learner placed 3 in tens",
        "C": "Learner read face value only",
        "D": "Learner placed 3 in thousands"
    },
    "misconception_tags": ["place_value_confusion", "face_value_error"],
    "item_type": "mcq",
    "language": "en",
    "difficulty_b": -0.5,
    "discrimination_a": 1.0,
    "guessing_c": 0.25,
    "max_exposure": 50,
    "source": "llm_generated",
    "safety_passed": True,
}

class TestEnumMirrors:
    def test_review_status_values_match(self) -> None:
        orm_values = {m.value for m in ReviewStatusEnum}
        pydantic_values = {m.value for m in ReviewStatus}
        assert orm_values == pydantic_values

    def test_item_type_values_match(self) -> None:
        orm_values = {m.value for m in ItemTypeEnum}
        pydantic_values = {m.value for m in ItemType}
        assert orm_values == pydantic_values

    def test_subject_code_values_match(self) -> None:
        orm_values = {m.value for m in SubjectCodeEnum}
        pydantic_values = {m.value for m in SubjectCode}
        assert orm_values == pydantic_values

    def test_language_values_match(self) -> None:
        orm_values = {m.value for m in LanguageEnum}
        pydantic_values = {m.value for m in LanguageCode}
        assert orm_values == pydantic_values

    def test_item_source_values_match(self) -> None:
        orm_values = {m.value for m in ItemSourceEnum}
        pydantic_values = {m.value for m in ItemSource}
        assert orm_values == pydantic_values

class TestDiagnosticItemColumns:
    def _table(self):
        return DiagnosticItem.__table__

    def test_tablename(self) -> None:
        assert DiagnosticItem.__tablename__ == "diagnostic_items"

    def test_primary_key_is_item_id(self) -> None:
        pk_cols = [c.name for c in self._table().primary_key.columns]
        assert pk_cols == ["item_id"]

    def test_item_id_is_uuid(self) -> None:
        col = self._table().c["item_id"]
        from sqlalchemy.dialects.postgresql import UUID as PG_UUID
        assert isinstance(col.type, PG_UUID)

    def test_required_text_columns_exist(self) -> None:
        col_names = {c.name for c in self._table().c}
        required = {
            "caps_ref", "grade", "subject", "term", "topic", "subtopic", "skill",
            "stem", "answer_key", "explanation",
            "item_type", "language",
            "difficulty_b", "discrimination_a", "guessing_c", "difficulty_band",
            "review_status", "reviewer_id", "reviewed_at",
            "exposure_count", "max_exposure",
            "quality_score", "safety_passed",
            "source", "created_at", "updated_at",
        }
        missing = required - col_names
        assert not missing, f"Missing columns: {missing}"

    def test_jsonb_columns_exist(self) -> None:
        from sqlalchemy.dialects.postgresql import JSONB
        jsonb_cols = {
            c.name for c in self._table().c
            if isinstance(c.type, JSONB)
        }
        assert "options" in jsonb_cols
        assert "distractor_rationale" in jsonb_cols

    def test_array_column_exists(self) -> None:
        from sqlalchemy.dialects.postgresql import ARRAY
        array_cols = {
            c.name for c in self._table().c
            if isinstance(c.type, ARRAY)
        }
        assert "misconception_tags" in array_cols

    def test_nullable_columns(self) -> None:
        table = self._table()
        for col_name in ("options", "distractor_rationale", "reviewer_id", "reviewed_at", "quality_score"):
            assert table.c[col_name].nullable, f"Column '{col_name}' should be nullable"

    def test_non_nullable_core_columns(self) -> None:
        table = self._table()
        for col_name in ("caps_ref", "grade", "stem", "answer_key", "explanation", "review_status"):
            assert not table.c[col_name].nullable, f"Column '{col_name}' should NOT be nullable"

class TestDiagnosticItemProperties:
    def _make_item(self, **overrides) -> DiagnosticItem:
        defaults = dict(
            item_id=uuid.uuid4(),
            caps_ref="4.M.1.1",
            grade=4,
            subject=SubjectCodeEnum.MATHEMATICS,
            term=1,
            topic="Whole Numbers",
            subtopic="Place value",
            skill="identify_place_value_4digit",
            stem="What is the value of digit 3 in 2 347?",
            answer_key="A",
            explanation="The digit 3 is in the hundreds column, so its value is 300.",
            item_type=ItemTypeEnum.MCQ,
            language=LanguageEnum.EN,
            difficulty_b=0.0,
            discrimination_a=1.0,
            guessing_c=0.25,
            difficulty_band=DifficultyBandEnum.ON_LEVEL,
            review_status=ReviewStatusEnum.DRAFT,
            exposure_count=0,
            max_exposure=50,
            safety_passed=False,
            source=ItemSourceEnum.LLM_GENERATED,
            misconception_tags=[],
        )
        defaults.update(overrides)
        return DiagnosticItem(**defaults)

    def test_is_approved_false_for_draft(self) -> None:
        item = self._make_item(review_status=ReviewStatusEnum.DRAFT)
        assert not item.is_approved

    def test_is_approved_true_for_approved(self) -> None:
        item = self._make_item(
            review_status=ReviewStatusEnum.APPROVED,
            reviewer_id=uuid.uuid4(),
        )
        assert item.is_approved

    def test_is_available_false_when_draft(self) -> None:
        item = self._make_item(review_status=ReviewStatusEnum.DRAFT)
        assert not item.is_available_for_selection

    def test_is_available_false_when_exposure_cap_reached(self) -> None:
        item = self._make_item(
            review_status=ReviewStatusEnum.APPROVED,
            reviewer_id=uuid.uuid4(),
            exposure_count=50,
            max_exposure=50,
        )
        assert not item.is_available_for_selection

    def test_is_available_true_when_approved_and_under_cap(self) -> None:
        item = self._make_item(
            review_status=ReviewStatusEnum.APPROVED,
            reviewer_id=uuid.uuid4(),
            exposure_count=0,
            max_exposure=50,
        )
        assert item.is_available_for_selection

    def test_repr_contains_item_id_prefix(self) -> None:
        item_id = uuid.uuid4()
        item = self._make_item(item_id=item_id)
        assert str(item_id)[:8] in repr(item)

    def test_repr_contains_caps_ref(self) -> None:
        item = self._make_item(caps_ref="4.M.1.1")
        assert "4.M.1.1" in repr(item)

class TestItemExposureColumns:
    def _table(self):
        return ItemExposure.__table__

    def test_tablename(self) -> None:
        assert ItemExposure.__tablename__ == "item_exposures"

    def test_primary_key_is_id(self) -> None:
        pk_cols = [c.name for c in self._table().primary_key.columns]
        assert pk_cols == ["id"]

    def test_required_columns_exist(self) -> None:
        col_names = {c.name for c in self._table().c}
        required = {
            "id", "item_id", "learner_id", "session_id",
            "served_at", "answered_at", "learner_response",
            "is_correct", "response_time_ms",
        }
        missing = required - col_names
        assert not missing, f"Missing columns: {missing}"

class TestRelationships:
    def test_diagnostic_item_has_exposures_relationship(self) -> None:
        mapper = sa_inspect(DiagnosticItem)
        rel_names = {r.key for r in mapper.relationships}
        assert "exposures" in rel_names

    def test_item_exposure_has_item_relationship(self) -> None:
        mapper = sa_inspect(ItemExposure)
        rel_names = {r.key for r in mapper.relationships}
        assert "item" in rel_names

class TestItemCreateSchema:
    def test_valid_mcq_item_parses(self) -> None:
        item = ItemCreate(**VALID_ITEM_DICT)
        assert item.caps_ref == "4.M.1.1"
        assert item.answer_key == "A"

    def test_mcq_requires_options(self) -> None:
        data = {**VALID_ITEM_DICT, "options": []}
        with pytest.raises(ValidationError):
            ItemCreate(**data)

    def test_invalid_caps_ref_format_rejected(self) -> None:
        data = {**VALID_ITEM_DICT, "caps_ref": "Grade4.Maths.Term1"}
        with pytest.raises(ValidationError, match="caps_ref"):
            ItemCreate(**data)

    def test_difficulty_b_out_of_range_rejected(self) -> None:
        data = {**VALID_ITEM_DICT, "difficulty_b": 5.0}
        with pytest.raises(ValidationError):
            ItemCreate(**data)

    def test_discrimination_a_below_minimum_rejected(self) -> None:
        data = {**VALID_ITEM_DICT, "discrimination_a": 0.1}
        with pytest.raises(ValidationError):
            ItemCreate(**data)

    def test_guessing_c_above_maximum_rejected(self) -> None:
        data = {**VALID_ITEM_DICT, "guessing_c": 0.5}
        with pytest.raises(ValidationError):
            ItemCreate(**data)

    def test_missing_stem_rejected(self) -> None:
        data = {k: v for k, v in VALID_ITEM_DICT.items() if k != "stem"}
        with pytest.raises(ValidationError):
            ItemCreate(**data)

    def test_non_mcq_item_without_options_is_valid(self) -> None:
        data = {
            **VALID_ITEM_DICT,
            "item_type": "true_false",
            "options": None,
            "answer_key": "True",
            "distractor_rationale": None,
        }
        item = ItemCreate(**data)
        assert item.item_type == ItemType.TRUE_FALSE

    def test_defaults_applied(self) -> None:
        item = ItemCreate(**VALID_ITEM_DICT)
        assert item.item_type == ItemType.MCQ
        assert item.language == LanguageCode.EN
        assert item.difficulty_b == -0.5
        assert item.discrimination_a == 1.0
        assert item.guessing_c == 0.25
        assert item.max_exposure == 50
        assert item.source == ItemSource.LLM_GENERATED
        assert item.safety_passed is True

class TestMCQOption:
    def test_valid_option(self) -> None:
        opt = MCQOption(label="A", text="300")
        assert opt.label == "A"

    def test_lowercase_label_rejected(self) -> None:
        with pytest.raises(ValidationError, match=r"\^\[A-E\]\$"):
            MCQOption(label="a", text="300")
