"""
tests/unit/modules/diagnostics/test_item_generator.py
─────────────────────────────────────────────────────────────────────────────
Phase 2/3: Unit Tests for ItemGenerator (P2-03, P2-07)

Tests the two-call generation + verification pattern:
  - Successful generation produces a valid, enriched item
  - Answer-key mismatch raises AnswerKeyMismatchError
  - LLM failure raises ItemGenerationError
  - b-parameter is clamped within band bounds
  - System fields (review_status, source, exposure_count) are set correctly
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock
from pathlib import Path

import pytest

from app.modules.diagnostics.item_generator import (
    ItemGenerator,
    ItemGenerationError,
    AnswerKeyMismatchError,
    DEFAULT_DISCRIMINATION,
    DEFAULT_GUESSING,
)

# ---------------------------------------------------------------------------
# Mock topic data and CAPS ref
# ---------------------------------------------------------------------------

CAPS_REF = "4.M.1.1"

TOPIC_DATA = {
    "grade": 4,
    "subject": "Mathematics",
    "term": 1,
    "topic": "Whole Numbers",
    "subtopic": "Count, Order and Compare 4-digit Numbers",
    "skill": "place_value_ordering",
    "learning_outcomes": [
        "Count forwards and backwards in whole number intervals up to at least 10 000",
    ],
}

DIFFICULTY_BAND = "moderate"
B_MIN, B_MAX = -1.0, 0.0


# ---------------------------------------------------------------------------
# Mock LLM gateway
# ---------------------------------------------------------------------------

def _mock_generation_response(answer_key: str = "B") -> str:
    """Return a well-formed item JSON string from the 'LLM'."""
    item = {
        "item_id":        str(uuid.uuid4()),
        "stem":           "Sipho has 1 200 apples and gets 300 more. How many does he have?",
        "answer_key":     answer_key,
        "options": [
            {"label": "A", "text": "1 500"},
            {"label": "B", "text": "1 500"},
            {"label": "C", "text": "1 230"},
            {"label": "D", "text": "900"},
        ],
        "explanation":    "You add the hundreds. 1 200 plus 300 equals 1 500. The answer is B because the digits add up correctly.",
        "distractor_rationale": {
            "A": "A learner might confuse the place values.",
            "C": "A learner might add only the units digit.",
            "D": "A learner might subtract instead of add.",
        },
        "misconception_tags": ["place_value_confusion"],
        "item_type":       "mcq",
        "language":        "en",
        "difficulty_b":    -0.5,
        "discrimination_a": 1.0,
        "guessing_c":      0.25,
        "safety_passed":   True,
    }
    return json.dumps(item)


def _mock_verification_response(correct_answer: str = "B") -> str:
    return json.dumps({
        "correct_answer": correct_answer,
        "working":        "1 200 + 300 = 1 500. The answer is B.",
        "confidence":     "high",
    })


def _make_gateway(
    gen_answer: str = "B",
    verify_answer: str = "B",
    gen_raises: Exception | None = None,
    verify_raises: Exception | None = None,
) -> MagicMock:
    """
    Build a mock LLM gateway.
    complete() is called twice per item: once for generation, once for verification.
    """
    gateway = MagicMock()
    call_count = {"n": 0}

    async def _complete(**kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            # Generation call
            if gen_raises:
                raise gen_raises
            return _mock_generation_response(gen_answer)
        else:
            # Verification call
            if verify_raises:
                raise verify_raises
            return _mock_verification_response(verify_answer)

    gateway.complete = _complete
    return gateway


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestItemGeneratorHappyPath:

    @pytest.mark.asyncio
    async def test_generate_returns_valid_item(self, tmp_path, monkeypatch):
        """generate() with matching answers returns a complete, enriched item."""
        _patch_prompts(monkeypatch, tmp_path)
        gateway   = _make_gateway(gen_answer="B", verify_answer="B")
        generator = ItemGenerator(gateway=gateway)

        item = await generator.generate(
            caps_ref=CAPS_REF,
            topic_data=TOPIC_DATA,
            difficulty_band=DIFFICULTY_BAND,
            b_min=B_MIN,
            b_max=B_MAX,
        )

        assert item is not None
        assert item["caps_ref"]       == CAPS_REF
        assert item["grade"]          == 4
        assert item["review_status"]  == "ai_generated"
        assert item["source"]         == "llm_generated"
        assert item["exposure_count"] == 0
        assert item["item_id"] is not None

    @pytest.mark.asyncio
    async def test_generate_sets_system_fields(self, tmp_path, monkeypatch):
        """System-managed fields must be set by the generator, not the LLM."""
        _patch_prompts(monkeypatch, tmp_path)
        gateway   = _make_gateway()
        generator = ItemGenerator(gateway=gateway)

        item = await generator.generate(
            caps_ref=CAPS_REF,
            topic_data=TOPIC_DATA,
            difficulty_band=DIFFICULTY_BAND,
            b_min=B_MIN,
            b_max=B_MAX,
        )

        assert item["review_status"]   == "ai_generated"
        assert item["reviewer_id"]     is None
        assert item["reviewed_at"]     is None
        assert item["exposure_count"]  == 0
        assert item["max_exposure"]    == 50
        assert item["source"]          == "llm_generated"
        assert item["created_at"]      is not None

    @pytest.mark.asyncio
    async def test_generate_uses_default_irt_params(self, tmp_path, monkeypatch):
        """Default a and c params must be applied when LLM omits them."""
        _patch_prompts(monkeypatch, tmp_path)

        # Return item without a/c params
        async def _complete_no_ac(**kwargs):
            raw = json.loads(_mock_generation_response())
            raw.pop("discrimination_a", None)
            raw.pop("guessing_c", None)
            if not hasattr(_complete_no_ac, "called"):
                _complete_no_ac.called = True
                return json.dumps(raw)
            return _mock_verification_response()

        gateway = MagicMock()
        call_n  = {"n": 0}

        async def _complete(**kwargs):
            call_n["n"] += 1
            if call_n["n"] == 1:
                raw = json.loads(_mock_generation_response())
                raw.pop("discrimination_a", None)
                raw.pop("guessing_c", None)
                return json.dumps(raw)
            return _mock_verification_response()

        gateway.complete = _complete
        generator = ItemGenerator(gateway=gateway)

        item = await generator.generate(
            caps_ref=CAPS_REF,
            topic_data=TOPIC_DATA,
            difficulty_band=DIFFICULTY_BAND,
            b_min=B_MIN,
            b_max=B_MAX,
        )
        assert item["discrimination_a"] == DEFAULT_DISCRIMINATION
        assert item["guessing_c"]       == DEFAULT_GUESSING

    @pytest.mark.asyncio
    async def test_b_param_clamped_within_band(self, tmp_path, monkeypatch):
        """
        If the LLM returns a b-param outside [b_min, b_max],
        it must be clamped to the band range.
        """
        _patch_prompts(monkeypatch, tmp_path)
        call_n = {"n": 0}

        async def _complete(**kwargs):
            call_n["n"] += 1
            if call_n["n"] == 1:
                raw = json.loads(_mock_generation_response())
                raw["difficulty_b"] = 99.9  # way out of band
                return json.dumps(raw)
            return _mock_verification_response()

        gateway = MagicMock()
        gateway.complete = _complete
        generator = ItemGenerator(gateway=gateway)

        item = await generator.generate(
            caps_ref=CAPS_REF,
            topic_data=TOPIC_DATA,
            difficulty_band=DIFFICULTY_BAND,
            b_min=B_MIN,
            b_max=B_MAX,
        )
        assert B_MIN <= item["difficulty_b"] <= B_MAX, (
            f"difficulty_b={item['difficulty_b']} should be clamped to [{B_MIN}, {B_MAX}]"
        )

    @pytest.mark.asyncio
    async def test_topic_metadata_injected_from_topic_data(self, tmp_path, monkeypatch):
        """topic, subtopic, subject, term, grade must come from topic_data, not the LLM."""
        _patch_prompts(monkeypatch, tmp_path)
        gateway   = _make_gateway()
        generator = ItemGenerator(gateway=gateway)

        item = await generator.generate(
            caps_ref=CAPS_REF,
            topic_data=TOPIC_DATA,
            difficulty_band=DIFFICULTY_BAND,
            b_min=B_MIN,
            b_max=B_MAX,
        )
        assert item["topic"]    == TOPIC_DATA["topic"]
        assert item["subtopic"] == TOPIC_DATA["subtopic"]
        assert item["subject"]  == TOPIC_DATA["subject"]
        assert item["grade"]    == TOPIC_DATA["grade"]
        assert item["term"]     == TOPIC_DATA["term"]


# ---------------------------------------------------------------------------
# Answer-key verification (two-call pattern)
# ---------------------------------------------------------------------------

class TestAnswerKeyVerification:

    @pytest.mark.asyncio
    async def test_matching_answers_pass(self, tmp_path, monkeypatch):
        """When generation and verification agree, item is returned cleanly."""
        _patch_prompts(monkeypatch, tmp_path)
        gateway   = _make_gateway(gen_answer="B", verify_answer="B")
        generator = ItemGenerator(gateway=gateway)

        item = await generator.generate(
            caps_ref=CAPS_REF, topic_data=TOPIC_DATA,
            difficulty_band=DIFFICULTY_BAND, b_min=B_MIN, b_max=B_MAX,
        )
        assert item["answer_key"].upper() == "B"

    @pytest.mark.asyncio
    async def test_mismatched_answers_raise_mismatch_error(self, tmp_path, monkeypatch):
        """
        When generation says 'B' but verification says 'A', AnswerKeyMismatchError
        must be raised — item must NOT be returned.
        """
        _patch_prompts(monkeypatch, tmp_path)
        gateway   = _make_gateway(gen_answer="B", verify_answer="A")
        generator = ItemGenerator(gateway=gateway)

        with pytest.raises(AnswerKeyMismatchError) as exc_info:
            await generator.generate(
                caps_ref=CAPS_REF, topic_data=TOPIC_DATA,
                difficulty_band=DIFFICULTY_BAND, b_min=B_MIN, b_max=B_MAX,
            )
        assert "mismatch" in str(exc_info.value).lower()
        assert "B" in str(exc_info.value) or "A" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_answer_key_case_insensitive_match(self, tmp_path, monkeypatch):
        """Verification answer 'b' (lowercase) must match generated 'B'."""
        _patch_prompts(monkeypatch, tmp_path)
        call_n = {"n": 0}

        async def _complete(**kwargs):
            call_n["n"] += 1
            if call_n["n"] == 1:
                return _mock_generation_response("B")
            return json.dumps({"correct_answer": "b", "working": "ok", "confidence": "high"})

        gateway = MagicMock()
        gateway.complete = _complete
        generator = ItemGenerator(gateway=gateway)

        # Should NOT raise — case-insensitive comparison
        item = await generator.generate(
            caps_ref=CAPS_REF, topic_data=TOPIC_DATA,
            difficulty_band=DIFFICULTY_BAND, b_min=B_MIN, b_max=B_MAX,
        )
        assert item is not None


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestItemGeneratorErrors:

    @pytest.mark.asyncio
    async def test_generation_llm_error_raises_generation_error(self, tmp_path, monkeypatch):
        """If the LLM gateway raises on the generation call, ItemGenerationError is raised."""
        _patch_prompts(monkeypatch, tmp_path)
        gateway   = _make_gateway(gen_raises=RuntimeError("Gateway timeout"))
        generator = ItemGenerator(gateway=gateway)

        with pytest.raises(ItemGenerationError, match="generation call failed"):
            await generator.generate(
                caps_ref=CAPS_REF, topic_data=TOPIC_DATA,
                difficulty_band=DIFFICULTY_BAND, b_min=B_MIN, b_max=B_MAX,
            )

    @pytest.mark.asyncio
    async def test_verification_llm_error_raises_generation_error(self, tmp_path, monkeypatch):
        """If the LLM gateway raises on the verification call, ItemGenerationError is raised."""
        _patch_prompts(monkeypatch, tmp_path)
        gateway   = _make_gateway(verify_raises=RuntimeError("Rate limit"))
        generator = ItemGenerator(gateway=gateway)

        with pytest.raises(ItemGenerationError, match="verification call failed"):
            await generator.generate(
                caps_ref=CAPS_REF, topic_data=TOPIC_DATA,
                difficulty_band=DIFFICULTY_BAND, b_min=B_MIN, b_max=B_MAX,
            )

    @pytest.mark.asyncio
    async def test_invalid_json_response_raises_generation_error(self, tmp_path, monkeypatch):
        """If the LLM returns non-JSON, ItemGenerationError is raised."""
        _patch_prompts(monkeypatch, tmp_path)

        async def _bad_complete(**kwargs):
            return "Sorry, I cannot generate a maths question right now."

        gateway = MagicMock()
        gateway.complete = _bad_complete
        generator = ItemGenerator(gateway=gateway)

        with pytest.raises(ItemGenerationError, match="not valid JSON"):
            await generator.generate(
                caps_ref=CAPS_REF, topic_data=TOPIC_DATA,
                difficulty_band=DIFFICULTY_BAND, b_min=B_MIN, b_max=B_MAX,
            )

    @pytest.mark.asyncio
    async def test_no_gateway_raises_generation_error(self, tmp_path, monkeypatch):
        """
        If no gateway is available (e.g. env not configured),
        ItemGenerationError is raised, not AttributeError.
        """
        _patch_prompts(monkeypatch, tmp_path)
        generator = ItemGenerator(gateway=None)
        # Manually clear _gateway so the 'is None' check triggers
        generator._gateway = None

        with pytest.raises(ItemGenerationError, match="not available"):
            await generator.generate(
                caps_ref=CAPS_REF, topic_data=TOPIC_DATA,
                difficulty_band=DIFFICULTY_BAND, b_min=B_MIN, b_max=B_MAX,
            )

    @pytest.mark.asyncio
    async def test_markdown_fenced_json_is_parsed(self, tmp_path, monkeypatch):
        """LLM responses wrapped in ```json...``` fences must still be parsed."""
        _patch_prompts(monkeypatch, tmp_path)
        call_n = {"n": 0}

        async def _fenced_complete(**kwargs):
            call_n["n"] += 1
            if call_n["n"] == 1:
                return f"```json\n{_mock_generation_response()}\n```"
            return f"```json\n{_mock_verification_response()}\n```"

        gateway = MagicMock()
        gateway.complete = _fenced_complete
        generator = ItemGenerator(gateway=gateway)

        item = await generator.generate(
            caps_ref=CAPS_REF, topic_data=TOPIC_DATA,
            difficulty_band=DIFFICULTY_BAND, b_min=B_MIN, b_max=B_MAX,
        )
        assert item is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patch_prompts(monkeypatch, tmp_path: Path) -> None:
    """
    Write minimal Jinja2 prompt templates into a temp directory and
    patch ItemGenerator to load from there instead of the real prompts dir.
    """
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    # Minimal generation template — just outputs a fixed prompt string
    (prompts_dir / "item_generation_v1.jinja2").write_text(
        "Generate a maths item for {{ caps_ref }} at {{ difficulty_band }} difficulty."
    )
    (prompts_dir / "answer_key_verification_v1.jinja2").write_text(
        "Verify the answer for: {{ stem }}"
    )

    monkeypatch.setattr(
        "app.modules.diagnostics.item_generator.PROMPTS_DIR",
        prompts_dir,
    )
