"""POPIA data-subject-rights service.

The service centralises learner export, erasure-request, correction, and
processing-restriction workflows so routers do not assemble compliance payloads
ad hoc. It intentionally preserves append-only audit records and returns only
structured, machine-readable status metadata.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from io import StringIO
from typing import Any, Literal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorization import assert_can_access_learner
from app.models import DiagnosticSession, KnowledgeGap, LearnerProfile, Lesson, ParentalConsent
from app.repositories.audit_repository import AuditRepository
from app.repositories.repositories import LearnerRepository
from app.services.consent import ConsentService

POPIA_EXPORT_SLA_DAYS = 30
POPIA_ERASURE_REVIEW_SLA_DAYS = 30
POPIA_ERASURE_GRACE_DAYS = 30


@dataclass(frozen=True)
class RightsRequestStatus:
    request_type: str
    status: Literal["accepted", "completed", "pending_review", "cancelled"]
    learner_id: str
    requested_at: str
    due_at: str
    audit_event_type: str
    requires_admin_review: bool = False
    reason: str | None = None


def _now() -> datetime:
    return datetime.now(UTC)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class POPIADataRightsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.learners = LearnerRepository(db)
        self.audit = AuditRepository(db)
        self.consent = ConsentService(db)

    async def load_authorized_learner(self, learner_id: str, current_user: dict[str, Any]) -> LearnerProfile:
        learner = await self.learners.get_by_id(learner_id)
        if learner is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
        assert_can_access_learner(current_user, learner)
        return learner

    async def build_learner_export(
        self,
        learner_id: str,
        current_user: dict[str, Any],
        *,
        export_format: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        requester_id = str(current_user.get("sub") or "")
        learner = await self.load_authorized_learner(learner_id, current_user)
        await self.consent.require_active_consent(learner_id, actor_id=requester_id)

        payload = await self._export_payload(learner)
        await self.audit.append(
            "data_export.requested",
            actor_id=requester_id,
            resource_id=learner_id,
            payload={
                "learner_id": learner_id,
                "learner_pseudonym": learner.pseudonym_id,
                "format": export_format,
                "sla_days": POPIA_EXPORT_SLA_DAYS,
            },
        )
        filename_base = f"eduboost_data_export_{learner_id}_{_now().strftime('%Y%m%d_%H%M%S')}"
        if export_format == "csv":
            return {
                "filename": f"{filename_base}.csv",
                "content_type": "text/csv",
                "data": self._to_csv(payload),
                "status": asdict(self._status("export", "completed", learner_id, POPIA_EXPORT_SLA_DAYS, "data_export.requested")),
            }
        return {
            "filename": f"{filename_base}.json",
            "content_type": "application/json",
            "data": payload,
            "status": asdict(self._status("export", "completed", learner_id, POPIA_EXPORT_SLA_DAYS, "data_export.requested")),
        }

    async def request_erasure(self, learner_id: str, current_user: dict[str, Any], *, reason: str = "guardian_request") -> dict[str, Any]:
        requester_id = str(current_user.get("sub") or "")
        learner = await self.load_authorized_learner(learner_id, current_user)
        if str(learner.guardian_id) != requester_id and str(current_user.get("role", "")).lower() != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the learner's guardian or admin can request erasure")
        if learner.deletion_requested_at is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erasure already requested for this learner")

        learner.is_deleted = True
        learner.deletion_requested_at = _now()
        self.db.add(learner)
        await self.consent.execute_erasure(requester_id, learner_id)
        review_required = await self.requires_admin_review(learner)
        status_obj = self._status(
            "erasure",
            "pending_review" if review_required else "accepted",
            learner_id,
            POPIA_ERASURE_REVIEW_SLA_DAYS,
            "erasure.requested",
            requires_admin_review=review_required,
            reason=reason,
        )
        await self.audit.append(
            "erasure.requested",
            actor_id=requester_id,
            resource_id=learner_id,
            payload={
                "learner_id": learner_id,
                "learner_pseudonym": learner.pseudonym_id,
                "reason": reason,
                "grace_period_days": POPIA_ERASURE_GRACE_DAYS,
                "requires_admin_review": review_required,
                "preserve_audit_records": True,
            },
        )
        await self.db.flush()
        return asdict(status_obj)

    async def cancel_erasure(self, learner_id: str, current_user: dict[str, Any]) -> dict[str, Any]:
        requester_id = str(current_user.get("sub") or "")
        learner = await self.load_authorized_learner(learner_id, current_user)
        if learner.deletion_requested_at is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No erasure request exists for this learner")
        learner.is_deleted = False
        learner.deletion_requested_at = None
        self.db.add(learner)
        await self.audit.append(
            "erasure.cancelled",
            actor_id=requester_id,
            resource_id=learner_id,
            payload={"learner_id": learner_id, "learner_pseudonym": learner.pseudonym_id},
        )
        await self.db.flush()
        return asdict(self._status("erasure", "cancelled", learner_id, POPIA_ERASURE_REVIEW_SLA_DAYS, "erasure.cancelled"))

    async def request_correction(
        self,
        learner_id: str,
        current_user: dict[str, Any],
        fields: dict[str, Any],
        *,
        reason: str,
    ) -> dict[str, Any]:
        requester_id = str(current_user.get("sub") or "")
        learner = await self.load_authorized_learner(learner_id, current_user)
        allowed = {"display_name", "grade", "language"}
        rejected = sorted(set(fields) - allowed)
        if rejected:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"unsupported_fields": rejected})
        updates = {key: value for key, value in fields.items() if key in allowed}
        for key, value in updates.items():
            setattr(learner, key, value)
        self.db.add(learner)
        await self.audit.append(
            "data_subject.correction_requested",
            actor_id=requester_id,
            resource_id=learner_id,
            payload={"learner_id": learner_id, "fields": sorted(updates), "reason": reason},
        )
        await self.db.flush()
        return asdict(self._status("correction", "completed", learner_id, POPIA_EXPORT_SLA_DAYS, "data_subject.correction_requested"))

    async def restrict_processing(
        self,
        learner_id: str,
        current_user: dict[str, Any],
        *,
        reason: str,
    ) -> dict[str, Any]:
        requester_id = str(current_user.get("sub") or "")
        learner = await self.load_authorized_learner(learner_id, current_user)
        await self.consent.revoke(learner_id, guardian_id=requester_id, reason="processing_restricted")
        await self.audit.append(
            "processing.restricted",
            actor_id=requester_id,
            resource_id=learner_id,
            payload={"learner_id": learner_id, "learner_pseudonym": learner.pseudonym_id, "reason": reason},
        )
        await self.db.flush()
        return asdict(self._status("restriction", "accepted", learner_id, POPIA_EXPORT_SLA_DAYS, "processing.restricted", reason=reason))

    async def requires_admin_review(self, learner: LearnerProfile) -> bool:
        # Current minimal policy: billing/school-retained records are not modeled
        # yet, but an admin queue hook is exposed and audited for future rules.
        return False

    async def _export_payload(self, learner: LearnerProfile) -> dict[str, Any]:
        learner_id = learner.id
        diagnostic_sessions = list((await self.db.scalars(select(DiagnosticSession).where(DiagnosticSession.learner_id == learner_id))).all())
        lessons = list((await self.db.scalars(select(Lesson).where(Lesson.learner_id == learner_id))).all())
        gaps = list((await self.db.scalars(select(KnowledgeGap).where(KnowledgeGap.learner_id == learner_id))).all())
        consents = list((await self.db.scalars(select(ParentalConsent).where(ParentalConsent.learner_id == learner_id))).all())
        return {
            "export_date": _now().isoformat(),
            "learner": {
                "id": learner.id,
                "pseudonym_id": learner.pseudonym_id,
                "display_name": learner.display_name,
                "grade": learner.grade,
                "language": str(learner.language),
                "archetype": str(learner.archetype) if learner.archetype else None,
                "theta": learner.theta,
                "xp": learner.xp,
                "streak_days": learner.streak_days,
                "created_at": _iso(learner.created_at),
                "last_active": _iso(learner.last_active),
            },
            "diagnostic_sessions": [
                {"id": row.id, "theta_before": row.theta_before, "theta_after": row.theta_after, "completed_at": _iso(row.completed_at), "created_at": _iso(row.created_at)}
                for row in diagnostic_sessions
            ],
            "lessons": [
                {"id": row.id, "grade": row.grade, "subject": row.subject, "topic": row.topic, "language": str(row.language), "archetype": str(row.archetype) if row.archetype else None, "feedback_score": row.feedback_score, "served_from_cache": row.served_from_cache, "created_at": _iso(row.created_at)}
                for row in lessons
            ],
            "knowledge_gaps": [
                {"id": row.id, "grade": row.grade, "subject": row.subject, "topic": row.topic, "severity": row.severity, "resolved": row.resolved, "created_at": _iso(row.created_at)}
                for row in gaps
            ],
            "parental_consents": [
                {"id": row.id, "policy_version": row.policy_version, "granted_at": _iso(row.granted_at), "expires_at": _iso(row.expires_at), "revoked_at": _iso(row.revoked_at), "is_active": row.is_active}
                for row in consents
            ],
        }

    def _to_csv(self, payload: dict[str, Any]) -> str:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["section", "field", "value"])
        for key, value in payload.get("learner", {}).items():
            writer.writerow(["learner", key, value])
        for section in ("diagnostic_sessions", "lessons", "knowledge_gaps", "parental_consents"):
            for row in payload.get(section, []):
                for key, value in row.items():
                    writer.writerow([section, key, value])
        return output.getvalue()

    def _status(
        self,
        request_type: str,
        status_value: Literal["accepted", "completed", "pending_review", "cancelled"],
        learner_id: str,
        sla_days: int,
        audit_event_type: str,
        *,
        requires_admin_review: bool = False,
        reason: str | None = None,
    ) -> RightsRequestStatus:
        requested_at = _now()
        return RightsRequestStatus(
            request_type=request_type,
            status=status_value,
            learner_id=learner_id,
            requested_at=requested_at.isoformat(),
            due_at=(requested_at + timedelta(days=sla_days)).isoformat(),
            audit_event_type=audit_event_type,
            requires_admin_review=requires_admin_review,
            reason=reason,
        )


__all__ = [
    "POPIADataRightsService",
    "POPIA_ERASURE_GRACE_DAYS",
    "POPIA_ERASURE_REVIEW_SLA_DAYS",
    "POPIA_EXPORT_SLA_DAYS",
    "RightsRequestStatus",
]
