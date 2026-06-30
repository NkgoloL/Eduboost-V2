"""Domain types for file-backed Content Factory scopes."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ContentScopeStatus(str, Enum):
    PLANNED = "planned"
    SOURCE_LOADED = "source_loaded"
    GENERATING = "generating"
    REVIEW = "review"
    ACTIVE = "active"
    RETIRED = "retired"
    DRAFT = "draft"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ContentScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope_id: str = Field(min_length=1)
    grade: int = Field(ge=0, le=12)
    subject_code: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    language: str = Field(min_length=2, max_length=8)
    curriculum: str = Field(min_length=1)
    status: ContentScopeStatus
    topic_map_path: str | None = None
    caps_refs: list[str] = Field(default_factory=list)
    phase: str | None = None
    curriculum_version: str | None = None
    source_documents: list[str] = Field(default_factory=list)
    coverage_policy_id: str | None = None
    review_policy_id: str | None = None
    artifact_paths: dict[str, str] = Field(default_factory=dict)


class ContentScopeRegistryDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    scopes: list[ContentScope]
