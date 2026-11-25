from app.services.content_generation.scope_blueprint_generator import ScopeBlueprintGenerator
from app.services.content_generation.scope_item_generator import ScopeItemGenerator
from app.services.content_generation.scope_lesson_generator import ScopeLessonGenerator
from app.services.content_generation.topic_map_source_context import TopicMapSourceContext


def context():
    return TopicMapSourceContext(
        scope_id="grade4_mathematics_en",
        caps_ref="4.M.1.1",
        grade=4,
        phase="Intermediate",
        subject="Mathematics",
        subject_code="MATH",
        language="en",
        topic="Whole Numbers",
        subtopic="Place value",
        term=1,
        weeks="1-2",
        assessment_standards=("Represent four-digit numbers in different ways.",),
        learning_outcomes=("Read and represent numbers.",),
        prerequisites=(),
        common_misconceptions=("Confusing tens and hundreds.",),
        vocabulary=("place value",),
        source_document_ids=("caps-grade4-maths",),
        source_text_snippets=("Learners represent, compare, order and describe numbers.",),
        context_hash="a" * 64,
    )


def test_item_generator_never_self_approves():
    item = ScopeItemGenerator().generate(context(), index=0, band="on_level", scope_id="grade4_mathematics_en")
    assert item["review_status"] == "ai_generated"
    assert item["reviewer_id"] is None


def test_lesson_generator_never_self_approves():
    lesson = ScopeLessonGenerator().generate(context(), index=0)
    assert lesson["review_status"] == "ai_generated"
    assert lesson["reviewer_id"] is None
    assert lesson["reviewed_at"] is None
    assert lesson["trust_label"]["teacher_reviewed"] is False


def test_blueprint_generator_never_self_approves():
    generated = ScopeBlueprintGenerator().generate(
        "grade4_mathematics_en",
        ["4.M.1.1"],
        {"4.M.1.1": {"subject": "Mathematics", "grade": 4, "topic": "Whole Numbers", "subtopic": "Place value"}},
    )
    assert generated["blueprints"]
    assert all(row["review_status"] == "ai_generated" for row in generated["blueprints"])


def test_legacy_generator_review_policy_never_self_approves():
    from scripts.generate_items import apply_review_policy

    class PassingValidator:
        def validate_all(self, item):
            return []

    class HighScoring:
        def score(self, item):
            return {
                **item,
                "safety_passed": True,
                "quality_score": 0.99,
                "review_status": "approved",
                "reviewer_id": "00000000-0000-0000-0000-000000000002",
                "reviewed_at": "2026-01-01T00:00:00Z",
            }

    result = apply_review_policy({"item_id": "candidate"}, PassingValidator(), HighScoring())
    assert result["review_status"] == "ai_generated"
    assert result["reviewer_id"] is None
    assert result["reviewed_at"] is None


def test_item_bank_seeder_rejects_synthetic_approval():
    from scripts.seed_item_bank import filter_items
    import pytest

    with pytest.raises(ValueError, match="non-synthetic reviewer_id"):
        filter_items(
            [{
                "item_id": "legacy-item",
                "review_status": "approved",
                "reviewer_id": "00000000-0000-0000-0000-000000000001",
                "reviewed_at": "2026-01-01T00:00:00Z",
            }],
            "approved",
        )


def test_item_bank_seeder_rejects_approval_without_review_timestamp():
    from scripts.seed_item_bank import filter_items
    import pytest

    with pytest.raises(ValueError, match="non-synthetic reviewer_id"):
        filter_items(
            [{
                "item_id": "unreviewed-item",
                "review_status": "approved",
                "reviewer_id": "fbd3a466-490e-49c0-a2e5-593d82b0f9b4",
            }],
            "approved",
        )


def test_seeder_requires_external_independent_approval_register(tmp_path):
    import pytest
    from scripts.seed_item_bank import validate_external_review_register

    approved = [{
        "item_id": "reviewed-item",
        "review_status": "approved",
        "reviewer_id": "fbd3a466-490e-49c0-a2e5-593d82b0f9b4",
        "reviewed_at": "2026-11-23T12:00:00Z",
    }]
    with pytest.raises(ValueError, match="register is absent"):
        validate_external_review_register(approved, tmp_path / "missing.json")

    register = tmp_path / "register.json"
    register.write_text(
        '{"entries":[{"item_id":"reviewed-item","reviewer_id":"fbd3a466-490e-49c0-a2e5-593d82b0f9b4","independent":false,"decision":"approved"}]}'
    )
    with pytest.raises(ValueError, match="matching independent approval"):
        validate_external_review_register(approved, register)

    register.write_text(
        '{"entries":[{"item_id":"reviewed-item","reviewer_id":"fbd3a466-490e-49c0-a2e5-593d82b0f9b4","independent":true,"decision":"approved"}]}'
    )
    validate_external_review_register(approved, register)


def test_review_service_rejects_known_synthetic_reviewer():
    import asyncio
    import uuid
    import pytest
    from app.modules.diagnostics.item_bank_service import ItemBankService

    service = ItemBankService(repo=object())
    with pytest.raises(ValueError, match="synthetic reviewer"):
        asyncio.run(service.mark_item_reviewed(
            item_id=uuid.uuid4(),
            new_status="approved",
            reviewer_id="00000000-0000-0000-0000-000000000001",
        ))


def test_lesson_seeder_requires_external_review_register(tmp_path):
    import pytest
    from scripts.lessons.seed_lesson_bank import validate_lesson_review_register

    lessons = [{
        "lesson_id": "lesson-1",
        "review_status": "approved",
        "reviewer_id": "fbd3a466-490e-49c0-a2e5-593d82b0f9b4",
        "reviewed_at": "2026-11-23T12:00:00Z",
    }]
    with pytest.raises(ValueError, match="register is absent"):
        validate_lesson_review_register(lessons, tmp_path / "missing.json")


def test_item_seeder_rejects_generated_records_even_when_explicitly_selected():
    import pytest
    from scripts.seed_item_bank import require_approved_for_seeding

    with pytest.raises(ValueError, match="non-approved item"):
        require_approved_for_seeding([{"item_id": "candidate", "review_status": "ai_generated"}])


def test_lesson_seeder_rejects_generated_records():
    import pytest
    from pathlib import Path
    from scripts.lessons.seed_lesson_bank import validate_lesson_review_register

    with pytest.raises(ValueError, match="non-approved lesson"):
        validate_lesson_review_register(
            [{"lesson_id": "candidate", "review_status": "ai_generated"}],
            Path("absent"),
        )
