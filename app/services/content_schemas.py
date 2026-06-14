"""Strict schemas for Phase 1 generated content.

The models reject unknown fields and coercion-prone values so malformed LLM
output cannot silently enter the content-review pipeline. Schema versions are
class metadata rather than serialized payload fields.
"""
from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BloomLevel = Literal["knowledge", "comprehension", "application", "analysis"]
DifficultyBand = Literal["easy", "medium", "hard"]


class StrictPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class DiagnosticItemPayload(StrictPayload):
    """Single multiple-choice diagnostic item."""

    SCHEMA_VERSION: ClassVar[str] = "1.0"

    question: Annotated[str, Field(min_length=10, max_length=300)]
    options: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=200)]],
        Field(min_length=2, max_length=5),
    ]
    correct_answer_index: Annotated[int, Field(ge=0)]
    explanation: Annotated[str, Field(min_length=20, max_length=500)]
    bloom_level: BloomLevel
    difficulty_band: DifficultyBand
    caps_ref: Annotated[
        str,
        Field(min_length=3, max_length=80, pattern=r"^\d+\.[A-Z]+\.\d+(\.\d+)?$"),
    ]
    tags: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def correct_index_in_range(self) -> "DiagnosticItemPayload":
        if self.correct_answer_index >= len(self.options):
            raise ValueError(
                f"correct_answer_index {self.correct_answer_index} is out of range "
                f"for options list of length {len(self.options)}"
            )
        if len(set(self.options)) != len(self.options):
            raise ValueError("options must be unique")
        return self

    @field_validator("question", "explanation", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class DiagnosticItemBatch(StrictPayload):
    """Wrapper for a JSON array of diagnostic items from one generation call."""

    SCHEMA_VERSION: ClassVar[str] = "1.0"
    items: Annotated[list[DiagnosticItemPayload], Field(min_length=1, max_length=20)]

    @classmethod
    def from_list(cls, raw: list[dict[str, object]]) -> "DiagnosticItemBatch":
        return cls(items=[DiagnosticItemPayload.model_validate(item) for item in raw])


class VocabularyEntry(StrictPayload):
    term: Annotated[str, Field(min_length=1, max_length=120)]
    definition: Annotated[str, Field(min_length=1, max_length=400)]


class WorkedExample(StrictPayload):
    problem: Annotated[str, Field(min_length=1, max_length=500)]
    solution: Annotated[str, Field(min_length=1, max_length=2000)]
    answer: Annotated[str, Field(min_length=1, max_length=300)]


class LessonPayload(StrictPayload):
    """A single CAPS-aligned lesson."""

    SCHEMA_VERSION: ClassVar[str] = "1.0"

    title: Annotated[str, Field(min_length=10, max_length=120)]
    caps_ref: Annotated[
        str,
        Field(min_length=3, max_length=80, pattern=r"^\d+\.[A-Z]+\.\d+(\.\d+)?$"),
    ]
    grade: Annotated[int, Field(ge=0, le=12)]
    subject_code: Annotated[str, Field(min_length=1, max_length=20)]
    language: Annotated[str, Field(min_length=2, max_length=5)]
    learning_objectives: Annotated[
        list[Annotated[str, Field(min_length=5, max_length=300)]],
        Field(min_length=1, max_length=10),
    ]
    key_vocabulary: list[VocabularyEntry] = Field(default_factory=list, max_length=50)
    body_markdown: Annotated[str, Field(min_length=100, max_length=10000)]
    worked_examples: list[WorkedExample] = Field(default_factory=list, max_length=10)

    @field_validator("title", "body_markdown", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


CONTENT_TYPE_SCHEMAS: dict[str, type[BaseModel]] = {
    "diagnostic_item": DiagnosticItemPayload,
    "lesson": LessonPayload,
}

CONTENT_TYPE_SCHEMA_VERSIONS: dict[str, str] = {
    "diagnostic_item": DiagnosticItemPayload.SCHEMA_VERSION,
    "lesson": LessonPayload.SCHEMA_VERSION,
}


def get_schema_version(content_type: str) -> str:
    try:
        return CONTENT_TYPE_SCHEMA_VERSIONS[content_type]
    except KeyError as exc:
        raise KeyError(f"Unknown content type: {content_type!r}") from exc
