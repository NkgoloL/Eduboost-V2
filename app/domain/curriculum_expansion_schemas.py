"""Strict Phase 7 curriculum expansion and dataset-governance schemas."""
from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class ExpansionPlanRequest(StrictSchema):
    scope_ids: list[str] = Field(min_length=1, max_length=50)
    languages: list[str] = Field(default_factory=lambda: ["en"], min_length=1, max_length=12)
    layers: list[str] = Field(default_factory=lambda: ["diagnostic_items", "lessons"], min_length=1, max_length=8)
    dry_run: bool = True

    @field_validator("scope_ids", "languages", "layers")
    @classmethod
    def unique_nonempty(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values if value.strip()]
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("Values must be unique")
        return cleaned


class CoverageSnapshotRequest(StrictSchema):
    scope_ids: list[str] = Field(min_length=1, max_length=50)
    source_commit_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{7,64}$")


class TrainingManifestCreateRequest(StrictSchema):
    dataset_version: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,95}$")
    scope_ids: list[str] = Field(min_length=1, max_length=50)
    languages: list[str] = Field(min_length=1, max_length=12)
    require_published: bool = True
    min_quality_score: float = Field(default=0.80, ge=0, le=1)
    min_caps_alignment_score: float = Field(default=0.80, ge=0, le=1)
    policy_version: str = Field(default="phase7-training-v1", min_length=1, max_length=40)
    rubric_version: str = Field(default="phase3-review-v1", min_length=1, max_length=40)


class TrainingManifestApproveRequest(StrictSchema):
    decision: Literal["approve", "reject"]
    reason: str = Field(min_length=5, max_length=1000)


class DatasetExportRequest(StrictSchema):
    output_name: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,120}\.jsonl$")


class CoverageSummaryResponse(StrictSchema):
    scope_id: str
    language: str
    target_total: int
    approved_total: int
    gap_count: int
    status: str
    details: dict[str, Any]


class ExpansionPlanResponse(StrictSchema):
    run_id: UUID
    status: str
    dry_run: bool
    plan: dict[str, Any]


class TrainingManifestResponse(StrictSchema):
    manifest_id: UUID
    dataset_version: str
    status: str
    artifact_count: int
    language_counts: dict[str, int]
    scope_counts: dict[str, int]
    dataset_sha256: str | None = None
    output_path: str | None = None
