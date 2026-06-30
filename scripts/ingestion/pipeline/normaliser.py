"""
Content Normaliser  (Pipeline Stage 1)
=======================================
Converts RawContent → NormalisedContent by:

  1. HTML stripping and Unicode normalisation
  2. Subject / grade inference from metadata
  3. Content-type classification
  4. Duplicate detection via SHA-256 hash
  5. Language detection (langdetect)
  6. Confidence scoring

This stage runs entirely in-process and is CPU-bound, so it is
implemented synchronously with an async wrapper for the pipeline.
"""
from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
from typing import Any

from scripts.ingestion.config import (
    GRADE_TO_PHASE,
    SUBJECT_NORMALISATION,
)
from scripts.ingestion.models import (
    ContentType,
    DifficultyLevel,
    NormalisedContent,
    RawContent,
)

logger = logging.getLogger(__name__)

# Seen-content hashes for in-memory dedup within a run
_SEEN_HASHES: set[str] = set()


# ── Public interface ──────────────────────────────────────────────────────────

def normalise(raw: RawContent) -> NormalisedContent | None:
    """
    Normalise a single RawContent record.

    Returns None if the content should be discarded (too short,
    duplicate, or non-educational).
    """
    # ── Text cleaning ────────────────────────────────────────────────────────
    body = _clean_text(raw.raw_text)
    # For MCQ / structured items, include options in the length check so short
    # questions with rich answer choices are not discarded.
    check_body = body
    if raw.raw_json:
        _opts = _coerce_list(raw.raw_json.get("options"))
        if _opts:
            check_body = body + "\n" + "\n".join(f"• {o}" for o in _opts)
        _support = raw.raw_json.get("support") or raw.raw_json.get("passage")
        if _support and _support not in check_body:
            check_body = f"{_support}\n\n{check_body}"
    if len(check_body) < 80:
        logger.debug("[Normaliser] Skipping too-short content from %s", raw.source_id)
        return None

    # ── Duplicate detection ──────────────────────────────────────────────────
    content_hash = hashlib.sha256(body.encode()).hexdigest()
    if content_hash in _SEEN_HASHES:
        logger.debug("[Normaliser] Duplicate content — skipping")
        return None
    _SEEN_HASHES.add(content_hash)

    # ── Metadata extraction ──────────────────────────────────────────────────
    meta      = raw.metadata or {}
    title     = _extract_title(raw)
    subject   = _normalise_subject(meta.get("subject") or meta.get("caps_subject", ""))
    grade     = _extract_grade(meta, raw)
    topic     = meta.get("topic") or meta.get("caps_topic") or None
    subtopic  = meta.get("subtopic") or None
    kind      = _classify_content_type(raw)
    difficulty = _infer_difficulty(meta, grade)
    language  = _detect_language(body, raw.language)

    # ── CAPS phase ───────────────────────────────────────────────────────────
    caps_phase = GRADE_TO_PHASE.get(grade).value if grade else None

    # ── Options / answer extraction for MCQ items ────────────────────────────
    options:     list[str] | None = None
    answer:      str | None       = None
    explanation: str | None       = None

    if raw.raw_json:
        options     = _coerce_list(raw.raw_json.get("options"))
        answer      = raw.raw_json.get("answer") or raw.raw_json.get("correct_answer")
        explanation = (
            raw.raw_json.get("explanation")
            or raw.raw_json.get("solution")
            or raw.raw_json.get("hint")
        )
        # Flatten explanation list → string
        if isinstance(explanation, list):
            explanation = "\n".join(str(e) for e in explanation)

    # ── Confidence scoring ────────────────────────────────────────────────────
    confidence = _compute_confidence(subject, grade, title, kind)

    return NormalisedContent(
        source_id          = raw.source_id,
        source_url         = raw.source_url,
        source_internal_id = raw.source_internal_id,
        subject            = subject or "unknown",
        grade              = grade,
        topic              = topic,
        subtopic           = subtopic,
        content_type       = kind,
        difficulty         = difficulty,
        title              = title,
        body               = body,
        body_html          = raw.raw_html,
        answer             = str(answer) if answer else None,
        options            = options,
        explanation        = str(explanation) if explanation else None,
        caps_phase         = caps_phase,
        caps_subject       = meta.get("caps_subject") or subject,
        caps_topic_code    = meta.get("caps_topic") or meta.get("caps_code"),
        language           = language,
        jurisdiction       = meta.get("jurisdiction", "global"),
        license            = raw.license,
        confidence_score   = confidence,
        extra              = {
            "content_hash": content_hash,
            "source_meta":  meta,
        },
    )


def normalise_batch(items: list[RawContent]) -> list[NormalisedContent]:
    """Normalise a batch of RawContent records, skipping None results."""
    results: list[NormalisedContent] = []
    for raw in items:
        try:
            norm = normalise(raw)
            if norm:
                results.append(norm)
        except Exception as exc:
            logger.error("[Normaliser] Failed on %s: %s", raw.source_id, exc)
    return results


def reset_dedup_cache() -> None:
    """Clear the in-process dedup hash set (use between separate runs)."""
    _SEEN_HASHES.clear()


# ── Text cleaning ─────────────────────────────────────────────────────────────

_WHITESPACE_RE  = re.compile(r"[ \t]+")
_NEWLINE_RE     = re.compile(r"\n{3,}")
_URL_RE         = re.compile(r"https?://\S+")
_HTML_ENT_RE    = re.compile(r"&[a-zA-Z]+;|&#\d+;|&#x[0-9a-fA-F]+;")


def _clean_text(text: str) -> str:
    """Strip HTML entities, normalise whitespace, remove noise."""
    if not text:
        return ""
    # NFKC normalisation (resolves ligatures, compatibility chars)
    text = unicodedata.normalize("NFKC", text)
    # Strip residual HTML entities
    text = _HTML_ENT_RE.sub(" ", text)
    # Collapse inline whitespace
    text = _WHITESPACE_RE.sub(" ", text)
    # Collapse blank lines
    text = _NEWLINE_RE.sub("\n\n", text)
    return text.strip()


# ── Subject normalisation ─────────────────────────────────────────────────────

def _normalise_subject(raw_subject: str) -> str:
    """Map any subject label to a CAPS-canonical lower_snake_case string."""
    if not raw_subject:
        return "unknown"
    key = raw_subject.lower().strip().replace("-", " ").replace("_", " ")
    return SUBJECT_NORMALISATION.get(key, key.replace(" ", "_"))


# ── Grade extraction ──────────────────────────────────────────────────────────

_GRADE_IN_TEXT_RE = re.compile(r"\bgrade\s*(\d{1,2})\b", re.IGNORECASE)


def _extract_grade(meta: dict[str, Any], raw: RawContent) -> int | None:
    """Extract a single representative grade from metadata or source URL."""
    # Direct grade field
    for key in ("grade", "gradeLevel", "grade_level"):
        val = meta.get(key)
        if isinstance(val, int) and 1 <= val <= 12:
            return val
        if isinstance(val, str):
            m = re.search(r"(\d{1,2})", val)
            if m:
                g = int(m.group(1))
                if 1 <= g <= 12:
                    return g

    # Grade range — use median
    grades = meta.get("grades") or meta.get("grade_range")
    if isinstance(grades, (list, tuple)) and grades:
        valid = [g for g in grades if isinstance(g, int) and 1 <= g <= 12]
        if valid:
            return valid[len(valid) // 2]

    # Grade in URL
    if raw.source_url:
        m = re.search(r"grade[-_]?(\d{1,2})", raw.source_url, re.IGNORECASE)
        if m:
            g = int(m.group(1))
            if 1 <= g <= 12:
                return g

    return None


# ── Content-type classification ───────────────────────────────────────────────

_MCQ_SIGNALS   = {"assessment_item", "exercise", "quiz", "practice", "mcq"}
_WORK_SIGNALS  = {"worked_example", "solution", "worked example"}
_VIDEO_SIGNALS = {"video_transcript", "transcript"}
_STD_SIGNALS   = {"curriculum_standard", "standard", "learning_outcome"}


def _classify_content_type(raw: RawContent) -> ContentType:
    """Infer ContentType from source metadata."""
    kind = (raw.metadata.get("kind") or "").lower()

    if kind in _MCQ_SIGNALS or (
        raw.raw_json and raw.raw_json.get("options")
    ):
        return ContentType.ASSESSMENT_ITEM

    if kind in _WORK_SIGNALS or (
        raw.raw_json and raw.raw_json.get("solution")
    ):
        return ContentType.WORKED_EXAMPLE

    if kind in _VIDEO_SIGNALS:
        return ContentType.VIDEO_TRANSCRIPT

    if kind in _STD_SIGNALS:
        return ContentType.CURRICULUM_STANDARD

    if kind in {"textbook_section", "textbook"}:
        return ContentType.TEXTBOOK_SECTION

    if kind in {"reading_passage", "reading", "passage"}:
        return ContentType.READING_PASSAGE

    if kind in {"lesson", "article", "concept"}:
        return ContentType.LESSON

    # Heuristic: presence of options / answer field
    if raw.raw_json:
        if raw.raw_json.get("question") and raw.raw_json.get("answer"):
            return ContentType.ASSESSMENT_ITEM
        if raw.raw_json.get("solution") or raw.raw_json.get("explanation"):
            return ContentType.WORKED_EXAMPLE

    return ContentType.LESSON


# ── Difficulty inference ──────────────────────────────────────────────────────

def _infer_difficulty(meta: dict[str, Any], grade: int | None) -> DifficultyLevel:
    """Map grade / difficulty metadata to a CAPS-style DifficultyLevel."""
    raw_diff = (meta.get("difficulty") or "").lower()
    if "advance" in raw_diff or "hard" in raw_diff or "level 4" in raw_diff:
        return DifficultyLevel.ADVANCED
    if "develop" in raw_diff or "medium" in raw_diff or "level 2" in raw_diff:
        return DifficultyLevel.DEVELOPING
    if "found" in raw_diff or "easy" in raw_diff or "level 1" in raw_diff:
        return DifficultyLevel.FOUNDATION

    # Lexile-based difficulty for CommonLit
    lexile = meta.get("lexile")
    if isinstance(lexile, int):
        if lexile >= 1100:
            return DifficultyLevel.ADVANCED
        if lexile >= 800:
            return DifficultyLevel.ACHIEVED
        if lexile >= 500:
            return DifficultyLevel.DEVELOPING
        return DifficultyLevel.FOUNDATION

    # Grade-based fallback
    if grade:
        if grade >= 10:
            return DifficultyLevel.ACHIEVED
        if grade >= 7:
            return DifficultyLevel.DEVELOPING
    return DifficultyLevel.FOUNDATION


# ── Language detection ────────────────────────────────────────────────────────

def _detect_language(text: str, declared: str) -> str:
    """Use langdetect to verify / override declared language."""
    if declared != "en":
        return declared  # Trust non-English declarations
    try:
        from langdetect import detect  # type: ignore
        lang = detect(text[:500])
        return lang if lang else "en"
    except Exception:
        return declared


# ── Title extraction ──────────────────────────────────────────────────────────

def _extract_title(raw: RawContent) -> str:
    """Best-effort title from metadata or first line of text."""
    title = (
        (raw.metadata or {}).get("title")
        or (raw.raw_json or {}).get("title")
    )
    if title:
        return str(title).strip()[:250]
    # First non-empty line of the text
    for line in raw.raw_text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:250]
    return raw.source_id


# ── Confidence scoring ────────────────────────────────────────────────────────

def _compute_confidence(
    subject: str, grade: int | None, title: str, kind: ContentType
) -> float:
    """
    Assign a 0–1 confidence score to the classification.
    Higher = more reliable for training use.
    """
    score = 1.0
    if subject == "unknown":
        score -= 0.3
    if grade is None:
        score -= 0.2
    if title == "unknown":
        score -= 0.1
    if kind == ContentType.LESSON:
        score -= 0.05  # Lessons are slightly noisier than structured items
    return max(0.1, round(score, 2))


# ── Helpers ───────────────────────────────────────────────────────────────────

def _coerce_list(val: Any) -> list[str] | None:
    if isinstance(val, list) and val:
        return [str(v) for v in val]
    return None
