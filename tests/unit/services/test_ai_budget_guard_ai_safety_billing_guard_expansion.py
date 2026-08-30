"""Batch 192: Unit tests for ai_budget_guard, ai_safety, and billing_guard services."""
import json
import re
import tempfile
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.services.ai_budget_guard import (
    AIBudgetExceededError,
    AIBudgetGuard,
    DEFAULT_MAX_TOKENS_PER_REQUEST,
    DEFAULT_DAILY_TOKEN_BUDGET,
)
from app.services.ai_safety import (
    ContentQualityScore,
    redact_pii,
    redact_pii_text,
    score_lesson_quality,
)
from app.services.billing_guard import (
    BillingLockError,
    assert_billing_authorized,
    check_live_billing_authorization,
    sanitize_billing_webhook,
)


# ─────────────────────────────────────────────
# AIBudgetGuard
# ─────────────────────────────────────────────


class TestAIBudgetGuard:
    def test_defaults(self):
        guard = AIBudgetGuard()
        assert guard.max_tokens_per_request == DEFAULT_MAX_TOKENS_PER_REQUEST
        assert guard.daily_budget == DEFAULT_DAILY_TOKEN_BUDGET
        assert guard._current_usage == 0

    def test_check_and_reserve_success(self):
        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=5000)
        used = guard.check_and_reserve(500)
        assert used == 500
        used2 = guard.check_and_reserve(300)
        assert used2 == 800

    def test_check_and_reserve_zero_raises_value_error(self):
        guard = AIBudgetGuard()
        with pytest.raises(ValueError, match="positive"):
            guard.check_and_reserve(0)

    def test_check_and_reserve_negative_raises_value_error(self):
        guard = AIBudgetGuard()
        with pytest.raises(ValueError):
            guard.check_and_reserve(-10)

    def test_exceeds_per_request_limit(self):
        guard = AIBudgetGuard(max_tokens_per_request=100, daily_budget=10000)
        with pytest.raises(AIBudgetExceededError) as exc_info:
            guard.check_and_reserve(101)
        assert exc_info.value.status_code == 429
        assert "single-request limit" in str(exc_info.value.detail)

    def test_exceeds_daily_budget(self):
        guard = AIBudgetGuard(max_tokens_per_request=600, daily_budget=800)
        guard.check_and_reserve(500)
        with pytest.raises(AIBudgetExceededError) as exc_info:
            guard.check_and_reserve(400)
        assert exc_info.value.status_code == 429
        assert "Daily AI budget exhausted" in str(exc_info.value.detail)

    def test_reset_usage(self):
        guard = AIBudgetGuard(max_tokens_per_request=500, daily_budget=2000)
        guard.check_and_reserve(300)
        assert guard._current_usage == 300
        guard.reset_usage()
        assert guard._current_usage == 0
        # Can reserve again after reset
        guard.check_and_reserve(300)
        assert guard._current_usage == 300

    def test_ai_budget_exceeded_error_is_http_exception(self):
        err = AIBudgetExceededError()
        assert isinstance(err, HTTPException)
        assert err.status_code == 429
        assert "Retry-After" in err.headers
        assert err.headers["X-AI-Budget-Status"] == "EXCEEDED"

    def test_custom_error_detail(self):
        err = AIBudgetExceededError("custom message")
        assert err.detail == "custom message"


# ─────────────────────────────────────────────
# ai_safety - PII redaction
# ─────────────────────────────────────────────


class TestRedactPii:
    def test_email_redacted(self):
        result = redact_pii_text("Contact user@example.com for support")
        assert "[redacted-email]" in result
        assert "user@example.com" not in result

    def test_sa_phone_redacted(self):
        result = redact_pii_text("Call me on 0821234567 for details")
        assert "[redacted-phone]" in result

    def test_sa_id_number_redacted(self):
        result = redact_pii_text("My ID is 9001015009087 please")
        assert "[redacted-id-number]" in result

    def test_clean_text_unchanged(self):
        text = "The answer is 42. Well done!"
        assert redact_pii(text) == text

    def test_redact_pii_list(self):
        result = redact_pii(["user@example.com", "safe text"])
        assert result[0] == "[redacted-email]"
        assert result[1] == "safe text"

    def test_redact_pii_dict(self):
        result = redact_pii({"email": "user@example.com", "name": "John"})
        assert result["email"] == "[redacted-email]"
        assert result["name"] == "John"

    def test_redact_pii_tuple(self):
        result = redact_pii(("user@example.com", "hello"))
        assert result[0] == "[redacted-email]"
        assert result[1] == "hello"

    def test_redact_pii_non_string_passthrough(self):
        assert redact_pii(42) == 42
        assert redact_pii(None) is None
        assert redact_pii(3.14) == 3.14


# ─────────────────────────────────────────────
# ai_safety - ContentQualityScore
# ─────────────────────────────────────────────


class TestContentQualityScore:
    def test_overall_is_mean_of_seven_dimensions(self):
        score = ContentQualityScore(
            correctness=1.0,
            caps_alignment=1.0,
            clarity=1.0,
            readability=1.0,
            pedagogical_completeness=1.0,
            inclusiveness=1.0,
            safety=1.0,
        )
        assert score.overall == 1.0

    def test_partial_overall(self):
        score = ContentQualityScore(
            correctness=0.0,
            caps_alignment=0.0,
            clarity=0.0,
            readability=0.0,
            pedagogical_completeness=0.0,
            inclusiveness=0.0,
            safety=0.0,
        )
        assert score.overall == 0.0

    def test_mixed_overall(self):
        score = ContentQualityScore(
            correctness=1.0,
            caps_alignment=1.0,
            clarity=1.0,
            readability=1.0,
            pedagogical_completeness=0.0,
            inclusiveness=0.0,
            safety=0.0,
        )
        assert abs(score.overall - round(4.0 / 7.0, 3)) < 0.001


# ─────────────────────────────────────────────
# ai_safety - score_lesson_quality
# ─────────────────────────────────────────────


class TestScoreLessonQuality:
    def _good_content(self):
        # 80-900 word content with SA context, example and practice
        return (
            "In South Africa, fractions are a key concept in Grade 5. "
            + "A fraction represents part of a whole. "
            + "For example, if you cut a braai into 4 equal parts and eat 1 part, "
            + "you have eaten 1/4 of the braai. "
            + "Practice: What fraction of 8 slices is 3 slices? "
        ) * 5  # repeat to get enough words

    def test_good_lesson_full_score(self):
        content = self._good_content()
        score = score_lesson_quality(
            content=content,
            caps_aligned=True,
            answer_present=True,
            has_worked_example=True,
            has_practice=True,
        )
        assert score.correctness == 1.0
        assert score.caps_alignment == 1.0
        assert score.safety == 1.0
        assert score.inclusiveness == 1.0

    def test_short_content_low_clarity(self):
        score = score_lesson_quality(
            content="Short.",
            caps_aligned=False,
            answer_present=False,
            has_worked_example=False,
            has_practice=False,
        )
        assert score.clarity == 0.35

    def test_no_answer_lowers_correctness(self):
        score = score_lesson_quality(
            content="Some content here" * 10,
            caps_aligned=True,
            answer_present=False,
            has_worked_example=True,
            has_practice=True,
        )
        assert score.correctness == 0.4

    def test_unsafe_content_zero_safety(self):
        score = score_lesson_quality(
            content="This content is about explicit gambling and drug use. " * 10,
            caps_aligned=True,
            answer_present=True,
            has_worked_example=True,
            has_practice=True,
        )
        assert score.safety == 0.0

    def test_no_sa_context_lower_inclusiveness(self):
        score = score_lesson_quality(
            content="Mathematics is a subject. " * 20,
            caps_aligned=True,
            answer_present=True,
            has_worked_example=True,
            has_practice=True,
        )
        assert score.inclusiveness == 0.7


# ─────────────────────────────────────────────
# billing_guard
# ─────────────────────────────────────────────


class TestBillingGuard:
    def _make_register(self, tmp_path: Path, live_payments: bool, billing_launch: bool) -> Path:
        docs_dir = tmp_path / "docs" / "roadmap" / "production_readiness"
        docs_dir.mkdir(parents=True)
        register = {
            "authority_boundaries": {
                "live_payment_processing_authorised": live_payments,
                "billing_launch_authorised": billing_launch,
            }
        }
        reg_path = docs_dir / "true_state_remediation_register.json"
        reg_path.write_text(json.dumps(register), encoding="utf-8")
        return tmp_path

    def test_authorized_when_both_true(self, tmp_path):
        root = self._make_register(tmp_path, True, True)
        assert check_live_billing_authorization(root) is True

    def test_locked_when_live_payments_false(self, tmp_path):
        root = self._make_register(tmp_path, False, True)
        assert check_live_billing_authorization(root) is False

    def test_locked_when_billing_launch_false(self, tmp_path):
        root = self._make_register(tmp_path, True, False)
        assert check_live_billing_authorization(root) is False

    def test_locked_when_register_missing(self, tmp_path):
        # No register file created
        assert check_live_billing_authorization(tmp_path) is False

    def test_locked_on_corrupt_json(self, tmp_path):
        docs_dir = tmp_path / "docs" / "roadmap" / "production_readiness"
        docs_dir.mkdir(parents=True)
        (docs_dir / "true_state_remediation_register.json").write_text("{invalid json", encoding="utf-8")
        assert check_live_billing_authorization(tmp_path) is False

    def test_assert_billing_authorized_raises_when_locked(self, tmp_path):
        with pytest.raises(BillingLockError) as exc_info:
            assert_billing_authorized(tmp_path)
        assert exc_info.value.status_code == 403
        assert "X-Billing-Lock" in exc_info.value.headers

    def test_assert_billing_authorized_passes_when_unlocked(self, tmp_path):
        root = self._make_register(tmp_path, True, True)
        # Should not raise
        assert_billing_authorized(root)

    def test_sanitize_billing_webhook_authorized(self, tmp_path):
        root = self._make_register(tmp_path, True, True)
        payload = {"id": "evt_12345", "type": "payment_intent.succeeded"}
        result = sanitize_billing_webhook(payload, root)
        assert result["status"] == "processed"
        assert result["event_id"] == "evt_12345"

    def test_sanitize_billing_webhook_locked_raises(self, tmp_path):
        payload = {"id": "evt_99999"}
        with pytest.raises(BillingLockError):
            sanitize_billing_webhook(payload, tmp_path)

    def test_billing_lock_error_is_http_exception(self):
        err = BillingLockError()
        assert isinstance(err, HTTPException)
        assert err.status_code == 403
        assert err.headers["X-Billing-Lock"] == "LOCKED_FAIL_CLOSED"
