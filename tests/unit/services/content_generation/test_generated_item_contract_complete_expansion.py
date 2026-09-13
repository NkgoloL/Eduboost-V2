import pytest

from app.services.content_generation.generated_item_contract import (
    GeneratedItemQualityIssue,
    GeneratedItemQualityResult,
    GeneratedItemQualityValidator,
)


def _build_valid_item(**kwargs) -> dict:
    item = {
        "item_id": "item_001",
        "caps_ref": "CAPS.MATH.G4.T1",
        "stem": "What is 15 multiplied by 4?",
        "options": [
            {"label": "A", "text": "60"},
            {"label": "B", "text": "50"},
            {"label": "C", "text": "45"},
            {"label": "D", "text": "40"},
        ],
        "answer_key": "A",
        "explanation": "15 * 4 = 60.",
        "difficulty_band": "on_level",
        "source": "scope_item_generator_v2",
    }
    item.update(kwargs)
    return item


def test_validate_item_valid():
    validator = GeneratedItemQualityValidator()
    item = _build_valid_item()
    issues = validator.validate_item(item)
    assert issues == []


def test_validate_item_all_issues():
    validator = GeneratedItemQualityValidator()

    # 1. Missing stem
    item_no_stem = _build_valid_item(stem="")
    issues = validator.validate_item(item_no_stem)
    assert any(i.field == "stem" and "missing" in i.reason for i in issues)

    # 2. Generic stem
    item_gen_stem = _build_valid_item(stem="What should you do first?")
    issues = validator.validate_item(item_gen_stem)
    assert any(i.field == "stem" and "generic" in i.reason for i in issues)

    # 3. Fewer than 4 options
    item_few_opts = _build_valid_item(options=[{"label": "A", "text": "1"}])
    issues = validator.validate_item(item_few_opts)
    assert any(i.field == "options" and "fewer than four" in i.reason for i in issues)

    # 4. Duplicate option text
    item_dup_opts = _build_valid_item(options=[
        {"label": "A", "text": "dup"},
        {"label": "B", "text": "dup"},
        {"label": "C", "text": "other1"},
        {"label": "D", "text": "other2"},
    ])
    issues = validator.validate_item(item_dup_opts)
    assert any(i.field == "options" and "duplicate" in i.reason for i in issues)

    # 5. answer_key not in labels
    item_bad_key = _build_valid_item(answer_key="Z")
    issues = validator.validate_item(item_bad_key)
    assert any(i.field == "answer_key" and "not in option labels" in i.reason for i in issues)

    # 6. Generic option patterns
    item_gen_opt = _build_valid_item(options=[
        {"label": "A", "text": "the answer follows the given facts in the question"},
        {"label": "B", "text": "the answer guesses without checking"},
        {"label": "C", "text": "the answer ignores the topic words"},
        {"label": "D", "text": "the answer changes the order before solving"},
    ])
    issues = validator.validate_item(item_gen_opt)
    assert any(i.field == "options" and "generic study-behaviour" in i.reason for i in issues)

    # 7. Missing explanation
    item_no_exp = _build_valid_item(explanation="   ")
    issues = validator.validate_item(item_no_exp)
    assert any(i.field == "explanation" and "missing" in i.reason for i in issues)

    # 8. Unsupported difficulty band
    item_bad_band = _build_valid_item(difficulty_band="ultra_hard")
    issues = validator.validate_item(item_bad_band)
    assert any(i.field == "difficulty_band" and "unsupported" in i.reason for i in issues)

    # 9. Legacy source
    item_scaffold = _build_valid_item(source="scope_scaffold")
    issues = validator.validate_item(item_scaffold)
    assert any(i.field == "source" and "legacy" in i.reason for i in issues)


def test_validate_file_payload():
    validator = GeneratedItemQualityValidator()

    # Valid payload
    payload_valid = {
        "items": [
            _build_valid_item(item_id="i1", stem="Stem one"),
            _build_valid_item(item_id="i2", stem="Stem two"),
        ]
    }
    res_valid = validator.validate_file_payload(payload_valid)
    assert res_valid.passed is True
    assert res_valid.item_count == 2
    assert res_valid.failed_item_count == 0
    assert len(res_valid.issues) == 0

    # Payload with duplicate stem in same caps_ref
    payload_dup = {
        "items": [
            _build_valid_item(item_id="i1", caps_ref="C1", stem="Duplicate stem"),
            _build_valid_item(item_id="i2", caps_ref="C1", stem="Duplicate stem"),
        ]
    }
    res_dup = validator.validate_file_payload(payload_dup)
    assert res_dup.passed is False
    assert any("duplicate stem" in i.reason for i in res_dup.issues)

    # Empty payload
    res_empty = validator.validate_file_payload({})
    assert res_empty.passed is True
    assert res_empty.item_count == 0
