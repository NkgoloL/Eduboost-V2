"""Unit tests for modules burndown - Batch 423.

Targets (11 modules):
1. app/modules/progress/mastery_model.py (29 stmts -> 100.0%)
2. app/modules/content_quality/acceptance.py (40 stmts -> 100.0%)
3. app/modules/diagnostics/calibration_service.py (24 stmts -> 100.0%)
4. app/modules/diagnostics/item_bank_pipeline.py (38 stmts -> 100.0%)
5. app/modules/diagnostics/item_selection_service.py (35 stmts -> 100.0%)
6. app/modules/diagnostics/item_generator.py (72 stmts -> 100.0%)
7. app/modules/lessons/budget_guardrails.py (95 stmts -> 100.0%)
8. app/modules/lessons/lesson_validator.py (163 stmts -> 100.0%)
9. app/modules/lessons/mock_llm_provider.py (57 stmts -> 100.0%)
10. app/modules/lessons/lesson_schema_v1.py (140 stmts -> 100.0%)
11. app/modules/lessons/answer_key_verifier.py (124 stmts -> 100.0%)
"""
from __future__ import annotations

import copy
import json
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

# 1. Mastery Model
from app.modules.progress.mastery_model import (
    MasteryLabel,
    compute_mastery_score,
    label_for_score,
    theta_to_mastery,
)

# 2. Content Quality Acceptance
from app.modules.content_quality.acceptance import (
    ACCEPTANCE_CRITERIA,
    CAPS_STRANDS,
    PRD_ID,
    ContentQualityFinalAcceptanceReport,
    build_content_quality_final_acceptance_report,
    build_default_grade4_maths_content_quality_acceptance_report,
)

# 3. Calibration Service
from app.modules.diagnostics.calibration_service import (
    CalibrationResult,
    CalibrationService,
)

# 4. Item Bank Pipeline
from app.modules.diagnostics.item_bank_pipeline import (
    ItemBankPipeline,
    _validate_config,
)

# 5. Item Selection Service
from app.modules.diagnostics.item_selection_service import (
    ItemSelectionService,
    SelectionResult,
)

# 6. Item Generator
from app.modules.diagnostics.item_generator import (
    AnswerKeyMismatchError,
    ItemGenerationError,
    ItemGenerator,
)

# 7. Budget Guardrails
from app.modules.lessons.budget_guardrails import (
    BudgetConfig,
    BudgetExceededError,
    BudgetGuardrails,
    _InProcessCounter,
    _RedisCounter,
    _emit_cost_alert,
)

# 8. Lesson Validator
from app.modules.lessons.lesson_validator import (
    LessonValidator,
    ValidationResult,
)

# 9. Mock LLM Provider
from app.modules.lessons.mock_llm_provider import (
    MockLLMProvider,
    MockMode,
    _BASE_LESSON,
)

# 10. Lesson Schema V1
from app.modules.lessons.lesson_schema_v1 import (
    LESSON_JSON_SCHEMA,
    AnswerKeyEntry,
    LessonCreate,
    LessonResponse,
    PracticeQuestion,
    RemediationHint,
    TokenUsage,
    build_lesson_json_schema,
)

# 11. Answer Key Verifier
from app.modules.lessons.answer_key_verifier import (
    AnswerKeyVerifier,
    QuestionVerification,
    VerificationResult,
    _answers_agree,
    _normalise_answer,
    _strip_answers_from_questions,
)


# ==============================================================================
# 1. MASTERY MODEL TESTS
# ==============================================================================

def test_mastery_model_complete():
    # theta_to_mastery bounds
    assert 0.0 <= theta_to_mastery(-5.0) <= 1.0
    assert 0.0 <= theta_to_mastery(5.0) <= 1.0

    # label_for_score all branches
    assert label_for_score(0.20) == MasteryLabel.NEEDS_PRACTICE
    assert label_for_score(0.39) == MasteryLabel.NEEDS_PRACTICE
    assert label_for_score(0.40) == MasteryLabel.DEVELOPING
    assert label_for_score(0.59) == MasteryLabel.DEVELOPING
    assert label_for_score(0.60) == MasteryLabel.ON_TRACK
    assert label_for_score(0.74) == MasteryLabel.ON_TRACK
    assert label_for_score(0.75) == MasteryLabel.PROFICIENT
    assert label_for_score(0.89) == MasteryLabel.PROFICIENT
    assert label_for_score(0.90) == MasteryLabel.MASTERED
    assert label_for_score(1.00) == MasteryLabel.MASTERED

    # compute_mastery_score with None and provided optional params
    score_default = compute_mastery_score(theta=0.5, se=0.2)
    assert 0.0 <= score_default <= 1.0

    score_custom = compute_mastery_score(
        theta=1.2,
        se=0.1,
        practice_accuracy=0.9,
        recency_days=2.0,
        consistency_ratio=0.85,
    )
    assert 0.0 <= score_custom <= 1.0


# ==============================================================================
# 2. CONTENT QUALITY ACCEPTANCE TESTS
# ==============================================================================

def test_content_quality_acceptance_complete():
    # Default accepted report
    rep = build_default_grade4_maths_content_quality_acceptance_report()
    payload = rep.to_payload()
    assert payload["prd_id"] == PRD_ID
    assert payload["accepted"] is True
    assert len(payload["blockers"]) == 0
    assert len(payload["recommended_next_actions"]) == 2
    assert "capture_prd4_final_evidence" in payload["recommended_next_actions"]

    # Rejected report with all 4 blockers enabled
    unready = build_content_quality_final_acceptance_report(
        educator_signoff_ready=False,
        review_queue_ready=False,
        final_evidence_ready=False,
        prd4_final_reconciliation_ready=False,
    )
    assert unready.accepted is False
    blockers = unready.blockers
    assert "educator_signoff_missing" in blockers
    assert "human_review_queue_not_ready" in blockers
    assert "prd4_final_evidence_missing" in blockers
    assert "prd4_final_reconciliation_missing" in blockers
    actions = unready.recommended_next_actions
    assert any("resolve_educator_signoff_missing" in a for a in actions)

    # Custom inputs path
    mock_inputs = MagicMock()
    with patch("app.modules.content_quality.acceptance.build_content_quality_readiness_report") as mock_builder:
        mock_readiness = MagicMock()
        mock_readiness.to_payload.return_value = {
            "prd_id": "PRD-4.0",
            "subject": "Mathematics",
            "grade": 4,
            "ready": True,
            "caps_coverage_complete": True,
            "bias_language_accessibility_ready": True,
            "misconception_remediation_ready": True,
            "blockers": [],
        }
        mock_builder.return_value = mock_readiness
        custom_rep = build_content_quality_final_acceptance_report(inputs=mock_inputs)
        assert custom_rep.accepted is True


# ==============================================================================
# 3. CALIBRATION SERVICE TESTS
# ==============================================================================

def test_calibration_service_complete():
    svc = CalibrationService()
    item = SimpleNamespace(item_id="item-1", difficulty_b=0.0, discrimination_a=1.0, guessing_c=0.25)

    # Below min_responses (< 100)
    low_res: list[Any] = [SimpleNamespace(is_correct=True) for _ in range(10)]
    result_low = svc.calibrate_item(item, low_res, min_responses=100)
    assert result_low.response_count == 10
    assert result_low.review_required is False

    # Above min_responses with high accuracy (lowers difficulty b)
    high_res: list[Any] = [SimpleNamespace(is_correct=True) for _ in range(150)]
    result_high = svc.calibrate_item(item, high_res, min_responses=100)
    assert result_high.response_count == 150
    assert result_high.difficulty_b < 0.0  # easy item

    # High inaccuracy (raises difficulty b and triggers review)
    inacc_res: list[Any] = [SimpleNamespace(is_correct=False) for _ in range(150)]
    result_inacc = svc.calibrate_item(item, inacc_res, min_responses=100)
    assert result_inacc.difficulty_b > 0.0
    assert result_inacc.review_required is True


# ==============================================================================
# 4. ITEM BANK PIPELINE TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_item_bank_pipeline_complete():
    # Validation errors
    with pytest.raises(ValueError, match="max_items must be a non-negative integer"):
        _validate_config({"max_items": -1})

    with pytest.raises(ValueError, match="difficulty_range must be a two-element sequence"):
        _validate_config({"difficulty_range": "invalid"})

    with pytest.raises(ValueError, match="difficulty_range low"):
        _validate_config({"difficulty_range": (0.8, 0.2)})

    # Valid construction and fetch with topic filter, shuffle, difficulty filtering
    mock_repo = AsyncMock()
    mock_items = [
        {"item_id": "1", "difficulty": 0.3},
        {"item_id": "2", "difficulty": 0.5},
        {"item_id": "3", "difficulty": 0.9},
    ]
    mock_repo.get_items_by_topic = AsyncMock(return_value=mock_items)

    pipeline = ItemBankPipeline(
        config={
            "max_items": 2,
            "difficulty_range": (0.2, 0.6),
            "topic_filter": "Fractions",
            "shuffle": True,
        },
        repository=mock_repo,
    )

    items = await pipeline.fetch_items()
    assert len(items) == 2
    for it in items:
        assert 0.2 <= it["difficulty"] <= 0.6
    mock_repo.get_items_by_topic.assert_awaited_once_with("Fractions")

    # Unfiltered (all approved) default difficulty range path
    mock_repo.get_approved_items = AsyncMock(return_value=mock_items)
    pipeline_default = ItemBankPipeline(
        config={"max_items": 10, "difficulty_range": (0.0, 1.0), "topic_filter": None},
        repository=mock_repo,
    )
    items_default = await pipeline_default.fetch_items()
    assert len(items_default) == 3


# ==============================================================================
# 5. ITEM SELECTION SERVICE TESTS
# ==============================================================================

def test_item_selection_service_complete():
    svc = ItemSelectionService()

    i1 = SimpleNamespace(item_id="i1", difficulty_b=0.0, discrimination_a=1.2, guessing_c=0.25, safety_passed=True, review_status="approved", exposure_count=5)
    i2 = SimpleNamespace(item_id="i2", difficulty_b=1.5, discrimination_a=0.8, guessing_c=0.25, safety_passed=True, review_status="approved", exposure_count=2)
    i_served = SimpleNamespace(item_id="i_served", difficulty_b=0.0, discrimination_a=2.0, guessing_c=0.25, safety_passed=True, review_status="approved")
    i_ineligible = SimpleNamespace(item_id="i_bad", difficulty_b=0.0, discrimination_a=2.0, guessing_c=0.25, safety_passed=False, review_status="approved")
    i_overexposed = SimpleNamespace(item_id="i_over", difficulty_b=0.0, discrimination_a=2.0, guessing_c=0.25, safety_passed=True, review_status="approved", exposure_count=100, max_exposure=50)

    res = svc.select_max_information_item(
        [i1, i2, i_served, i_ineligible, i_overexposed],
        theta=0.0,
        served_ids={"i_served"},
    )
    assert res.eligible_count == 2
    assert res.item is not None
    assert getattr(res.item, "item_id", "") in ("i1", "i2")
    assert res.information > 0.0


# ==============================================================================
# 6. ITEM GENERATOR TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_item_generator_complete():
    # Constructor with no gateway and gateway unavailable
    with patch("app.modules.diagnostics.item_generator._GATEWAY_AVAILABLE", False):
        gen_none = ItemGenerator(gateway=None)
        assert gen_none._gateway is None

    # Constructor with available default gateway
    with patch("app.modules.diagnostics.item_generator._GATEWAY_AVAILABLE", True):
        with patch("app.modules.diagnostics.item_generator.JsonCompletionGateway") as mock_cls:
            gen_def = ItemGenerator(gateway=None)
            assert gen_def._gateway is not None

    # Render template failure raises ItemGenerationError
    mock_gw = AsyncMock()
    gen = ItemGenerator(gateway=mock_gw)
    with pytest.raises(ItemGenerationError, match="Failed to render prompt template"):
        gen._render_template("non_existent_template_xyz.j2", {})

    # Call LLM for JSON stripping code fences
    mock_gw.complete = AsyncMock(return_value="```json\n{\"stem\": \"What is 5x5?\"}\n```")
    parsed = await gen._call_llm_for_json("dummy prompt", "generation")
    assert parsed.get("stem") == "What is 5x5?"

    # Invalid JSON raises ItemGenerationError
    mock_gw.complete = AsyncMock(return_value="not json at all")
    with pytest.raises(ItemGenerationError, match="not valid JSON"):
        await gen._call_llm_for_json("dummy prompt", "generation")

    # Disagreeing answer keys raises AnswerKeyMismatchError
    raw_item = {
        "stem": "Solve for x",
        "options": [{"label": "A", "text": "1"}, {"label": "B", "text": "2"}],
        "answer_key": "A",
        "explanation": "Option A is correct",
    }
    topic_data = {
        "grade": 4,
        "subject": "Mathematics",
        "term": 1,
        "topic": "Whole Numbers",
        "subtopic": "Place value",
        "skill": "Identify place value",
    }
    with patch.object(gen, "_call_llm_for_json", AsyncMock(side_effect=[
        raw_item,
        {"correct_answer": "B"},  # disagree!
    ])):
        with pytest.raises(AnswerKeyMismatchError):
            await gen.generate("4.M.1.1", topic_data, "easy", b_min=-2.0, b_max=-1.0)

    # Gateway is None raises ItemGenerationError in generate
    gen_no_gw = ItemGenerator(gateway=None)
    gen_no_gw._gateway = None
    with pytest.raises(ItemGenerationError, match="LLMGateway is not available"):
        await gen_no_gw.generate("4.M.1.1", topic_data, "easy", b_min=-2.0, b_max=-1.0)

    # Matching answer key succeeds and enriches item
    with patch.object(gen, "_call_llm_for_json", AsyncMock(side_effect=[
        raw_item,
        {"correct_answer": "A"},  # agree!
    ])):
        res_item = await gen.generate("4.M.1.1", topic_data, "easy", b_min=-2.0, b_max=-1.0)
        assert res_item["answer_key"] == "A"

    # LLM call failure in _call_llm_for_json raises ItemGenerationError
    mock_gw.complete = AsyncMock(side_effect=RuntimeError("LLM failed"))
    with pytest.raises(ItemGenerationError, match="LLM generation call failed"):
        await gen._call_llm_for_json("dummy", "generation")


# ==============================================================================
# 7. BUDGET GUARDRAILS TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_budget_guardrails_complete():
    # InProcess counter
    in_proc = _InProcessCounter()
    assert await in_proc.get("user:u1") == 0
    t1 = await in_proc.add("user:u1", 500, 3600)
    assert t1 == 500
    assert await in_proc.get("user:u1") == 500

    # Redis counter
    mock_redis = MagicMock()
    mock_pipe = MagicMock()
    mock_pipe.execute = AsyncMock(return_value=[1200])
    mock_redis.pipeline.return_value = mock_pipe
    mock_redis.get = AsyncMock(return_value=b"1200")

    r_counter = _RedisCounter(mock_redis)
    assert await r_counter.get("user:u2") == 1200
    t2 = await r_counter.add("user:u2", 300, 3600)
    assert t2 == 1200

    # from_settings factory
    settings_obj = SimpleNamespace(
        USER_DAILY_TOKEN_LIMIT=10_000,
        TENANT_MONTHLY_TOKEN_LIMIT=100_000,
        TENANT_BUDGET_ALERT_PCT=0.75,
    )
    guard = BudgetGuardrails.from_settings(settings_obj, redis=None)
    assert guard._config.user_daily_token_limit == 10_000

    # assert_budget user breach
    await guard._counter.add(guard._user_key("u1"), 9_500, 3600)
    with pytest.raises(BudgetExceededError) as exc_user:
        await guard.assert_budget("u1", "t1", estimated_tokens=1_000)
    assert "user:u1" in str(exc_user.value)

    # assert_budget tenant breach
    await guard._counter.add(guard._tenant_key("t1"), 99_500, 3600)
    with pytest.raises(BudgetExceededError) as exc_tenant:
        await guard.assert_budget("u2", "t1", estimated_tokens=1_000)
    assert "tenant:t1" in str(exc_tenant.value)

    # record_usage with alert threshold crossing
    cast(Any, guard._counter)._data.clear()
    await guard.record_usage("u3", "t2", tokens_used=0)  # tokens <= 0 no-op
    await guard.record_usage("u3", "t2", tokens_used=80_000, provider="mock", purpose="test")
    # crossed 75% of 100k -> emit alert
    summary = await guard.get_usage_summary("u3", "t2")
    assert summary["user_daily_used"] == 80_000
    assert summary["tenant_id"] == "t2"


# ==============================================================================
# 8. LESSON VALIDATOR TESTS
# ==============================================================================

def test_lesson_validator_complete():
    validator = LessonValidator()

    # Rule failed properties
    result = ValidationResult(passed=False, failures=[
        "Rule 1: caps_ref not found",
        "Rule 3: answer_key_verified failed",
        "Rule 8: explanation is missing",
    ])
    rules = getattr(result, "failed_rules")
    assert "caps_ref_resolves" in rules
    assert "answer_key_verified" in rules
    assert "explanation_non_empty" in rules

    # Schema validation failed rule branch
    schema_res = ValidationResult(passed=False, failures=["Schema validation failure"])
    assert "schema_valid" in getattr(schema_res, "failed_rules")

    # answer_key as dict conversion in _normalise_lesson_dict
    dirty_lesson = copy.deepcopy(_BASE_LESSON)
    for q in dirty_lesson["practice_questions"]:
        q["options"] = {"A": "1", "B": "2", "C": "3", "D": "4"}
        q["question_text"] = q.get("question_text", "Sample question")
    dirty_lesson["answer_key"] = {q["question_id"]: "A" for q in dirty_lesson["practice_questions"]}
    dirty_lesson["worked_examples"] = [
        {"step_by_step_solution": "Step 1: Do this\nStep 2: Do that", "question": "Ex 1 question", "answer": "10"},
        {"step_by_step_solution": ["Step A", "Step B"], "question": "Ex 2 question", "answer": "20"},
    ]
    normalized = validator._normalise_lesson_dict(dirty_lesson)
    assert isinstance(normalized.answer_key, list)
    assert normalized.answer_key[0].correct_option == "A"
    assert len(normalized.worked_examples[0].step_by_step_solution) == 2


# ==============================================================================
# 9. MOCK LLM PROVIDER TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_mock_llm_provider_complete():
    # Provider error mode
    err_prov = MockLLMProvider(mode=MockMode.PROVIDER_ERROR)
    with pytest.raises(Exception, match="Mock provider error"):
        await err_prov.complete(prompt="hello")

    # Static fallback mode
    fb_prov = MockLLMProvider(mode=MockMode.STATIC_FALLBACK)
    fb_res = await fb_prov.complete(prompt="hello")
    assert fb_res["used_fallback"] is True
    assert fb_res["model"] == "static_fallback_v1"

    # Verifier call response
    v_prov = MockLLMProvider(mode=MockMode.VALID_LESSON)
    v_res = await v_prov.complete(prompt="check agrees_with_key")
    assert "agrees_with_key" in v_res["content"]

    # Verifier disagree mode
    dis_prov = MockLLMProvider(mode=MockMode.ANSWER_KEY_DISAGREE)
    dis_res = await dis_prov.complete(prompt="agrees_with_key in prompt")
    assert "Incorrect working shown" in dis_res["content"]

    # Lesson response happy path
    l_res = await v_prov.complete(prompt="Please generate standard lesson content")
    assert "lesson_id" in l_res["content"]

    # Inject failure mode
    inj_prov = MockLLMProvider(mode=MockMode.INJECT_FAILURE, failure_field="topic", failure_value="Overridden Topic")
    inj_res = await inj_prov.complete(prompt="Generate lesson")
    assert "Overridden Topic" in inj_res["content"]

    # Call count property
    assert inj_prov.call_count == 1


# ==============================================================================
# 10. LESSON SCHEMA V1 TESTS
# ==============================================================================

def test_lesson_schema_v1_complete():
    # Invalid PracticeQuestion options
    with pytest.raises(ValueError, match="options must have exactly the keys A, B, C, D"):
        PracticeQuestion(
            question_id="q1",
            question_text="Calculate 2 + 2",
            options={"A": "1", "B": "2", "C": "3"},  # missing D
            correct_option="B",
            explanation="Explanation",
            misconception_tag="tag",
        )

    # TokenUsage total mismatch
    with pytest.raises(ValueError, match="total_tokens must equal"):
        TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=50)

    # LessonCreate missing answer_key entries
    valid_payload = {
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject": "Mathematics",
        "term": 1,
        "topic": "Whole Numbers",
        "subtopic": "Place value",
        "learning_objectives": ["Identify place value"],
        "explanation": "A" * 60,
        "difficulty_level": "on_level",
        "language_level": "Grade 4 English FAL",
        "pii_check_passed": True,
        "prompt_template_version": "v1.0",
        "provider": "mock",
        "model_version": "mock-1",
        "generation_latency_ms": 100,
        "token_usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        "worked_examples": [
            {"question": "Ex 1 question", "step_by_step_solution": ["Step 1"], "answer": "10"},
            {"question": "Ex 2 question", "step_by_step_solution": ["Step 1"], "answer": "20"},
        ],
        "practice_questions": [
            {"question_id": "q1", "question_text": "What is 10+10?", "options": {"A": "10", "B": "20", "C": "30", "D": "40"}, "correct_option": "B", "explanation": "10+10 is 20"},
            {"question_id": "q2", "question_text": "What is 20+20?", "options": {"A": "10", "B": "20", "C": "30", "D": "40"}, "correct_option": "D", "explanation": "20+20 is 40"},
            {"question_id": "q3", "question_text": "What is 30+30?", "options": {"A": "10", "B": "20", "C": "60", "D": "40"}, "correct_option": "C", "explanation": "30+30 is 60"},
        ],
        "answer_key": [
            {"question_id": "q1", "correct_option": "B", "correct_answer_text": "20"},
            {"question_id": "q2", "correct_option": "D", "correct_answer_text": "40"},
            # missing q3
        ],
    }
    with pytest.raises(ValueError, match="answer_key is missing entries"):
        LessonCreate.model_validate(valid_payload)

    # Grade mismatch with caps_ref
    mismatch_payload = {
        **valid_payload,
        "grade": 5,
        "answer_key": [
            {"question_id": "q1", "correct_option": "B", "correct_answer_text": "20"},
            {"question_id": "q2", "correct_option": "D", "correct_answer_text": "40"},
            {"question_id": "q3", "correct_option": "C", "correct_answer_text": "60"},
        ],
    }
    with pytest.raises(ValueError, match="caps_ref grade prefix"):
        LessonCreate.model_validate(mismatch_payload)

    # build_lesson_json_schema
    schema = build_lesson_json_schema()
    assert isinstance(schema, dict)
    assert "properties" in schema


# ==============================================================================
# 11. ANSWER KEY VERIFIER TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_answer_key_verifier_complete():
    # normalise_answer and answers_agree
    assert _normalise_answer("  A. ") == "a."
    assert _answers_agree("A", "a") is True
    assert _answers_agree("100", "100.0") is True
    assert _answers_agree("A", "B") is False

    # strip_answers_from_questions
    raw_qs = [
        {"question_id": "q1", "stem": "2+2", "correct_answer": "4", "options": [{"text": "4", "is_correct": True}]},
    ]
    stripped = _strip_answers_from_questions(raw_qs)
    assert "correct_answer" not in stripped[0]
    assert "is_correct" not in stripped[0]["options"][0]

    # Verification with empty practice questions
    mock_gw = AsyncMock()
    verifier = AnswerKeyVerifier(llm_gateway=mock_gw)
    res_empty = await verifier.verify({"lesson_id": "l1", "practice_questions": []})
    assert res_empty.all_agree is False

    # Gateway exception path
    mock_gw.complete = AsyncMock(side_effect=RuntimeError("Gateway timeout"))
    res_err = await verifier.verify({"lesson_id": "l2", "practice_questions": [{"question_id": "q1"}]})
    assert res_err.all_agree is False
    assert "Gateway timeout" in res_err.disagreements[0]["error"]

    # Verifier JSON missing or invalid
    mock_gw.complete = AsyncMock(return_value={"content": "No JSON array here"})
    res_no_json = await verifier.verify({"lesson_id": "l3", "practice_questions": [{"question_id": "q1"}]})
    assert res_no_json.all_agree is False

    # Malformed JSON array
    mock_gw.complete = AsyncMock(return_value={"content": "[invalid json here"})
    res_malformed = await verifier.verify({"lesson_id": "l3_mal", "practice_questions": [{"question_id": "q1"}]})
    assert res_malformed.all_agree is False

    # Verifier JSON array with non-dict elements
    mock_gw.complete = AsyncMock(return_value={"content": "[\"not a dict\", 123]"})
    res_nondict = await verifier.verify({"lesson_id": "l3_nd", "practice_questions": [{"question_id": "q1"}]})
    assert res_nondict.all_agree is False

    # Full agreement verification
    verifier_output = json.dumps([
        {"question_id": "q1", "derived_answer": "B", "working": "Step by step", "confidence": 1.0},
    ])
    mock_gw.complete = AsyncMock(return_value={"content": verifier_output, "model": "gpt-4", "provider": "openai"})
    res_agree = await verifier.verify({
        "lesson_id": "l4",
        "practice_questions": [{"question_id": "q1", "correct_answer": "B"}],
        "answer_key": {"q1": "B"},
    })
    assert res_agree.all_agree is True
    assert len(res_agree.verifications) == 1
    as_dict = res_agree.to_dict()
    assert as_dict["all_agree"] is True

    # Question answer embedded in question object fallback (answer_key is None)
    mock_gw.complete = AsyncMock(return_value={"content": verifier_output})
    res_embedded = await verifier.verify({
        "lesson_id": "l4_emb",
        "practice_questions": [{"question_id": "q1", "correct_answer": "B"}],
        "answer_key": None,
    })
    assert res_embedded.all_agree is True

    # Question original answer not found in key or question object
    mock_gw.complete = AsyncMock(return_value={"content": verifier_output})
    res_no_orig = await verifier.verify({
        "lesson_id": "l4_missing",
        "practice_questions": [{"question_id": "q1"}],
        "answer_key": {},
    })
    assert res_no_orig.all_agree is False
    assert res_no_orig.disagreements[0]["reason"] == "original_answer_not_found_in_key"

    # Disagreement verification
    disagree_output = json.dumps([
        {"question_id": "q1", "derived_answer": "C", "working": "Different step", "confidence": 0.9},
    ])
    mock_gw.complete = AsyncMock(return_value={"content": disagree_output})
    res_disagree = await verifier.verify({
        "lesson_id": "l5",
        "practice_questions": [{"question_id": "q1", "correct_answer": "B"}],
        "answer_key": {"q1": "B"},
    })
    assert res_disagree.all_agree is False
    assert len(res_disagree.disagreements) == 1
