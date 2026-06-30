"""Domain types for CAPS source-document inventory."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SourceDocumentStatus(str, Enum):
    PLANNED = "planned"
    SOURCE_LOADED = "source_loaded"
    TOPIC_MAP_APPROVED = "topic_map_approved"
    RETIRED = "retired"
    NOT_APPLICABLE = "not_applicable"


class SourceDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    curriculum: str = Field(min_length=1)
    phase: str = Field(min_length=1)
    grades: list[int] = Field(default_factory=list)
    subjects: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    status: SourceDocumentStatus
    language_role: str | None = None
    language_code: str | None = None
    canonical_source_url: str | None = None
    source_path: str | None = None
    object_store_uri: str | None = None
    source_hash: str | None = None
    source_sha256: str | None = None
    retrieved_at: str | None = None
    downloaded_at: str | None = None
    published_at: str | None = None
    reviewed_at: str | None = None
    reviewer_id: str | None = None
    evidence_notes: str | None = None
    notes: str | None = None


class PlannedSourceRequirements(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    required_fields_before_generation: list[str] = Field(default_factory=list)


class SourceDocumentManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    documents: list[SourceDocument]
    planned_source_requirements: PlannedSourceRequirements
