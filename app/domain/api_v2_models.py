from pydantic import BaseModel, Field


class StudyPlanGenerateRequest(BaseModel):
    gap_ratio: float = Field(default=0.4, ge=0.0, le=1.0)
