"""
Training Formatter  (Pipeline Stage 3)
========================================
Converts NormalisedContent → TrainingRecord (system-user-assistant triplets)
ready for LLM fine-tuning or RAG indexing.

Template selection is content-type driven:
  • ASSESSMENT_ITEM   → MCQ answering with justification
  • WORKED_EXAMPLE    → step-by-step solution walkthrough
  • TEXTBOOK_SECTION  → conceptual explanation / tutoring
  • READING_PASSAGE   → comprehension and inference
  • CURRICULUM_STD    → learning-goal articulation
  • LESSON / default  → socratic teaching dialogue

Output formats:
  • OpenAI fine-tuning JSONL  (messages array)
  • Anthropic fine-tuning JSONL (system + messages)
  • RAG document JSON          (for embedding / vector store ingestion)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from scripts.ingestion.models import (
    ContentType,
    NormalisedContent,
    TrainingRecord,
)

logger = logging.getLogger(__name__)

# ── System prompt template ────────────────────────────────────────────────────

_CAPS_SYSTEM = (
    "You are EduBoostAI, an expert South African tutor aligned to the CAPS "
    "curriculum (Curriculum and Assessment Policy Statement). "
    "You teach Grades 1–12 across all CAPS subjects. "
    "Your responses are accurate, patient, and appropriately scaffolded for "
    "the learner's grade level. "
    "When solving problems, show each step clearly. "
    "Use South African examples, currency (ZAR), and context where relevant."
)


# ── Public interface ──────────────────────────────────────────────────────────

def format_record(content: NormalisedContent) -> TrainingRecord | None:
    """
    Produce a TrainingRecord from a NormalisedContent item.
    Returns None if the content is unsuitable for training use.
    """
    if content.confidence_score < 0.3:
        logger.debug("[Formatter] Skipping low-confidence record: %.2f", content.confidence_score)
        return None
    if len(content.body) < 50:
        return None

    ctype = content.content_type

    if ctype == ContentType.ASSESSMENT_ITEM:
        user_msg, asst_msg = _format_mcq(content)
    elif ctype == ContentType.WORKED_EXAMPLE:
        user_msg, asst_msg = _format_worked_example(content)
    elif ctype == ContentType.TEXTBOOK_SECTION:
        user_msg, asst_msg = _format_textbook(content)
    elif ctype == ContentType.READING_PASSAGE:
        user_msg, asst_msg = _format_reading(content)
    elif ctype == ContentType.CURRICULUM_STANDARD:
        user_msg, asst_msg = _format_standard(content)
    elif ctype == ContentType.VIDEO_TRANSCRIPT:
        user_msg, asst_msg = _format_transcript(content)
    else:
        user_msg, asst_msg = _format_lesson(content)

    if not user_msg or not asst_msg:
        return None

    # Build CAPS code for filtering
    caps_code = _build_caps_code(content)

    return TrainingRecord(
        source_id    = content.source_id,
        caps_code    = caps_code,
        grade        = content.grade,
        subject      = content.subject,
        content_type = ctype,
        system       = _CAPS_SYSTEM,
        user         = user_msg,
        assistant    = asst_msg,
        difficulty   = content.difficulty,
        jurisdiction = content.jurisdiction,
        language     = content.language,
        license      = content.license,
        tags         = _build_tags(content),
    )


def format_batch(items: list[NormalisedContent]) -> list[TrainingRecord]:
    """Format a batch, silently dropping None results."""
    records: list[TrainingRecord] = []
    for item in items:
        try:
            rec = format_record(item)
            if rec:
                records.append(rec)
        except Exception as exc:
            logger.error("[Formatter] Error formatting %s: %s", item.source_id, exc)
    return records


def export_jsonl(
    records: list[TrainingRecord],
    output_path: str | Path,
    fmt: str = "openai",
) -> int:
    """
    Write training records to a JSONL file.

    Parameters
    ----------
    records     : list of TrainingRecord
    output_path : file path for the output JSONL
    fmt         : "openai" | "anthropic" | "rag"

    Returns
    -------
    Number of records written.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            if fmt == "anthropic":
                row = rec.to_anthropic_format()
            elif fmt == "rag":
                row = _to_rag_format(rec)
            else:
                row = rec.to_openai_format()
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            written += 1

    logger.info("[Formatter] Wrote %d records to %s (format=%s)", written, path, fmt)
    return written


# ── Content-type formatters ───────────────────────────────────────────────────

def _format_mcq(c: NormalisedContent) -> tuple[str, str]:
    """MCQ / assessment item → question + justified answer."""
    stem = c.body[:800].strip()

    if c.options:
        labelled = "\n".join(
            f"  {chr(65+i)}) {opt}"
            for i, opt in enumerate(c.options)
        )
        user_msg = (
            f"Grade {c.grade or '?'} {_subject_label(c.subject)} question:\n\n"
            f"{stem}\n\n"
            f"Options:\n{labelled}\n\n"
            "Select the correct option and explain your reasoning."
        )
    else:
        user_msg = (
            f"Grade {c.grade or '?'} {_subject_label(c.subject)} question:\n\n"
            f"{stem}\n\n"
            "Answer this question and explain how you arrived at your answer."
        )

    answer = c.answer or "See solution below."
    explanation = c.explanation or ""
    asst_msg = f"**Answer:** {answer}"
    if explanation:
        asst_msg += f"\n\n**Explanation:**\n{explanation[:1200]}"

    return user_msg, asst_msg


def _format_worked_example(c: NormalisedContent) -> tuple[str, str]:
    """Worked example → step-by-step solution walkthrough."""
    problem = (
        c.body[:600].strip()
        if not c.options
        else f"{c.title}\n\n{c.body[:500].strip()}"
    )
    user_msg = (
        f"Please work through this Grade {c.grade or '?'} "
        f"{_subject_label(c.subject)} problem step by step:\n\n{problem}"
    )
    solution = c.explanation or c.answer or c.body[:1200]
    asst_msg = f"**Step-by-step solution:**\n\n{solution.strip()}"
    return user_msg, asst_msg


def _format_textbook(c: NormalisedContent) -> tuple[str, str]:
    """Textbook section → concise explanation in tutoring style."""
    topic = c.topic or c.title
    user_msg = (
        f"Explain the topic **{topic}** as it appears in the Grade {c.grade or '?'} "
        f"CAPS {_subject_label(c.subject)} curriculum.  "
        "Include key definitions, worked examples, and common misconceptions."
    )
    # Use first 1 200 chars of body as the answer base — models learn to
    # replicate this explanatory style
    body_excerpt = c.body[:1200].strip()
    asst_msg = body_excerpt
    return user_msg, asst_msg


def _format_reading(c: NormalisedContent) -> tuple[str, str]:
    """Reading passage → comprehension scaffolding."""
    user_msg = (
        f"Read the following Grade {c.grade or '?'} passage and answer:\n\n"
        f"**{c.title}**\n\n"
        f"{c.body[:1000].strip()}\n\n"
        "1. What is the main idea of this passage?\n"
        "2. Identify one piece of evidence the author uses.\n"
        "3. What inference can you draw from the text?"
    )
    answer = c.answer or (
        "1. The main idea is presented in the opening paragraph.\n"
        "2. Evidence is provided through direct statements and examples.\n"
        "3. An inference should connect information across the text."
    )
    asst_msg = answer[:1400]
    return user_msg, asst_msg


def _format_standard(c: NormalisedContent) -> tuple[str, str]:
    """Curriculum standard → learning-goal description."""
    user_msg = (
        f"Describe the CAPS learning outcome for Grade {c.grade or '?'} "
        f"{_subject_label(c.subject)}"
        + (f" ({c.caps_topic_code})" if c.caps_topic_code else "")
        + ".  What should a learner be able to do by the end of this topic?"
    )
    asst_msg = c.caps_learning_outcome or c.body[:800]
    return user_msg, asst_msg


def _format_transcript(c: NormalisedContent) -> tuple[str, str]:
    """Video transcript → lesson summary."""
    user_msg = (
        f"Summarise this {_subject_label(c.subject)} lesson transcript "
        f"for a Grade {c.grade or '?'} learner, highlighting key concepts:\n\n"
        f"{c.body[:800].strip()}"
    )
    asst_msg = c.body[:1200].strip()
    return user_msg, asst_msg


def _format_lesson(c: NormalisedContent) -> tuple[str, str]:
    """Generic lesson → socratic tutoring dialogue."""
    user_msg = (
        f"I'm a Grade {c.grade or '?'} learner studying "
        f"{_subject_label(c.subject)}.  "
        f"Can you teach me about: **{c.title}**?"
    )
    asst_msg = c.body[:1400].strip()
    return user_msg, asst_msg


# ── RAG export format ─────────────────────────────────────────────────────────

def _to_rag_format(rec: TrainingRecord) -> dict[str, Any]:
    """Emit a flat document dict suitable for vector-store ingestion."""
    return {
        "id":          rec.id,
        "text":        f"{rec.user}\n\n{rec.assistant}",
        "metadata": {
            "source":      rec.source_id,
            "subject":     rec.subject,
            "grade":       rec.grade,
            "caps_code":   rec.caps_code,
            "difficulty":  rec.difficulty.value if rec.difficulty else None,
            "language":    rec.language,
            "license":     rec.license,
            "content_type":rec.content_type.value,
            "tags":        rec.tags,
        },
    }


# ── Utility helpers ───────────────────────────────────────────────────────────

def _subject_label(subject: str) -> str:
    """Produce a human-readable subject label from a snake_case key."""
    return subject.replace("_", " ").title()


def _build_caps_code(c: NormalisedContent) -> str | None:
    if c.caps_content_item_code:
        return c.caps_content_item_code
    parts = [
        str(c.grade) if c.grade else "",
        _subject_initial(c.subject),
        c.caps_topic_code or "",
    ]
    code = ".".join(p for p in parts if p)
    return code or None


def _subject_initial(subject: str) -> str:
    mapping = {
        "mathematics": "M", "mathematical_literacy": "ML",
        "life_sciences": "LS", "physical_sciences": "PS",
        "natural_sciences": "NS", "english_home_language": "EHL",
        "english_first_additional_language": "EFAL",
        "history": "HIS", "geography": "GEO",
        "economics": "ECO", "accounting": "ACC",
        "business_studies": "BS", "life_orientation": "LO",
        "technology": "TEC", "creative_arts": "CA",
    }
    return mapping.get(subject, subject[:3].upper())


def _build_tags(c: NormalisedContent) -> list[str]:
    tags: list[str] = []
    if c.grade:
        tags.append(f"grade-{c.grade}")
    if c.caps_phase:
        tags.append(f"phase-{c.caps_phase}")
    if c.subject:
        tags.append(f"subject-{c.subject}")
    if c.caps_topic_code:
        tags.append(f"topic-{c.caps_topic_code}")
    if c.jurisdiction != "global":
        tags.append(f"jurisdiction-{c.jurisdiction}")
    if c.difficulty:
        tags.append(f"difficulty-{c.difficulty.value}")
    if c.language != "en":
        tags.append(f"lang-{c.language}")
    tags.append(f"source-{c.source_id}")
    tags.append(f"type-{c.content_type.value}")
    return tags
