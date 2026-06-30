"""Domain types for Content Factory coverage targets."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ContentLayer(str, Enum):
    TOPIC_MAP = "topic_map"
    DIAGNOSTIC_ITEMS = "diagnostic_items"
    LESSONS = "lessons"
    ASSESSMENT_BLUEPRINTS = "assessment_blueprints"
    STUDY_PLAN_TEMPLATES = "study_plan_templates"


class CoverageTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope_id: str = Field(min_length=1)
    caps_ref: str = Field(min_length=1)
    targets: dict[str, int] = Field(default_factory=dict)


class CoverageTargetRegistryDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    targets: list[CoverageTarget]


class CoverageLayerStatus(str, Enum):
    RED = "red"
    AMBER = "amber"
    GREEN = "green"
    NOT_CONFIGURED = "not_configured"


class CoverageLayerCounts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: int = 0
    approved: int = 0
    pending_review: int = 0
    rejected: int = 0
    generated: int = 0
    status: CoverageLayerStatus
    coverage_ratio: float = 0.0


class CapsRefCoverageReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope_id: str
    caps_ref: str
    layers: dict[ContentLayer, CoverageLayerCounts]


class ScopeCoverageSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_caps_refs: int
    green_refs: int
    amber_refs: int
    red_refs: int
    not_configured_refs: int


class ScopeCoverageLayerSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_total: int = 0
    approved_total: int = 0
    coverage_ratio: float = 0.0


class ScopeCoverageReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope_id: str
    grade: int
    subject_code: str
    language: str
    summary: ScopeCoverageSummary
    layers: dict[ContentLayer, ScopeCoverageLayerSummary]
    per_caps_ref: list[CapsRefCoverageReport]


def coverage_status(approved: int, target: int) -> CoverageLayerStatus:
    if target <= 0:
        return CoverageLayerStatus.NOT_CONFIGURED
    if approved <= 0:
        return CoverageLayerStatus.RED
    if approved < target:
        return CoverageLayerStatus.AMBER
    return CoverageLayerStatus.GREEN
