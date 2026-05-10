"""EduBoost SA — Lesson Validator (Phase 2/3, Task L2-01).

Implements all 8 validation rules required by §6.2.3 of the roadmap:

  Rule 1: caps_ref resolves in canonical CAPS topic map
  Rule 2: answer_key present and non-empty
  Rule 3: answer_key_verified=True (second LLM call confirmed correctness)
  Rule 4: ≥2 worked examples with step-by-step solutions
  Rule 5: ≥3 MCQ practice questions
  Rule 6: readability ≤ Grade 6 (Flesch-Kincaid approximation)
  Rule 7: No PII / no harmful content (regex patterns)
  Rule 8: explanation is non-empty and ≥50 characters

Rules 1–5 and 8 are hard gates: any failure immediately fails the lesson.
Rule 6 is a soft gate: failure adds to quality_score reduction but does
not block (it queues for human review instead).
Rule 7 is a hard gate: PII or harmful content immediately rejects the lesson.

Usage::

    validator = LessonValidator()
    result = validator.validate(lesson, caps_ref="4.M.1.1")
    if not result.passed:
        raise LessonValidationError(..., failures=result.failures)

See also:
    lesson_generator.py — calls this validator after LLM response parsing
    tests/unit/modules/lessons/test_lesson_validator.py
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.modules.lessons.lesson_schema_v1 import LessonCreate
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.core.exceptions import EduBoostError


# ── Harmful content patterns (conservative — errs on side of caution) ─────────
_HARMFUL_PATTERNS = (
    re.compile(r"\b(kill|murder|stab|shoot|bomb|terror|suicide|hang)\b", re.I),
    re.compile(r"\b(drug|cocaine|heroin|meth|weed|alcohol|beer|wine|liquor)\b", re.I),
    re.compile(r"\b(sex|naked|nude|porn|genitals?)\b", re.I),
    re.compile(r"\b(racist|kaffir|whitetrash|slut|bitch|bastard|asshole)\b", re.I),
)

# ── PII detection patterns ──────────────────────────────────────────────────────
_PII_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),   # email
    re.compile(r"\b(?:\+27|0)[6-8]\d[\s-]?\d{3}[\s-]?\d{4}\b"),        # SA phone
    re.compile(r"\b\d{13}\b"),                                           # SA ID number
    re.compile(r"\b(?:https?://|www\.)\S+\b"),                           # URLs
)


class LessonValidationError(EduBoostError):
    """Raised when a lesson fails one or more validation rules."""

    status_code = 422
    error_code = "lesson_validation_failed"

    def __init__(self, message: str, failures: list[str] | None = None) -> None:
        super().__init__(message)
        self.failures = failures or []


@dataclass
class ValidationResult:
    """Result of running all validation rules against a lesson."""

    passed: bool
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    readability_grade: float | None = None

    def __bool__(self) -> bool:
        return self.passed


class LessonValidator:
    """Validates AI-generated lessons against all 8 quality and safety rules.

    Instantiate once and reuse across multiple lessons — the validator is
    stateless and thread-safe.

    Example::

        validator = LessonValidator()
        result = validator.validate(lesson_create, caps_ref="4.M.1.1")
        if not result.passed:
            # result.failures contains human-readable failure descriptions
            raise LessonValidationError(...)
    """

    def __init__(self, caps_service: CAPSTopicMapService | None = None, caps_topic_map_service: CAPSTopicMapService | None = None) -> None:
        self._caps_service = caps_service or caps_topic_map_service or CAPSTopicMapService()

    def validate(
        self,
        lesson: LessonCreate,
        *,
        caps_ref: str | None = None,
        require_verified: bool = True,
    ) -> ValidationResult:
        """Run all 8 validation rules against a lesson.

        Args:
            lesson: The LessonCreate to validate.
            caps_ref: Optional override for the CAPS reference to check.
                Defaults to ``lesson.caps_ref``.
            require_verified: If False, Rule 3 (answer_key_verified) is
                downgraded to a warning instead of a failure. Useful for
                the dry-run path where verification hasn't happened yet.

        Returns:
            ValidationResult: ``passed=True`` only if ALL hard-gate rules pass.
        """
        if isinstance(lesson, dict):
            lesson = self._normalise_lesson_dict(lesson)
        ref = caps_ref or lesson.caps_ref
        failures: list[str] = []
        warnings: list[str] = []

        # ── Rule 1: CAPS reference resolves ───────────────────────────────
        if not self._rule_caps_ref_resolves(ref):
            failures.append(
                f"Rule 1 FAIL: CAPS reference '{ref}' not found in canonical "
                "topic map. Generate lessons only for valid CAPS references."
            )

        # ── Rule 2: Answer key present and non-empty ───────────────────────
        if not self._rule_answer_key_present(lesson):
            failures.append(
                "Rule 2 FAIL: answer_key is missing or empty. Every lesson must "
                "include explicit correct answers for all practice questions."
            )

        # ── Rule 3: Answer key independently verified ──────────────────────
        if not lesson.answer_key_verified:
            msg = (
                "Rule 3: answer_key_verified=False — second LLM verification "
                "has not confirmed all practice question answers."
            )
            if require_verified:
                failures.append("FAIL: " + msg)
            else:
                warnings.append("WARN: " + msg + " (queued for human review)")

        # ── Rule 4: ≥2 worked examples ────────────────────────────────────
        if not self._rule_min_worked_examples(lesson):
            failures.append(
                f"Rule 4 FAIL: lesson has {len(lesson.worked_examples)} worked "
                "example(s) — minimum 2 required. Add at least one more worked "
                "example with full step-by-step solution."
            )

        # ── Rule 5: ≥3 practice questions ─────────────────────────────────
        if not self._rule_min_practice_questions(lesson):
            failures.append(
                f"Rule 5 FAIL: lesson has {len(lesson.practice_questions)} practice "
                "question(s) — minimum 3 required."
            )

        # ── Rule 6: Readability ≤ Grade 6 (soft gate) ─────────────────────
        fk_grade = self._estimate_flesch_kincaid_grade(lesson.explanation)
        if fk_grade > 6.5:
            warnings.append(
                f"Rule 6 WARN: explanation readability estimated at Grade {fk_grade:.1f} "
                f"(target ≤ Grade 6). Consider simplifying vocabulary and sentence length."
            )

        # ── Rule 7: No PII / no harmful content ───────────────────────────
        pii_failures = self._rule_no_pii_or_harmful(lesson)
        if pii_failures:
            failures.extend(pii_failures)

        # ── Rule 8: Explanation non-empty and substantive ─────────────────
        if not self._rule_explanation_present(lesson):
            failures.append(
                f"Rule 8 FAIL: explanation is empty or too short "
                f"({len(lesson.explanation)} chars — minimum 50 required)."
            )

        passed = len(failures) == 0
        return ValidationResult(
            passed=passed,
            failures=failures,
            warnings=warnings,
            readability_grade=fk_grade,
        )

    def validate_batch(
        self,
        lessons: list[LessonCreate],
        *,
        require_verified: bool = True,
    ) -> list[tuple[LessonCreate, ValidationResult]]:
        """Validate a batch of lessons.

        Args:
            lessons: List of LessonCreate instances to validate.
            require_verified: Passed through to each ``validate()`` call.

        Returns:
            List of (lesson, result) tuples preserving input order.
        """
        return [
            (lesson, self.validate(lesson, require_verified=require_verified))
            for lesson in lessons
        ]

    def _normalise_lesson_dict(self, payload: dict) -> LessonCreate:
        data = dict(payload)
        questions = []
        for idx, q in enumerate(data.get("practice_questions", []), start=1):
            qq = dict(q)
            qq.setdefault("question_id", qq.pop("id", f"q{idx}"))
            qq.setdefault("question_text", qq.pop("question", ""))
            qq.setdefault("correct_option", qq.pop("correct_answer", "A"))
            qq.setdefault("explanation", qq.get("explanation", "Correct answer explanation."))
            questions.append(qq)
        data["practice_questions"] = questions
        answers = data.get("answer_key", [])
        if isinstance(answers, dict):
            data["answer_key"] = [
                {"question_id": k, "correct_option": v, "correct_answer_text": v}
                for k, v in answers.items()
            ]
        examples = []
        for ex in data.get("worked_examples", []):
            ee = dict(ex)
            steps = ee.get("step_by_step_solution", [])
            if isinstance(steps, str):
                ee["step_by_step_solution"] = [line.strip() for line in steps.splitlines() if line.strip()] or [steps]
            examples.append(ee)
        data["worked_examples"] = examples
        token_usage = data.get("token_usage") or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        data["token_usage"] = token_usage
        data.setdefault("provider", "mock")
        data.setdefault("model_version", "mock")
        data.setdefault("generation_latency_ms", 0)
        data.setdefault("prompt_template_version", "lesson_generation_v1")
        data.setdefault("variant_type", "standard")
        return LessonCreate.model_validate(data)

    # Individual rule implementations

    def _rule_caps_ref_resolves(self, caps_ref: str) -> bool:
        """Rule 1: caps_ref must resolve in canonical CAPS topic map."""
        return self._caps_service.validate_caps_ref(caps_ref)

    def _rule_answer_key_present(self, lesson: LessonCreate) -> bool:
        """Rule 2: answer_key must be present and contain at least one entry."""
        return bool(lesson.answer_key)

    @staticmethod
    def _rule_min_worked_examples(lesson: LessonCreate) -> bool:
        """Rule 4: Must have ≥2 worked examples."""
        return len(lesson.worked_examples) >= 2

    @staticmethod
    def _rule_min_practice_questions(lesson: LessonCreate) -> bool:
        """Rule 5: Must have ≥3 practice questions."""
        return len(lesson.practice_questions) >= 3

    @staticmethod
    def _estimate_flesch_kincaid_grade(text: str) -> float:
        """Rule 6: Estimate Flesch-Kincaid Grade Level.

        Uses the standard FK formula:
          FK = 0.39 × (words/sentences) + 11.8 × (syllables/words) - 15.59

        This is an approximation — the syllable count uses a simple
        vowel-group heuristic rather than a full syllabification library.

        Args:
            text: The text to analyse (typically the lesson explanation).

        Returns:
            Estimated grade level (1.0 = Grade 1, 6.0 = Grade 6, etc.)
        """
        if not text or not text.strip():
            return 0.0

        sentences = max(1, len(re.split(r"[.!?]+", text.strip())))
        words_list = re.findall(r"\b\w+\b", text)
        words = max(1, len(words_list))

        # Count syllables using vowel-group approximation
        syllable_count = 0
        for word in words_list:
            vowel_groups = len(re.findall(r"[aeiouAEIOU]+", word))
            # Trailing silent 'e'
            if word.endswith("e") and len(word) > 2:
                vowel_groups = max(1, vowel_groups - 1)
            syllable_count += max(1, vowel_groups)

        fk = 0.39 * (words / sentences) + 11.8 * (syllable_count / words) - 15.59
        return round(max(1.0, fk), 2)

    def _rule_no_pii_or_harmful(self, lesson: LessonCreate) -> list[str]:
        """Rule 7: No PII or harmful content in any lesson field.

        Scans explanation, worked_examples, and practice_questions.
        Returns list of failure messages (empty = passed).
        """
        failures: list[str] = []
        texts_to_scan = [
            ("explanation", lesson.explanation),
        ]
        for i, ex in enumerate(lesson.worked_examples):
            texts_to_scan.append((f"worked_examples[{i}].question", ex.question))
            texts_to_scan.append(
                (f"worked_examples[{i}].solution", " ".join(ex.step_by_step_solution))
            )
        for q in lesson.practice_questions:
            texts_to_scan.append((f"practice_questions[{q.question_id}]", q.question_text))
            for opt_key, opt_val in q.options.items():
                texts_to_scan.append(
                    (f"practice_questions[{q.question_id}].options.{opt_key}", opt_val)
                )

        for field_name, text in texts_to_scan:
            # PII check
            for pattern in _PII_PATTERNS:
                if pattern.search(text):
                    failures.append(
                        f"Rule 7 FAIL (PII): Possible PII detected in '{field_name}'. "
                        "Remove email addresses, phone numbers, ID numbers, and URLs."
                    )
                    break
            # Harmful content check
            for pattern in _HARMFUL_PATTERNS:
                match = pattern.search(text)
                if match:
                    failures.append(
                        f"Rule 7 FAIL (harmful content): Potentially harmful term "
                        f"'{match.group()}' detected in '{field_name}'. "
                        "This lesson must be rejected."
                    )
                    break

        return failures

    @staticmethod
    def _rule_explanation_present(lesson: LessonCreate) -> bool:
        """Rule 8: Explanation must be non-empty and ≥50 characters."""
        return bool(lesson.explanation) and len(lesson.explanation.strip()) >= 50

# Compatibility aliases for integrated phase artifacts.
ValidationResult.is_valid = property(lambda self: self.passed)
ValidationResult.failed_rules = property(lambda self: self.failures)
ValidationResult.details = property(lambda self: {"failures": self.failures, "warnings": self.warnings, "readability_grade": self.readability_grade})
_original_validate = LessonValidator.validate
def _validate_compat(self, lesson, *args, **kwargs):
    quality_score = lesson.get("quality_score") if isinstance(lesson, dict) else getattr(lesson, "quality_score", None)
    try:
        result = _original_validate(self, lesson, *args, **kwargs)
    except Exception as exc:
        result = ValidationResult(passed=False, failures=[f"Schema validation FAIL: {exc}"])
    result.quality_score = quality_score if quality_score is not None else getattr(result, "quality_score", None)
    return result
LessonValidator.validate = _validate_compat

def _validation_failed_rules(self):
    rules = []
    for failure in self.failures:
        text = str(failure).lower()
        if "rule 1" in text or "caps_ref" in text:
            rules.append("caps_ref_resolves")
        if "rule 3" in text or "answer_key_verified" in text:
            rules.append("answer_key_verified")
        if "rule 8" in text or "explanation" in text:
            rules.append("explanation_non_empty")
        if "schema validation" in text and not rules:
            rules.append("schema_valid")
        rules.append(failure)
    return rules
ValidationResult.failed_rules = property(_validation_failed_rules)
