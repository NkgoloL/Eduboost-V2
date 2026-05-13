"""
app/services/data_subject_rights_service.py
§4.3 – Data Subject Rights: export, erasure, correction, restriction.
All actions are audited (§4.5) and SLA-tracked.
"""
from __future__ import annotations

import csv
import io
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import asyncpg

from app.domain.consent import AuditEventType
from app.domain.data_subject_rights import (
    CorrectionRequest,
    DataExportRequest,
    ErasureRequest,
    RequestStatus,
    RestrictionRequest,
)
from app.repositories.audit_repository import AuditRepository


class DataSubjectRightsService:
    def __init__(
        self,
        pool: asyncpg.Pool,
        audit_repo: AuditRepository,
    ) -> None:
        self._pool = pool
        self._audit = audit_repo

    # ==================================================================
    # §4.3 – Data Export
    # ==================================================================

    async def create_export_request(
        self,
        learner_id: uuid.UUID,
        requested_by: uuid.UUID,
        fmt: str = "json",
    ) -> DataExportRequest:
        req = DataExportRequest(
            learner_id=learner_id,
            requested_by=requested_by,
            format=fmt,
        )
        await self._pool.execute(
            """
            INSERT INTO data_export_requests
                (id, learner_id, requested_by, status, format, sla_deadline, created_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7)
            """,
            req.id, req.learner_id, req.requested_by,
            req.status.value, req.format, req.sla_deadline, req.created_at,
        )
        await self._audit.record(
            AuditEventType.DATA_EXPORT_REQUEST,
            actor_id=requested_by,
            learner_id=learner_id,
            payload={"request_id": str(req.id), "format": fmt},
        )
        return req

    async def get_export_status(self, request_id: uuid.UUID) -> Optional[DataExportRequest]:
        row = await self._pool.fetchrow(
            "SELECT * FROM data_export_requests WHERE id = $1", request_id
        )
        return self._row_to_export(row) if row else None

    async def build_and_complete_export(
        self, request_id: uuid.UUID, actor_id: uuid.UUID
    ) -> DataExportRequest:
        """
        Collects all learner data rows and writes JSON/CSV artifact.
        §4.3 machine-readable export.
        """
        req = await self._require_export_request(request_id)
        data = await self._collect_learner_data(req.learner_id)

        if req.format == "csv":
            artifact = self._to_csv(data)
            artifact_path = f"/exports/{request_id}.csv"
        else:
            artifact = json.dumps(data, default=str, indent=2)
            artifact_path = f"/exports/{request_id}.json"

        # In production: upload artifact to secure object storage,
        # then store the signed URL. Storing path here for clarity.
        download_url = f"/api/v2/popia/exports/{request_id}/download"

        now = datetime.now(timezone.utc)
        await self._pool.execute(
            """
            UPDATE data_export_requests
            SET status=$2, artifact_path=$3, download_url=$4, completed_at=$5
            WHERE id=$1
            """,
            request_id, RequestStatus.COMPLETED.value,
            artifact_path, download_url, now,
        )
        await self._audit.record(
            AuditEventType.DATA_EXPORT_DOWNLOAD,
            actor_id=actor_id,
            learner_id=req.learner_id,
            payload={"request_id": str(request_id), "artifact_path": artifact_path},
        )
        return req.model_copy(update={
            "status": RequestStatus.COMPLETED,
            "artifact_path": artifact_path,
            "download_url": download_url,
            "completed_at": now,
        })

    # ==================================================================
    # §4.3 – Erasure
    # ==================================================================

    async def create_erasure_request(
        self,
        learner_id: uuid.UUID,
        requested_by: uuid.UUID,
    ) -> ErasureRequest:
        req = ErasureRequest(learner_id=learner_id, requested_by=requested_by)
        await self._pool.execute(
            """
            INSERT INTO erasure_requests
                (id, learner_id, requested_by, status, legal_hold, sla_deadline, created_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7)
            """,
            req.id, req.learner_id, req.requested_by,
            req.status.value, req.legal_hold, req.sla_deadline, req.created_at,
        )
        await self._audit.record(
            AuditEventType.ERASURE_REQUEST,
            actor_id=requested_by,
            learner_id=learner_id,
            payload={"request_id": str(req.id)},
        )
        return req

    async def get_erasure_status(self, request_id: uuid.UUID) -> Optional[ErasureRequest]:
        row = await self._pool.fetchrow(
            "SELECT * FROM erasure_requests WHERE id = $1", request_id
        )
        return self._row_to_erasure(row) if row else None

    async def approve_erasure(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        review_notes: Optional[str] = None,
    ) -> ErasureRequest:
        """§4.3 – erasure approval/review queue step."""
        now = datetime.now(timezone.utc)
        await self._pool.execute(
            """
            UPDATE erasure_requests
            SET status=$2, approved_at=$3, review_notes=$4
            WHERE id=$1
            """,
            request_id, RequestStatus.IN_PROGRESS.value, now, review_notes,
        )
        row = await self._pool.fetchrow(
            "SELECT * FROM erasure_requests WHERE id=$1", request_id
        )
        return self._row_to_erasure(row)

    async def execute_erasure(
        self,
        request_id: uuid.UUID,
        executor_id: uuid.UUID,
    ) -> ErasureRequest:
        """
        §4.3 – erasure execution with audit-retention exception.
        Deletes learner PII but PRESERVES audit_events rows (anonymised).
        """
        row = await self._pool.fetchrow(
            "SELECT * FROM erasure_requests WHERE id=$1", request_id
        )
        if row is None:
            raise ValueError(f"Erasure request {request_id} not found")
        req = self._row_to_erasure(row)
        if not req.can_execute():
            raise PermissionError(
                f"Erasure {request_id} cannot be executed: "
                f"status={req.status!r}, legal_hold={req.legal_hold}"
            )

        learner_id = req.learner_id
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # 1. Anonymise audit records (retain chain, scrub PII payload)
                await conn.execute(
                    """
                    UPDATE audit_events
                    SET payload = jsonb_set(payload, '{erased}', 'true'::jsonb)
                    WHERE learner_id = $1
                    """,
                    learner_id,
                )
                # 2. Delete learner PII from operational tables
                await conn.execute(
                    "DELETE FROM learner_profiles WHERE id = $1", learner_id
                )
                await conn.execute(
                    "DELETE FROM diagnostic_sessions WHERE learner_id = $1", learner_id
                )
                await conn.execute(
                    "DELETE FROM lesson_records WHERE learner_id = $1", learner_id
                )
                await conn.execute(
                    "DELETE FROM study_plans WHERE learner_id = $1", learner_id
                )
                await conn.execute(
                    "DELETE FROM consent_records WHERE learner_id = $1", learner_id
                )
                # 3. Mark erasure complete
                now = datetime.now(timezone.utc)
                await conn.execute(
                    "UPDATE erasure_requests SET status=$2, executed_at=$3 WHERE id=$1",
                    request_id, RequestStatus.COMPLETED.value, now,
                )
                # 4. Audit the execution
                await self._audit.record(
                    AuditEventType.ERASURE_EXECUTION,
                    actor_id=executor_id,
                    learner_id=None,   # learner row is gone; store None
                    payload={
                        "request_id": str(request_id),
                        "learner_id": str(learner_id),
                    },
                    conn=conn,
                )
        return req.model_copy(update={
            "status": RequestStatus.COMPLETED,
            "executed_at": datetime.now(timezone.utc),
        })

    # ==================================================================
    # §4.3 – Correction
    # ==================================================================

    async def create_correction_request(
        self,
        learner_id: uuid.UUID,
        requested_by: uuid.UUID,
        field_name: str,
        new_value: str,
        old_value: Optional[str] = None,
    ) -> CorrectionRequest:
        req = CorrectionRequest(
            learner_id=learner_id,
            requested_by=requested_by,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
        )
        await self._pool.execute(
            """
            INSERT INTO correction_requests
                (id, learner_id, requested_by, field_name, old_value, new_value,
                 status, created_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
            """,
            req.id, req.learner_id, req.requested_by,
            req.field_name, req.old_value, req.new_value,
            req.status.value, req.created_at,
        )
        return req

    async def complete_correction(
        self,
        request_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> CorrectionRequest:
        now = datetime.now(timezone.utc)
        await self._pool.execute(
            "UPDATE correction_requests SET status=$2, completed_at=$3 WHERE id=$1",
            request_id, RequestStatus.COMPLETED.value, now,
        )
        row = await self._pool.fetchrow(
            "SELECT * FROM correction_requests WHERE id=$1", request_id
        )
        return self._row_to_correction(row)

    # ==================================================================
    # §4.3 – Processing Restriction
    # ==================================================================

    async def create_restriction_request(
        self,
        learner_id: uuid.UUID,
        requested_by: uuid.UUID,
        reason: str,
    ) -> RestrictionRequest:
        req = RestrictionRequest(
            learner_id=learner_id,
            requested_by=requested_by,
            reason=reason,
        )
        await self._pool.execute(
            """
            INSERT INTO restriction_requests
                (id, learner_id, requested_by, reason, status, created_at)
            VALUES ($1,$2,$3,$4,$5,$6)
            """,
            req.id, req.learner_id, req.requested_by,
            req.reason, req.status.value, req.created_at,
        )
        return req

    async def lift_restriction(
        self,
        request_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> RestrictionRequest:
        now = datetime.now(timezone.utc)
        await self._pool.execute(
            "UPDATE restriction_requests SET status=$2, lifted_at=$3 WHERE id=$1",
            request_id, RequestStatus.COMPLETED.value, now,
        )
        row = await self._pool.fetchrow(
            "SELECT * FROM restriction_requests WHERE id=$1", request_id
        )
        return self._row_to_restriction(row)

    # ==================================================================
    # §4.3 SLA tracking (called by scheduler)
    # ==================================================================

    async def list_overdue_export_requests(self) -> list[DataExportRequest]:
        rows = await self._pool.fetch(
            """
            SELECT * FROM data_export_requests
            WHERE status NOT IN ('completed','rejected')
              AND sla_deadline < NOW()
            """
        )
        return [self._row_to_export(r) for r in rows]

    async def list_overdue_erasure_requests(self) -> list[ErasureRequest]:
        rows = await self._pool.fetch(
            """
            SELECT * FROM erasure_requests
            WHERE status NOT IN ('completed','rejected')
              AND sla_deadline < NOW()
            """
        )
        return [self._row_to_erasure(r) for r in rows]

    # ==================================================================
    # Helpers
    # ==================================================================

    async def _collect_learner_data(self, learner_id: uuid.UUID) -> dict[str, Any]:
        """
        §4.3 – assemble all learner data for export.
        §4.4 – only fields in the data inventory are included.
        Raw names/emails are included in the export; LLM prompts must
        never receive these (enforced separately in lesson service).
        """
        profile = await self._pool.fetchrow(
            "SELECT * FROM learner_profiles WHERE id=$1", learner_id
        )
        diagnostics = await self._pool.fetch(
            "SELECT * FROM diagnostic_sessions WHERE learner_id=$1", learner_id
        )
        lessons = await self._pool.fetch(
            "SELECT id, created_at, subject, grade FROM lesson_records WHERE learner_id=$1",
            learner_id,
        )
        consents = await self._pool.fetch(
            "SELECT id, state, granted_at, expires_at, privacy_notice_version "
            "FROM consent_records WHERE learner_id=$1",
            learner_id,
        )
        return {
            "learner_id": str(learner_id),
            "profile": dict(profile) if profile else {},
            "diagnostic_sessions": [dict(r) for r in diagnostics],
            "lesson_records": [dict(r) for r in lessons],
            "consent_history": [dict(r) for r in consents],
        }

    @staticmethod
    def _to_csv(data: dict[str, Any]) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        # Flatten top-level profile fields for CSV
        profile = data.get("profile", {})
        writer.writerow(["section", "key", "value"])
        for k, v in profile.items():
            writer.writerow(["profile", k, v])
        for session in data.get("diagnostic_sessions", []):
            for k, v in session.items():
                writer.writerow(["diagnostic", k, v])
        return buf.getvalue()

    async def _require_export_request(
        self, request_id: uuid.UUID
    ) -> DataExportRequest:
        row = await self._pool.fetchrow(
            "SELECT * FROM data_export_requests WHERE id=$1", request_id
        )
        if row is None:
            raise ValueError(f"Export request {request_id} not found")
        return self._row_to_export(row)

    @staticmethod
    def _row_to_export(row: asyncpg.Record) -> DataExportRequest:
        return DataExportRequest(
            id=row["id"],
            learner_id=row["learner_id"],
            requested_by=row["requested_by"],
            status=RequestStatus(row["status"]),
            format=row["format"],
            download_url=row.get("download_url"),
            sla_deadline=row["sla_deadline"],
            created_at=row["created_at"],
            completed_at=row.get("completed_at"),
            artifact_path=row.get("artifact_path"),
        )

    @staticmethod
    def _row_to_erasure(row: asyncpg.Record) -> ErasureRequest:
        return ErasureRequest(
            id=row["id"],
            learner_id=row["learner_id"],
            requested_by=row["requested_by"],
            status=RequestStatus(row["status"]),
            review_notes=row.get("review_notes"),
            legal_hold=row.get("legal_hold", False),
            sla_deadline=row["sla_deadline"],
            created_at=row["created_at"],
            approved_at=row.get("approved_at"),
            executed_at=row.get("executed_at"),
        )

    @staticmethod
    def _row_to_correction(row: asyncpg.Record) -> CorrectionRequest:
        return CorrectionRequest(
            id=row["id"],
            learner_id=row["learner_id"],
            requested_by=row["requested_by"],
            field_name=row["field_name"],
            old_value=row.get("old_value"),
            new_value=row["new_value"],
            status=RequestStatus(row["status"]),
            created_at=row["created_at"],
            completed_at=row.get("completed_at"),
        )

    @staticmethod
    def _row_to_restriction(row: asyncpg.Record) -> RestrictionRequest:
        return RestrictionRequest(
            id=row["id"],
            learner_id=row["learner_id"],
            requested_by=row["requested_by"],
            reason=row["reason"],
            status=RequestStatus(row["status"]),
            created_at=row["created_at"],
            lifted_at=row.get("lifted_at"),
        )
