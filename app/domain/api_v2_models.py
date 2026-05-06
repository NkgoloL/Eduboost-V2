from typing import Any

from pydantic import BaseModel, Field


class StudyPlanGenerateRequest(BaseModel):
    gap_ratio: float = Field(default=0.4, ge=0.0, le=1.0)


class JobAcceptedResponse(BaseModel):
    job_id: str
    operation: str
    status: str = "queued"


class JobStatusResponse(JobAcceptedResponse):
    payload: dict[str, Any] = Field(default_factory=dict)
    result: Any | None = None
    error: dict[str, Any] | None = None
    created_at: str
    updated_at: str


class RLHFExportRequest(BaseModel):
    records: list[dict[str, Any]] = Field(default_factory=list)
