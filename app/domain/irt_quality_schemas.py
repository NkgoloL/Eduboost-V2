"""Phase 4 IRT quality and self-healing domain contracts."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IRTQualityState(StrEnum):
    UNCALIBRATED = "uncalibrated"
    HEALTHY = "healthy"
    MONITOR = "monitor"
    REVIEW_REQUIRED = "review_required"
    QUARANTINED = "quarantined"
    RETIRED = "retired"
    REWRITE_REVIEW = "rewrite_review"
    OVERRIDDEN = "overridden"


class IRTInterventionAction(StrEnum):
    NONE = "none"
    RETAIN = "retain"
    MONITOR = "monitor"
    REQUIRE_REVIEW = "require_review"
    QUARANTINE = "quarantine"
    RETIRE = "retire"
    CREATE_REWRITE = "create_rewrite"
    MANUAL_OVERRIDE = "manual_override"
    CLEAR_OVERRIDE = "clear_override"


class IRTQualityPolicy(BaseModel):
    """Versioned calibration and intervention policy.

    The fitted model is a conservative two-parameter logistic model using a
    session-rest-score ability proxy. It must not be described as population-
    normed IRT until a qualified statistical reviewer approves a richer
    calibration dataset.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_version: str = "phase4-v1"
    model_version: str = "2pl-session-proxy-v1"
    min_responses: int = Field(default=100, ge=30)
    min_unique_learners: int = Field(default=50, ge=20)
    min_sessions: int = Field(default=20, ge=10)
    min_answered_ratio: float = Field(default=0.95, ge=0.5, le=1.0)
    healthy_discrimination_min: float = Field(default=0.70, ge=0.1, le=3.0)
    monitor_discrimination_min: float = Field(default=0.50, ge=0.1, le=3.0)
    quarantine_discrimination_max: float = Field(default=0.35, ge=0.05, le=2.0)
    max_fit_rmse: float = Field(default=0.35, gt=0.0, le=1.0)
    quarantine_fit_rmse: float = Field(default=0.45, gt=0.0, le=1.0)
    min_acceptable_accuracy: float = Field(default=0.05, ge=0.0, le=0.5)
    max_acceptable_accuracy: float = Field(default=0.95, ge=0.5, le=1.0)
    max_correct_position_share: float = Field(default=0.45, ge=0.25, le=1.0)
    retire_after_strikes: int = Field(default=3, ge=2, le=10)
    max_observations_per_item: int = Field(default=1000, ge=100, le=10000)
    max_parameter_step: float = Field(default=0.35, gt=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_threshold_order(self) -> "IRTQualityPolicy":
        if not (
            self.quarantine_discrimination_max
            < self.monitor_discrimination_min
            <= self.healthy_discrimination_min
        ):
            raise ValueError("IRT discrimination thresholds must be strictly ordered")
        if self.quarantine_fit_rmse < self.max_fit_rmse:
            raise ValueError("quarantine_fit_rmse must be >= max_fit_rmse")
        return self


class IRTCalibrationObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    learner_id: UUID
    session_id: UUID
    ability_proxy: float = Field(ge=-3.0, le=3.0)
    is_correct: bool


class IRTCalibrationMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    response_count: int = Field(ge=0)
    unique_learners: int = Field(ge=0)
    session_count: int = Field(ge=0)
    answered_ratio: float = Field(ge=0.0, le=1.0)
    accuracy: float = Field(ge=0.0, le=1.0)
    difficulty_b: float = Field(ge=-3.0, le=3.0)
    discrimination_a: float = Field(ge=0.05, le=3.0)
    guessing_c: float = Field(ge=0.0, le=0.35)
    fit_rmse: float = Field(ge=0.0, le=1.0)
    converged: bool
    data_quality_passed: bool
    data_quality_reasons: list[str] = Field(default_factory=list)


class IRTCalibrationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    previous_state: IRTQualityState
    next_state: IRTQualityState
    action: IRTInterventionAction
    reason: str
    strike_count: int = Field(ge=0)
    create_rewrite: bool = False
    update_parameters: bool = False


class IRTCalibrationRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = False
    item_ids: list[UUID] | None = None
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=160)


class IRTCalibrationRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    status: str = "queued"


class IRTManualOverrideRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: IRTQualityState
    reason: str = Field(min_length=12, max_length=500)
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_state(self) -> "IRTManualOverrideRequest":
        if self.state not in {
            IRTQualityState.HEALTHY,
            IRTQualityState.MONITOR,
            IRTQualityState.QUARANTINED,
        }:
            raise ValueError("manual override state must be healthy, monitor, or quarantined")
        return self


class IRTItemQualityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: UUID
    state: IRTQualityState
    strike_count: int
    response_count: int
    unique_learners: int
    model_version: str | None
    last_calibrated_at: datetime | None
    last_run_id: UUID | None
    reason: str | None
    manual_override_until: datetime | None
    rewrite_artifact_id: UUID | None


class IRTRunStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    status: str
    dry_run: bool
    model_version: str
    policy_version: str
    summary: dict[str, Any]
    started_at: datetime
    finished_at: datetime | None
