"""
EduBoost SA — Ingestion Data Models
Pydantic schemas for every stage of the pipeline:
  RawContent → NormalisedContent → TrainingRecord
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ─── Enumerations ────────────────────────────────────────────────────────────

class ContentType(str, Enum):
    LESSON             = "lesson"
    EXERCISE           = "exercise"
    ASSESSMENT_ITEM    = "assessment_item"       # MCQ / short-answer
    VIDEO_TRANSCRIPT   = "video_transcript"
    WORKED_EXAMPLE     = "worked_example"
    TEXTBOOK_SECTION   = "textbook_section"
    CURRICULUM_STANDARD = "curriculum_standard"
    READING_PASSAGE    = "reading_passage"
    DEFINITION         = "definition"
    SUMMARY            = "summary"


class DifficultyLevel(str, Enum):
    FOUNDATION  = "foundation"   # Approx. CAPS Level 1
    DEVELOPING  = "developing"   # Level 2
    ACHIEVED    = "achieved"     # Level 3
    ADVANCED    = "advanced"     # Level 4


class JobStatus(str, Enum):
    PENDING    = "pending"
    RUNNING    = "running"
    COMPLETED  = "completed"
    FAILED     = "failed"
    CANCELLED  = "cancelled"


# ─── Stage 1: Raw Scrape ──────────────────────────────────────────────────────

class RawContent(BaseModel):
    """Unprocessed content exactly as received from a source."""
    id:                 str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id:          str
    source_url:         str | None = None
    source_internal_id: str | None = None   # KA content_id, OpenStax UUID, etc.
    raw_text:           str
    raw_html:           str | None = None
    raw_json:           dict[str, Any] | None = None
    metadata:           dict[str, Any] = Field(default_factory=dict)
    scraped_at:         datetime = Field(default_factory=datetime.utcnow)
    license:            str = "unknown"
    language:           str = "en"
    processed:          bool = False

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── Stage 2: Normalised Content ─────────────────────────────────────────────

class NormalisedContent(BaseModel):
    """
    Cleaned and structured content item, ready for CAPS alignment
    and eventual promotion into the EduBoost item bank.
    """
    id:                 str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id:          str
    source_url:         str | None = None
    source_internal_id: str | None = None

    # ── Curriculum taxonomy ─────────────────────────────────────────────────
    subject:            str                     # normalised lower_snake_case
    grade:              int | None = None       # 1–12; None = multi-grade
    topic:              str | None = None
    subtopic:           str | None = None
    content_type:       ContentType = ContentType.LESSON
    difficulty:         DifficultyLevel | None = None

    # ── Content body ────────────────────────────────────────────────────────
    title:              str
    body:               str                     # cleaned plain text
    body_html:          str | None = None
    answer:             str | None = None       # correct answer for MCQ / SA
    options:            list[str] | None = None # A/B/C/D for MCQ
    explanation:        str | None = None       # solution walkthrough

    # ── CAPS alignment ──────────────────────────────────────────────────────
    caps_phase:             str | None = None   # "foundation"|"intermediate"|…
    caps_subject:           str | None = None   # CAPSSubject value
    caps_topic_code:        str | None = None   # e.g. "NOR", "PFA", "DC"
    caps_learning_outcome:  str | None = None   # verbatim CAPS descriptor
    caps_content_item_code: str | None = None   # e.g. "4.M.1.1"

    # ── Provenance ──────────────────────────────────────────────────────────
    language:           str = "en"
    jurisdiction:       str = "global"
    license:            str = "unknown"
    ingested_at:        datetime = Field(default_factory=datetime.utcnow)
    confidence_score:   float = 1.0             # pipeline confidence in classification
    extra:              dict[str, Any] = Field(default_factory=dict)

    @field_validator("grade")
    @classmethod
    def grade_in_range(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 12):
            raise ValueError(f"grade must be 1–12, got {v}")
        return v

    @field_validator("subject")
    @classmethod
    def subject_lower(cls, v: str) -> str:
        return v.lower().strip()

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─── Stage 3: Training Record ─────────────────────────────────────────────────

class TrainingRecord(BaseModel):
    """
    JSONL record for LLM fine-tuning / RAG ingestion.
    Structured as a system-user-assistant conversation triplet.
    """
    id:             str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id:      str
    caps_code:      str | None = None
    grade:          int | None = None
    subject:        str
    content_type:   ContentType

    # Conversation turns
    system:         str
    user:           str
    assistant:      str

    # Metadata for filtering
    difficulty:     DifficultyLevel | None = None
    jurisdiction:   str = "global"
    language:       str = "en"
    license:        str = "unknown"
    tags:           list[str] = Field(default_factory=list)

    def to_openai_format(self) -> dict[str, Any]:
        """Emit in OpenAI fine-tune JSONL format."""
        return {
            "messages": [
                {"role": "system",    "content": self.system},
                {"role": "user",      "content": self.user},
                {"role": "assistant", "content": self.assistant},
            ]
        }

    def to_anthropic_format(self) -> dict[str, Any]:
        """Emit in Anthropic fine-tune JSONL format."""
        return {
            "system": self.system,
            "messages": [
                {"role": "user",      "content": self.user},
                {"role": "assistant", "content": self.assistant},
            ],
        }


# ─── Curriculum Standard ─────────────────────────────────────────────────────

class CurriculumStandard(BaseModel):
    """A single learning outcome from any curriculum framework."""
    id:           str = Field(default_factory=lambda: str(uuid.uuid4()))
    framework:    str              # "caps", "common_core", "uk_nc", "ib", "ngss"
    code:         str              # e.g. "4.M.1.1" or "CC.4.OA.1"
    grade:        int
    subject:      str
    topic:        str
    description:  str
    jurisdiction: str
    phase:        str | None = None
    keywords:     list[str] = Field(default_factory=list)


class CrossCurriculumMapping(BaseModel):
    """Maps an external standard to a CAPS equivalent."""
    id:             str = Field(default_factory=lambda: str(uuid.uuid4()))
    caps_code:      str
    external_code:  str
    framework:      str
    confidence:     float = 1.0    # 0–1
    mapping_method: str = "manual" # "manual"|"keyword"|"embedding"
    notes:          str | None = None


# ─── Job Tracking ─────────────────────────────────────────────────────────────

class IngestionJob(BaseModel):
    id:              str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id:       str
    started_at:      datetime | None = None
    completed_at:    datetime | None = None
    status:          JobStatus = JobStatus.PENDING
    items_scraped:   int = 0
    items_processed: int = 0
    items_failed:    int = 0
    errors:          list[dict[str, Any]] = Field(default_factory=list)
    config:          dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class IngestionProgress(BaseModel):
    """Live progress snapshot pushed to Redis."""
    job_id:    str
    source_id: str
    status:    JobStatus
    pct:       float = 0.0
    scraped:   int = 0
    processed: int = 0
    failed:    int = 0
    eta_secs:  int | None = None
    message:   str = ""
