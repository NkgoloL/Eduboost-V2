"""
app/domain/data_subject_rights.py
Domain models for §4.3 Data Subject Rights (export, erasure, correction, restriction).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# SLA windows (POPIA §23 – respond within a reasonable time; 30 days is standard)
EXPORT_SLA_DAYS = 30
ERASURE_SLA_DAYS = 30


class RequestStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

class DataExportRequest(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    learner_id: uuid.UUID
    requested_by: uuid.UUID          # guardian_id
    status: RequestStatus = RequestStatus.PENDING
    format: str = "json"             # "json" | "csv"
    download_url: Optional[str] = None
    sla_deadline: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=EXPORT_SLA_DAYS)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    artifact_path: Optional[str] = None

    def is_overdue(self) -> bool:
        return (
            self.status not in {RequestStatus.COMPLETED, RequestStatus.REJECTED}
            and datetime.now(timezone.utc) > self.sla_deadline
        )


# ---------------------------------------------------------------------------
# Erasure
# ---------------------------------------------------------------------------

class ErasureRequest(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    learner_id: uuid.UUID
    requested_by: uuid.UUID
    status: RequestStatus = RequestStatus.PENDING
    review_notes: Optional[str] = None
    legal_hold: bool = False         # blocks execution when True (audit-retention exception)
    sla_deadline: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=ERASURE_SLA_DAYS)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None

    def can_execute(self) -> bool:
        return (
            self.status == RequestStatus.IN_PROGRESS
            and not self.legal_hold
        )


# ---------------------------------------------------------------------------
# Correction
# ---------------------------------------------------------------------------

class CorrectionRequest(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    learner_id: uuid.UUID
    requested_by: uuid.UUID
    field_name: str
    old_value: Optional[str] = None
    new_value: str
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Processing restriction
# ---------------------------------------------------------------------------

class RestrictionRequest(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    learner_id: uuid.UUID
    requested_by: uuid.UUID
    reason: str
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lifted_at: Optional[datetime] = None
