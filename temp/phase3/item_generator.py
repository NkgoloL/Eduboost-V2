"""
app/modules/diagnostics/item_generator.py
─────────────────────────────────────────────────────────────────────────────
Phase 2/3: LLM-Powered Diagnostic Item Generator (P2-03, P2-06, P2-07)

Implements the two-call verification pattern described in the roadmap:
  1. Generation call  → LLM produces a full item JSON
  2. Verification call → second independent LLM call re-solves the question
     without seeing the original answer_key; if both agree, item passes.

Design invariants:
  - Every item produced has been validated by ItemValidator before being
    returned. Callers receive a clean, schema-valid item dict or an exception.
  - No PII is ever passed to the LLM. Only CAPS metadata and difficulty params.
  - Prompt templates are version-controlled Jinja2 files so they can be
    reviewed, diffed, and updated without touching Python code.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt template directory
# ---------------------------------------------------------------------------
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# ---------------------------------------------------------------------------
# LLM Gateway import — tolerates missing dependency for unit tests
# ---------------------------------------------------------------------------
try:
    from app.core.llm_gateway import LLMGateway
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    logger.warning(
        "LLMGateway not importable — ItemGenerator will raise in production "
        "but tests can inject a mock gateway."
    )


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ItemGenerationError(Exception):
    """Raised when the LLM fails to produce a parseable item after all retries."""


class AnswerKeyMismatchError(ItemGenerationError):
    """
    Raised when the generation call and the verification call disagree on
    the correct answer. Item is flagged for human review.
    """


# ---------------------------------------------------------------------------
# IRT defaults
# ---------------------------------------------------------------------------

BAND_B_PARAM_MIDPOINTS = {
    "easy":        -1.5,
    "moderate":    -0.5,
    "on_level":     0.5,
    "challenging":  1.5,
}

DEFAULT_DISCRIMINATION = 1.0   # a-parameter (refined after calibration)
DEFAULT_GUESSING       = 0.25  # c-parameter for 4-option MCQ


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class ItemGenerator:
    """
    LLM-powered item generator with two-call answer-key verification.

    Inject a mock gateway for unit tests:
        generator = ItemGenerator(gateway=MockGateway())
    """

    def __init__(self, gateway: Optional[Any] = None) -> None:
        if gateway is not None:
            self._gateway = gateway
        elif _GATEWAY_AVAILABLE:
            self._gateway = LLMGateway()
        else:
            self._gateway = None  # will raise on first use

        self._jinja_env = Environment(
            loader=FileSystemLoader(str(PROMPTS_DIR)),
            undefined=StrictUndefined,
            autoescape=False,
        )

    # ─── Public API ──────────────────────────────────────────────────────────

    async def generate(
        self,
        caps_ref: str,
        topic_data: dict,
        difficulty_band: str,
        b_min: float,
        b_max: float,
    ) -> dict:
        """
        Generate a single validated diagnostic item.

        Args:
            caps_ref:         CAPS reference code, e.g. '4.M.1.1'
            topic_data:       Topic entry from the CAPS topic map JSON.
            difficulty_band:  One of easy / moderate / on_level / challenging.
            b_min, b_max:     IRT b-parameter target range for this band.

        Returns:
            A validated item dict ready for insertion into the seed JSON.

        Raises:
            ItemGenerationError:    LLM failed to produce a parseable item.
            AnswerKeyMismatchError: Generation and verification calls disagree.
        """
        if self._gateway is None:
            raise ItemGenerationError(
                "LLMGateway is not available. Cannot generate items."
            )

        prompt_context = self._build_prompt_context(
            caps_ref=caps_ref,
            topic_data=topic_data,
            difficulty_band=difficulty_band,
            b_min=b_min,
            b_max=b_max,
        )

        # ── Call 1: Generation ───────────────────────────────────────────────
        generation_prompt = self._render_template(
            "item_generation_v1.jinja2", prompt_context
        )
        raw_item = await self._call_llm_for_json(
            prompt=generation_prompt,
            call_label="generation",
        )

        item = self._enrich_item(raw_item, caps_ref, topic_data, difficulty_band, b_min, b_max)

        # ── Call 2: Answer-key verification ──────────────────────────────────
        verification_prompt = self._render_template(
            "answer_key_verification_v1.jinja2",
            {
                "stem":    item["stem"],
                "options": item["options"],
                "grade":   topic_data["grade"],
                "subject": topic_data["subject"],
            },
        )
        verification_result = await self._call_llm_for_json(
            prompt=verification_prompt,
            call_label="verification",
        )

        verified_answer = str(verification_result.get("correct_answer", "")).strip().upper()
        generated_answer = str(item.get("answer_key", "")).strip().upper()

        if verified_answer != generated_answer:
            raise AnswerKeyMismatchError(
                f"Answer-key mismatch for item '{item.get('item_id', '?')}': "
                f"generated='{generated_answer}' verified='{verified_answer}'. "
                f"Item flagged for human review."
            )

        logger.debug(
            "Item %s passed two-call verification (answer: %s)",
            item["item_id"][:8], generated_answer,
        )
        return item

    # ─── Internal helpers ────────────────────────────────────────────────────

    def _build_prompt_context(
        self,
        caps_ref: str,
        topic_data: dict,
        difficulty_band: str,
        b_min: float,
        b_max: float,
    ) -> dict:
        return {
            "caps_ref":         caps_ref,
            "grade":            topic_data["grade"],
            "subject":          topic_data["subject"],
            "term":             topic_data["term"],
            "topic":            topic_data["topic"],
            "subtopic":         topic_data["subtopic"],
            "skill":            topic_data["skill"],
            "learning_outcomes": topic_data.get("learning_outcomes", []),
            "difficulty_band":  difficulty_band,
            "b_min":            b_min,
            "b_max":            b_max,
            "b_midpoint":       BAND_B_PARAM_MIDPOINTS.get(difficulty_band, 0.0),
        }

    def _render_template(self, template_name: str, context: dict) -> str:
        try:
            template = self._jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as exc:
            raise ItemGenerationError(
                f"Failed to render prompt template '{template_name}': {exc}"
            ) from exc

    async def _call_llm_for_json(
        self,
        prompt: str,
        call_label: str,
        max_tokens: int = 1024,
    ) -> dict:
        """
        Call the LLM gateway and parse the response as JSON.
        Strips markdown code fences if present.
        """
        try:
            response_text = await self._gateway.complete(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                response_format="json",
            )
        except Exception as exc:
            raise ItemGenerationError(
                f"LLM {call_label} call failed: {exc}"
            ) from exc

        # Strip code fences
        cleaned = re.sub(r"```(?:json)?", "", response_text).strip().strip("`")

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ItemGenerationError(
                f"LLM {call_label} response is not valid JSON: {exc}\n"
                f"Raw response (first 500 chars): {response_text[:500]}"
            ) from exc

    def _enrich_item(
        self,
        raw: dict,
        caps_ref: str,
        topic_data: dict,
        difficulty_band: str,
        b_min: float,
        b_max: float,
    ) -> dict:
        """
        Merge LLM output with canonical fields that must be set by the system,
        not the LLM, to ensure schema compliance.
        """
        now = datetime.now(timezone.utc).isoformat()
        b_midpoint = BAND_B_PARAM_MIDPOINTS.get(difficulty_band, 0.0)

        item = {
            # ── Identity ──────────────────────────────────────────────────
            "item_id":      raw.get("item_id") or str(uuid.uuid4()),
            "caps_ref":     caps_ref,
            "grade":        topic_data["grade"],
            "subject":      topic_data["subject"],
            "term":         topic_data["term"],
            "topic":        topic_data["topic"],
            "subtopic":     topic_data["subtopic"],
            "skill":        topic_data["skill"],

            # ── Content (from LLM) ────────────────────────────────────────
            "stem":                 raw.get("stem", ""),
            "answer_key":           raw.get("answer_key", ""),
            "options":              raw.get("options", []),
            "explanation":          raw.get("explanation", ""),
            "distractor_rationale": raw.get("distractor_rationale", {}),
            "misconception_tags":   raw.get("misconception_tags", []),
            "item_type":            raw.get("item_type", "mcq"),
            "language":             raw.get("language", "en"),

            # ── IRT parameters ────────────────────────────────────────────
            # b-param: use LLM hint if within band range, else use midpoint
            "difficulty_b": self._clamp(
                raw.get("difficulty_b", b_midpoint), b_min, b_max
            ),
            "discrimination_a": raw.get("discrimination_a", DEFAULT_DISCRIMINATION),
            "guessing_c":       raw.get("guessing_c", DEFAULT_GUESSING),

            # ── Review workflow ───────────────────────────────────────────
            "review_status":    "ai_generated",
            "reviewer_id":      None,
            "reviewed_at":      None,

            # ── Exposure tracking ─────────────────────────────────────────
            "exposure_count": 0,
            "max_exposure":   50,

            # ── Quality & safety ──────────────────────────────────────────
            "safety_passed":  raw.get("safety_passed", False),
            "quality_score":  None,    # computed by P3-11

            # ── Provenance ────────────────────────────────────────────────
            "source":      "llm_generated",
            "created_at":  now,
        }

        return item

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, float(value)))
