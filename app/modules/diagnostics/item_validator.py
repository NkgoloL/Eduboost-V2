"""
app/modules/diagnostics/item_validator.py
─────────────────────────────────────────────────────────────────────────────
Phase 2: Diagnostic Item Validator (P2-02)

Implements all 8 validation rules from the roadmap:
  1. CAPS reference exists in topic map
  2. answer_key matches one of options[].label
  3. stem readability ≤ Grade 6 Flesch-Kincaid
  4. No PII, no harmful content (regex + pattern checks)
  5. IRT params within valid bounds
  6. At least 4 MCQ options
  7. explanation non-empty
  8. distractor_rationale covers all wrong options

Also validates:
  - misconception_tags non-empty
  - item_type is a known enum value
  - safety_passed is True
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Validation exception
# ---------------------------------------------------------------------------

class ValidationError(ValueError):
    """Raised when an item fails one or more validation rules."""

    def __init__(self, rule: str, detail: str) -> None:
        self.rule   = rule
        self.detail = detail
        super().__init__(f"[{rule}] {detail}")


# ---------------------------------------------------------------------------
# PII / harmful content patterns
# ---------------------------------------------------------------------------

# Patterns that should never appear in item stems or explanations
_PII_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("email",       re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", re.I)),
    ("sa_id",       re.compile(r"\b\d{13}\b")),                          # SA ID number
    ("phone_za",    re.compile(r"\b0[6-8]\d\s?\d{3}\s?\d{4}\b")),        # ZA mobile
    ("url",         re.compile(r"https?://", re.I)),
]

_HARMFUL_KEYWORDS = frozenset({
    "violence", "weapon", "kill", "murder", "rape", "abuse",
    "drug", "alcohol", "suicide", "bomb", "terror", "racist",
    "nigger", "kaffir", "slut", "fuck", "shit", "bastard",
})

# Brand names that must not appear (non-exhaustive)
_BRAND_PATTERNS = re.compile(
    r"\b(coca.?cola|pepsi|mcdonalds|kfc|nando|pick n pay|woolworths|checkers"
    r"|vodacom|mtn|cell c|telkom|absa|fnb|standard bank|nedbank)\b",
    re.I,
)

# ---------------------------------------------------------------------------
# Readability — simplified Flesch-Kincaid Grade Level
# ---------------------------------------------------------------------------

def _count_syllables(word: str) -> int:
    """Rough syllable count — good enough for readability checks."""
    word = word.lower().strip(".,;:!?\"'()-")
    if not word:
        return 0
    # Count vowel groups
    count = len(re.findall(r"[aeiou]+", word))
    # Subtract silent trailing e
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def flesch_kincaid_grade(text: str) -> float:
    """
    Returns the Flesch-Kincaid Grade Level for the given text.
    Grade 6 = accessible to a Grade 4/5 learner with some support.
    """
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0.0

    words = text.split()
    if not words:
        return 0.0

    total_words     = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(_count_syllables(w) for w in words)

    # FK Grade Level formula
    grade = (
        0.39 * (total_words / total_sentences)
        + 11.8 * (total_syllables / total_words)
        - 15.59
    )
    return round(grade, 2)


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

VALID_ITEM_TYPES = frozenset({"mcq", "short_answer", "true_false", "fill_blank"})
VALID_IRT_BOUNDS = {
    "difficulty_b":     (-3.0,  3.0),
    "discrimination_a": ( 0.5,  2.5),
    "guessing_c":       ( 0.0,  0.35),
}
MAX_FK_GRADE = 6.5       # stem must not exceed this readability level
MIN_OPTIONS  = 4         # MCQ must have at least this many options


class ItemValidator:
    """
    Validates a diagnostic item dict against all 8 roadmap rules.

    Usage:
        validator = ItemValidator(topic_map=topic_map)
        validator.validate(item)   # raises ValidationError on failure
    """

    def __init__(self, topic_map: Optional[dict] = None) -> None:
        self._topic_map = topic_map or {}
        # Flatten CAPS refs for O(1) lookup
        self._valid_caps_refs = set()
        if "topics" in self._topic_map:
            # Handle both list and dict formats for robustness
            topics = self._topic_map["topics"]
            if isinstance(topics, list):
                self._index_topic_list(topics)
            elif isinstance(topics, dict):
                self._valid_caps_refs.update(topics.keys())
        elif "terms" in self._topic_map:
            for term in self._topic_map.get("terms", []):
                self._index_topic_list(term.get("topics", []))

    def _index_topic_list(self, topics: list[dict]) -> None:
        for t in topics:
            if "caps_ref" in t:
                self._valid_caps_refs.add(t["caps_ref"])
            for st in t.get("subtopics", []):
                if "caps_ref" in st:
                    self._valid_caps_refs.add(st["caps_ref"])

    # ─── Main entry point ────────────────────────────────────────────────────

    def validate(self, item: dict) -> None:
        """
        Run all validation rules. Raises ValidationError on the first failure.
        Call validate_all() to collect all failures instead.
        """
        for rule_fn in self._rules():
            rule_fn(item)

    def validate_all(self, item: dict) -> list[ValidationError]:
        """
        Run all validation rules and collect failures without raising.
        Returns a (possibly empty) list of ValidationError instances.
        """
        errors: list[ValidationError] = []
        for rule_fn in self._rules():
            try:
                rule_fn(item)
            except ValidationError as exc:
                errors.append(exc)
        return errors

    # ─── Rule registry ───────────────────────────────────────────────────────

    def _rules(self):
        return [
            self._rule_caps_ref_exists,
            self._rule_answer_key_matches_option,
            self._rule_stem_readability,
            self._rule_no_pii_or_harmful,
            self._rule_irt_params_in_bounds,
            self._rule_min_options,
            self._rule_explanation_non_empty,
            self._rule_distractor_rationale_complete,
            self._rule_misconception_tags_present,
            self._rule_item_type_valid,
            self._rule_safety_passed,
        ]

    # ─── Individual rules ────────────────────────────────────────────────────

    def _rule_caps_ref_exists(self, item: dict) -> None:
        """Rule 1: CAPS reference must exist in the topic map."""
        caps_ref = item.get("caps_ref", "")
        if not caps_ref:
            raise ValidationError("caps_ref", "caps_ref field is missing or empty.")
        if self._topic_map and caps_ref not in self._valid_caps_refs:
            raise ValidationError(
                "caps_ref",
                f"CAPS ref '{caps_ref}' is not in the topic map. "
                f"Known refs: {sorted(list(self._valid_caps_refs))}",
            )

    def _rule_answer_key_matches_option(self, item: dict) -> None:
        """Rule 2: answer_key must match one of options[].label."""
        answer_key = str(item.get("answer_key", "")).strip().upper()
        if not answer_key:
            raise ValidationError("answer_key", "answer_key is missing or empty.")

        options = item.get("options", [])
        option_labels = {str(o.get("label", "")).upper() for o in options}

        if answer_key not in option_labels:
            raise ValidationError(
                "answer_key",
                f"answer_key '{answer_key}' does not match any option label. "
                f"Option labels found: {sorted(option_labels)}",
            )

    def _rule_stem_readability(self, item: dict) -> None:
        """Rule 3: stem readability must be ≤ Grade 6 Flesch-Kincaid for Grade R–6 items.

        The generator rewrites stems for younger grades (R–6). Enforce the
        FK threshold only for those grades; allow higher-grade items to bypass
        this specific restriction.
        """
        stem = item.get("stem", "")
        if not stem or not stem.strip():
            raise ValidationError("stem_readability", "stem is missing or empty.")

        # Determine item grade. Accept numeric grades and 'R' (reception).
        grade_field = item.get("grade")
        grade_num: Optional[int]
        grade_num = None
        if isinstance(grade_field, str):
            g = grade_field.strip()
            if g.upper() == "R":
                grade_num = 0
            else:
                try:
                    grade_num = int(float(g))
                except Exception:
                    grade_num = None
        elif isinstance(grade_field, (int, float)):
            try:
                grade_num = int(grade_field)
            except Exception:
                grade_num = None

        # Only enforce the FK threshold for Grade R–6 items (inclusive).
        enforce_fk = grade_num is None or grade_num <= 6
        if not enforce_fk:
            return

        fk = flesch_kincaid_grade(stem)
        if fk > MAX_FK_GRADE:
            raise ValidationError(
                "stem_readability",
                f"Stem FK grade {fk:.1f} exceeds maximum {MAX_FK_GRADE}. "
                f"Simplify language for Grade R–6 learners.",
            )

    def _rule_no_pii_or_harmful(self, item: dict) -> None:
        """Rule 4: stem, explanation, and options must contain no PII or harmful content."""
        text_fields = [
            ("stem",        item.get("stem", "")),
            ("explanation", item.get("explanation", "")),
        ]
        for opt in item.get("options", []):
            text_fields.append((f"option_{opt.get('label')}", opt.get("text", "")))

        for field_name, text in text_fields:
            text_lower = text.lower()

            # PII regex
            for pii_name, pattern in _PII_PATTERNS:
                if pattern.search(text):
                    raise ValidationError(
                        "no_pii",
                        f"Field '{field_name}' contains suspected {pii_name} PII.",
                    )

            # Harmful keywords
            words = set(re.findall(r"\b\w+\b", text_lower))
            found = words & _HARMFUL_KEYWORDS
            if found:
                raise ValidationError(
                    "no_harmful",
                    f"Field '{field_name}' contains harmful keyword(s): {sorted(found)}",
                )

            # Brand names
            if _BRAND_PATTERNS.search(text):
                raise ValidationError(
                    "no_brands",
                    f"Field '{field_name}' contains a brand name. Use generic terms.",
                )

    def _rule_irt_params_in_bounds(self, item: dict) -> None:
        """Rule 5: IRT parameters must be within valid bounds."""
        for param, (lo, hi) in VALID_IRT_BOUNDS.items():
            value = item.get(param)
            if value is None:
                raise ValidationError(
                    "irt_params",
                    f"IRT parameter '{param}' is missing.",
                )
            try:
                value = float(value)
            except (TypeError, ValueError):
                raise ValidationError(
                    "irt_params",
                    f"IRT parameter '{param}' is not numeric: {value!r}",
                )
            if not (lo <= value <= hi):
                raise ValidationError(
                    "irt_params",
                    f"IRT parameter '{param}' = {value} is out of bounds [{lo}, {hi}].",
                )

    def _rule_min_options(self, item: dict) -> None:
        """Rule 6: MCQ items must have at least MIN_OPTIONS options."""
        item_type = item.get("item_type", "mcq")
        if item_type != "mcq":
            return   # non-MCQ types don't require options

        options = item.get("options", [])
        if len(options) < MIN_OPTIONS:
            raise ValidationError(
                "min_options",
                f"MCQ item has {len(options)} option(s); minimum is {MIN_OPTIONS}.",
            )

        # Each option must have a non-empty label and text
        for opt in options:
            if not opt.get("label", "").strip():
                raise ValidationError("min_options", f"Option is missing a label: {opt}")
            if not opt.get("text", "").strip():
                raise ValidationError(
                    "min_options",
                    f"Option '{opt.get('label')}' has an empty text field.",
                )

    def _rule_explanation_non_empty(self, item: dict) -> None:
        """Rule 7: explanation must be non-empty and reasonably detailed."""
        explanation = item.get("explanation", "")
        if not explanation or not explanation.strip():
            raise ValidationError("explanation", "explanation field is missing or empty.")
        if len(explanation.split()) < 10:
            raise ValidationError(
                "explanation",
                f"explanation is too short ({len(explanation.split())} words). "
                "Write a full explanation for the learner.",
            )

    def _rule_distractor_rationale_complete(self, item: dict) -> None:
        """Rule 8: distractor_rationale must cover all wrong options."""
        answer_key = str(item.get("answer_key", "")).strip().upper()
        options    = item.get("options", [])
        rationale  = item.get("distractor_rationale", {})

        wrong_labels = {
            str(o.get("label", "")).upper()
            for o in options
            if str(o.get("label", "")).upper() != answer_key
        }

        rationale_labels = {str(k).upper() for k in rationale}
        missing = wrong_labels - rationale_labels

        if missing:
            raise ValidationError(
                "distractor_rationale",
                f"distractor_rationale is missing entries for wrong option(s): "
                f"{sorted(missing)}. All wrong options must have a rationale.",
            )

        # Each rationale entry must be non-empty
        for label in wrong_labels:
            text = rationale.get(label) or rationale.get(label.lower(), "")
            if not str(text).strip():
                raise ValidationError(
                    "distractor_rationale",
                    f"distractor_rationale for option '{label}' is empty.",
                )

    def _rule_misconception_tags_present(self, item: dict) -> None:
        """Additional: at least one misconception_tag required."""
        tags = item.get("misconception_tags", [])
        if not tags:
            raise ValidationError(
                "misconception_tags",
                "misconception_tags list is empty. Provide at least one tag.",
            )

    def _rule_item_type_valid(self, item: dict) -> None:
        """Additional: item_type must be a known enum value."""
        item_type = item.get("item_type", "")
        if item_type not in VALID_ITEM_TYPES:
            raise ValidationError(
                "item_type",
                f"item_type '{item_type}' is not valid. "
                f"Must be one of: {sorted(VALID_ITEM_TYPES)}",
            )

    def _rule_safety_passed(self, item: dict) -> None:
        """Additional: safety_passed must be True."""
        if item.get("safety_passed") is not True:
            raise ValidationError(
                "safety_passed",
                "safety_passed is False or missing. "
                "Item must pass the AI safety check before entering the bank.",
            )
