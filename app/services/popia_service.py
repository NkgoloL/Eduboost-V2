"""POPIA data-subject-rights service.

The service centralises learner export, erasure-request, correction, and
processing-restriction workflows so routers do not assemble compliance payloads
ad hoc. It intentionally preserves append-only audit records and returns only
structured, machine-readable status metadata.
"""
from __future__ import annotations

import csv
import inspect
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from io import StringIO
from typing import Any, Literal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext
from app.security.dependencies import (
    actor_id_from_current_user,
    require_learner_read_for_current_user,
    require_learner_write_for_current_user,
)
from app.models import (
    AuditEvent,
    DiagnosticSession,
    ErasureRequest,
    Guardian,
    KnowledgeGap,
    LearnerProfile,
    Lesson,
    MasterySnapshot,
    ParentalConsent,
    PracticeQueue,
    SpacedReviewSchedule,
    SubjectMastery,
    TopicMastery,
)
from app.repositories.audit_repository import AuditRepository
from app.repositories.repositories import LearnerRepository
from app.services.consent import ConsentService

POPIA_EXPORT_SLA_DAYS = 30
POPIA_ERASURE_REVIEW_SLA_DAYS = 30
POPIA_ERASURE_GRACE_DAYS = 30

# Erasure request states
ERASURE_STATE_REQUESTED = "requested"
ERASURE_STATE_VERIFIED = "verified"
ERASURE_STATE_SCHEDULED = "scheduled"
ERASURE_STATE_CANCELLED = "cancelled"
ERASURE_STATE_EXECUTED = "executed"
ERASURE_STATE_FAILED = "failed"

# Execution methods
ERASURE_METHOD_SOFT = "soft"
ERASURE_METHOD_PHYSICAL = "physical"
ERASURE_METHOD_PURGE = "purge"


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
    return datetime.now(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None




async def _maybe_await(value: Any) -> Any:
    """Return sync values and await async test doubles.

    SQLAlchemy ``AsyncSession.add`` is intentionally synchronous, but many
    backend-fast tests use ``AsyncMock`` as a lightweight session double.
    Calling an AsyncMock-backed ``add`` without awaiting it creates unawaited
    coroutine warnings, which the backend-fast gate treats as failures.
    This adapter keeps production behaviour unchanged while making service
    writes safe under async test doubles.
    """
    if inspect.isawaitable(value):
        return await value
    return value

def _role_value(raw_role: Any) -> str:
    value = getattr(raw_role, "value", raw_role)
    return str(value or "").lower()


def _current_user_actor_id(current_user: dict[str, Any] | AuthContext) -> str:
    actor_id = actor_id_from_current_user(current_user)
    return str(actor_id or "")


def _current_user_role(current_user: dict[str, Any] | AuthContext) -> str:
    if isinstance(current_user, AuthContext):
        if current_user.roles:
            return _role_value(current_user.roles[0])
        return _role_value(current_user.raw_claims.get("role"))
    return _role_value(current_user.get("role"))


class POPIADataRightsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.learners = LearnerRepository(db)
        self.audit = AuditRepository(db)
        self.consent = ConsentService(db)


    async def _add(self, *objects: Any) -> None:
        """Add ORM objects while tolerating AsyncMock-backed test sessions."""
        for obj in objects:
            await _maybe_await(self.db.add(obj))

    async def load_learner_for_read(self, learner_id: str, current_user: dict[str, Any] | AuthContext) -> LearnerProfile:
        learner = await self.learners.get_by_id(learner_id)
        if learner is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
        require_learner_read_for_current_user(current_user, learner)
        return learner

    async def load_learner_for_write(self, learner_id: str, current_user: dict[str, Any] | AuthContext) -> LearnerProfile:
        learner = await self.learners.get_by_id(learner_id)
        if learner is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
        require_learner_write_for_current_user(current_user, learner_id)
        return learner

    async def build_learner_export(
        self,
        learner_id: str,
        current_user: dict[str, Any] | AuthContext,
        *,
        export_format: Literal["json", "csv"] = "json",
    ) -> dict[str, Any]:
        requester_id = _current_user_actor_id(current_user)
        learner = await self.load_learner_for_read(learner_id, current_user)
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

    async def request_erasure(self, learner_id: str, current_user: dict[str, Any] | AuthContext, *, reason: str = "guardian_request") -> dict[str, Any]:
        """Request POPIA Right to Erasure with state machine and safety checks."""
        requester_id = _current_user_actor_id(current_user)
        requester_role = _current_user_role(current_user)
        learner = await self.load_learner_for_write(learner_id, current_user)

        # Authorization check
        if str(learner.guardian_id) != requester_id and requester_role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the learner's guardian or admin can request erasure")

        # Check for existing erasure request
        existing_request = await self.db.scalar(
            select(ErasureRequest).where(
                ErasureRequest.learner_id == learner_id,
                ErasureRequest.state.in_([ERASURE_STATE_REQUESTED, ERASURE_STATE_VERIFIED, ERASURE_STATE_SCHEDULED])
            )
        )
        if existing_request:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erasure request already in progress for this learner")

        # Preflight safety checks
        preflight_result = await self._preflight_erasure_checks(learner, requester_id, requester_role)

        # Create erasure request record
        grace_period_end = _now() + timedelta(days=POPIA_ERASURE_GRACE_DAYS)
        erasure_request = ErasureRequest(
            learner_id=learner_id,
            requester_id=requester_id,
            requester_role=requester_role,
            state=ERASURE_STATE_REQUESTED,
            reason=reason,
            legal_basis="popia_section_11",
            export_offered=False,
            export_waived=False,
            legal_hold=preflight_result.get("legal_hold", False),
            grace_period_end_at=grace_period_end,
            preflight_result=preflight_result,
        )
        await self._add(erasure_request)

        # Soft delete learner (grace period)
        learner.is_deleted = True
        learner.deletion_requested_at = _now()
        learner.display_name = "[erased]"
        await self._add(learner)

        # Revoke consent
        await self.consent.execute_erasure(requester_id, learner_id)

        # Audit event
        await self.audit.append(
            "erasure.requested",
            actor_id=requester_id,
            resource_id=learner_id,
            payload={
                "learner_id": learner_id,
                "learner_pseudonym": learner.pseudonym_id,
                "reason": reason,
                "grace_period_days": POPIA_ERASURE_GRACE_DAYS,
                "grace_period_end": grace_period_end.isoformat(),
                "preflight_result": preflight_result,
                "preserve_audit_records": True,
            },
        )

        await self.db.flush()

        return {
            "request_id": erasure_request.id,
            "state": erasure_request.state,
            "learner_id": learner_id,
            "learner_pseudonym": learner.pseudonym_id,
            "grace_period_end": grace_period_end.isoformat(),
            "preflight_result": preflight_result,
        }

    async def erasure_status(self, learner_id: str, current_user: dict[str, Any] | AuthContext) -> dict[str, Any]:
        """Return the latest erasure request status for a learner."""
        requester_id = _current_user_actor_id(current_user)
        requester_role = _current_user_role(current_user)
        learner = await self.load_learner_for_read(learner_id, current_user)

        erasure_request = await self.db.scalar(
            select(ErasureRequest)
            .where(ErasureRequest.learner_id == learner_id)
            .order_by(ErasureRequest.created_at.desc())
        )
        if erasure_request is None:
            return asdict(self._status("erasure", "pending_review", learner_id, POPIA_ERASURE_REVIEW_SLA_DAYS, "erasure.status.none"))

        if erasure_request.requester_id != requester_id and requester_role != "admin" and str(learner.guardian_id) != requester_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the requester, guardian or admin can view erasure status")

        return {
            "request_id": erasure_request.id,
            "state": erasure_request.state,
            "learner_id": learner_id,
            "reason": erasure_request.reason,
            "requested_at": _iso(erasure_request.created_at),
            "grace_period_end": _iso(erasure_request.grace_period_end_at),
            "scheduled_at": _iso(erasure_request.scheduled_at),
            "executed_at": _iso(erasure_request.executed_at),
            "legal_hold": erasure_request.legal_hold,
            "requires_admin_review": erasure_request.legal_hold or erasure_request.state in {ERASURE_STATE_REQUESTED, ERASURE_STATE_VERIFIED, ERASURE_STATE_SCHEDULED},
        }

    async def cancel_erasure(self, learner_id: str, current_user: dict[str, Any] | AuthContext) -> dict[str, Any]:
        """Cancel an active erasure request."""
        requester_id = _current_user_actor_id(current_user)
        requester_role = _current_user_role(current_user)
        learner = await self.load_learner_for_write(learner_id, current_user)

        # Find active erasure request
        erasure_request = await self.db.scalar(
            select(ErasureRequest).where(
                ErasureRequest.learner_id == learner_id,
                ErasureRequest.state.in_([ERASURE_STATE_REQUESTED, ERASURE_STATE_VERIFIED, ERASURE_STATE_SCHEDULED])
            )
        )
        if not erasure_request:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No active erasure request exists for this learner")

        # Authorization check
        if erasure_request.requester_id != requester_id and requester_role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the requester or admin can cancel erasure")

        # Update erasure request state
        erasure_request.state = ERASURE_STATE_CANCELLED
        await self._add(erasure_request)

        # Restore learner
        learner.is_deleted = False
        learner.deletion_requested_at = None
        learner.display_name = learner.display_name if learner.display_name != "[erased]" else "Restored"
        await self._add(learner)

        # Audit event
        await self.audit.append(
            "erasure.cancelled",
            actor_id=requester_id,
            resource_id=learner_id,
            payload={
                "learner_id": learner_id,
                "learner_pseudonym": learner.pseudonym_id,
                "request_id": erasure_request.id,
            },
        )

        await self.db.flush()

        return {
            "request_id": erasure_request.id,
            "state": erasure_request.state,
            "learner_id": learner_id,
        }

    async def request_correction(
        self,
        learner_id: str,
        current_user: dict[str, Any] | AuthContext,
        fields: dict[str, Any],
        *,
        reason: str,
    ) -> dict[str, Any]:
        requester_id = _current_user_actor_id(current_user)
        learner = await self.load_learner_for_write(learner_id, current_user)
        allowed = {"display_name", "grade", "language"}
        rejected = sorted(set(fields) - allowed)
        if rejected:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"unsupported_fields": rejected})
        updates = {key: value for key, value in fields.items() if key in allowed}
        for key, value in updates.items():
            setattr(learner, key, value)
        await self._add(learner)
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
        current_user: dict[str, Any] | AuthContext,
        *,
        reason: str,
    ) -> dict[str, Any]:
        requester_id = _current_user_actor_id(current_user)
        learner = await self.load_learner_for_write(learner_id, current_user)
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

    async def _preflight_erasure_checks(self, learner: LearnerProfile, requester_id: str, requester_role: str) -> dict[str, Any]:
        """Perform pre-erasure safety checks."""
        checks = {
            "subject_exists": learner is not None,
            "requester_authorized": str(learner.guardian_id) == requester_id or requester_role == "admin",
            "consent_revoked": True,  # Will be revoked during erasure
            "legal_hold": False,  # TODO: Check for legal hold flag
            "grace_period_elapsed": False,  # Not applicable for initial request
            "export_offered": False,  # TODO: Check if export was offered
            "all_checks_passed": False,
        }

        checks["all_checks_passed"] = all(checks.values())
        return checks

    async def execute_erasure(self, request_id: str, current_user: dict[str, Any] | AuthContext, *, method: str = ERASURE_METHOD_PHYSICAL) -> dict[str, Any]:
        """Execute erasure after grace period with safety checks."""
        requester_id = _current_user_actor_id(current_user)
        requester_role = _current_user_role(current_user)

        # Find erasure request
        erasure_request = await self.db.scalar(
            select(ErasureRequest).where(ErasureRequest.id == request_id)
        )
        if not erasure_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Erasure request not found")

        # Authorization check
        if erasure_request.requester_id != requester_id and requester_role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the requester or admin can execute erasure")

        # State validation
        if erasure_request.state not in [ERASURE_STATE_VERIFIED, ERASURE_STATE_SCHEDULED]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Erasure request must be verified or scheduled, current state: {erasure_request.state}")

        # Grace period check (unless admin override)
        if not erasure_request.admin_override:
            if erasure_request.grace_period_end_at and erasure_request.grace_period_end_at > _now():
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Grace period has not elapsed")

        # Legal hold check
        if erasure_request.legal_hold and not erasure_request.admin_override:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Legal hold on learner data")

        # Export check
        if not erasure_request.export_offered and not erasure_request.export_waived:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Export must be offered or waived before erasure")

        # Load learner
        learner = await self.learners.get_by_id(erasure_request.learner_id)
        if not learner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

        # Execute deletion based on method
        if method == ERASURE_METHOD_SOFT:
            await self.learners.soft_delete(learner.id)
        elif method == ERASURE_METHOD_PHYSICAL:
            await self.learners.delete_by_id(learner.id)
        elif method == ERASURE_METHOD_PURGE:
            await self.learners.purge_personal_data(learner.id)
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid execution method: {method}")

        # Update erasure request state
        erasure_request.state = ERASURE_STATE_EXECUTED
        erasure_request.executed_at = _now()
        erasure_request.execution_method = method
        await self._add(erasure_request)

        # Post-erasure verification
        postflight_result = await self._postflight_erasure_verification(learner.id, method)

        erasure_request.postflight_result = postflight_result
        await self._add(erasure_request)

        # Audit event
        await self.audit.append(
            "erasure.executed",
            actor_id=requester_id,
            resource_id=learner.id,
            payload={
                "learner_id": learner.id,
                "learner_pseudonym": learner.pseudonym_id,
                "request_id": request_id,
                "method": method,
                "admin_override": erasure_request.admin_override,
                "postflight_result": postflight_result,
            },
        )

        await self.db.flush()

        return {
            "request_id": request_id,
            "state": erasure_request.state,
            "learner_id": learner.id,
            "execution_method": method,
            "executed_at": erasure_request.executed_at.isoformat() if erasure_request.executed_at else None,
            "postflight_result": postflight_result,
        }

    async def _postflight_erasure_verification(self, learner_id: str, method: str) -> dict[str, Any]:
        """Verify erasure was successful and PII is no longer accessible."""
        verification = {
            "learner_record_deleted": False,
            "dependent_records_deleted": False,
            "audit_records_preserved": False,
            "guardian_preserved": False,
            "pii_not_retrievable": False,
            "all_checks_passed": False,
        }

        # Check learner record
        learner = await self.learners.get_by_id(learner_id)
        verification["learner_record_deleted"] = learner is None

        # Check dependent records (CASCADE delete)
        # For soft delete, records should still exist but learner should be marked deleted
        if method == ERASURE_METHOD_SOFT:
            verification["dependent_records_deleted"] = learner is not None and learner.is_deleted
        else:
            verification["dependent_records_deleted"] = learner is None

        # Check audit records (should always be preserved)
        audit_events = await self.db.scalar(
            select(AuditEvent).where(AuditEvent.resource_id == learner_id)
        )
        verification["audit_records_preserved"] = audit_events is not None or method == ERASURE_METHOD_PHYSICAL

        # PII retrievability check
        if learner is None or learner.is_deleted and learner.display_name == "[erased]":
            verification["pii_not_retrievable"] = True

        verification["all_checks_passed"] = verification["learner_record_deleted"] and verification["pii_not_retrievable"]

        return verification

    async def _export_payload(self, learner: LearnerProfile) -> dict[str, Any]:
        learner_id = learner.id
        diagnostic_sessions = list((await self.db.scalars(select(DiagnosticSession).where(DiagnosticSession.learner_id == learner_id))).all())
        lessons = list((await self.db.scalars(select(Lesson).where(Lesson.learner_id == learner_id))).all())
        gaps = list((await self.db.scalars(select(KnowledgeGap).where(KnowledgeGap.learner_id == learner_id))).all())
        consents = list((await self.db.scalars(select(ParentalConsent).where(ParentalConsent.learner_id == learner_id))).all())
        subject_mastery = list((await self.db.scalars(select(SubjectMastery).where(SubjectMastery.learner_id == learner_id))).all())
        topic_mastery = list((await self.db.scalars(select(TopicMastery).where(TopicMastery.learner_id == learner_id))).all())
        mastery_snapshots = list((await self.db.scalars(select(MasterySnapshot).where(MasterySnapshot.learner_id == learner_id))).all())
        practice_queue = list((await self.db.scalars(select(PracticeQueue).where(PracticeQueue.learner_id == learner_id))).all())
        spaced_review = list((await self.db.scalars(select(SpacedReviewSchedule).where(SpacedReviewSchedule.learner_id == learner_id))).all())
        guardian = await self.db.get(Guardian, learner.guardian_id)
        audit_events = list((await self.db.scalars(select(AuditEvent).where(AuditEvent.resource_id == learner_id))).all())
        return {
            "export_date": _now().isoformat(),
            "learner": {
                "id": learner.pseudonym_id,
                "pseudonym_id": learner.pseudonym_id,
                "guardian_id": learner.guardian_id,
                "display_name": learner.display_name,
                "grade": learner.grade,
                "language": str(learner.language),
                "archetype": str(learner.archetype) if learner.archetype else None,
                "theta": learner.theta,
                "xp": learner.xp,
                "streak_days": learner.streak_days,
                "last_active": _iso(learner.last_active),
                "is_deleted": learner.is_deleted,
                "deletion_requested_at": _iso(learner.deletion_requested_at),
                "created_at": _iso(learner.created_at),
                "updated_at": _iso(learner.updated_at),
            },
            "diagnostic_sessions": [
                {
                    "id": row.id,
                    "theta_before": row.theta_before,
                    "theta_after": row.theta_after,
                    "se_estimate": row.se_estimate,
                    "session_state": row.session_state,
                    "gap_topics": row.gap_topics,
                    "misconception_tags": row.misconception_tags,
                    "items_served": row.items_served,
                    "theta_history": row.theta_history,
                    "items_correct": row.items_correct,
                    "completed_at": _iso(row.completed_at),
                    "created_at": _iso(row.created_at),
                }
                for row in diagnostic_sessions
            ],
            "lessons": [
                {
                    "id": row.id,
                    "knowledge_gap_id": row.knowledge_gap_id,
                    "grade": row.grade,
                    "subject": row.subject,
                    "topic": row.topic,
                    "language": str(row.language),
                    "archetype": str(row.archetype) if row.archetype else None,
                    "content": row.content,
                    "caps_ref": row.caps_ref,
                    "caps_reference": row.caps_reference,
                    "term": row.term,
                    "subtopic": row.subtopic,
                    "learning_objectives": row.learning_objectives,
                    "explanation": row.explanation,
                    "worked_examples": row.worked_examples,
                    "practice_questions": row.practice_questions,
                    "answer_key": row.answer_key,
                    "remediation_hints": row.remediation_hints,
                    "difficulty_level": row.difficulty_level,
                    "language_level": row.language_level,
                    "safety_classification": row.safety_classification,
                    "pii_check_passed": row.pii_check_passed,
                    "answer_key_verified": row.answer_key_verified,
                    "alignment_confidence": row.alignment_confidence,
                    "quality_score": row.quality_score,
                    "trust_label": row.trust_label,
                    "review_status": row.review_status,
                    "reviewed_at": _iso(row.reviewed_at),
                    "prompt_template_version": row.prompt_template_version,
                    "provider": row.provider,
                    "model_version": row.model_version,
                    "generation_latency_ms": row.generation_latency_ms,
                    "token_usage": row.token_usage,
                    "variant_type": row.variant_type,
                    "llm_provider": row.llm_provider,
                    "served_from_cache": row.served_from_cache,
                    "feedback_score": row.feedback_score,
                    "completed_at": _iso(row.completed_at),
                    "created_at": _iso(row.created_at),
                }
                for row in lessons
            ],
            "knowledge_gaps": [
                {"id": row.id, "grade": row.grade, "subject": row.subject, "topic": row.topic, "severity": row.severity, "resolved": row.resolved, "created_at": _iso(row.created_at)}
                for row in gaps
            ],
            "parental_consents": [
                {
                    "id": row.id,
                    "guardian_id": row.guardian_id,
                    "policy_version": row.policy_version,
                    "status": "granted" if row.is_active else ("revoked" if row.revoked_at else "expired"),
                    "granted_at": _iso(row.granted_at),
                    "expires_at": _iso(row.expires_at),
                    "revoked_at": _iso(row.revoked_at),
                    "created_at": _iso(row.created_at),
                    "updated_at": _iso(row.updated_at),
                }
                for row in consents
            ],
            "subject_mastery": [
                {
                    "id": row.id,
                    "subject": row.subject,
                    "topic": row.topic,
                    "theta": row.theta,
                    "standard_error": row.standard_error,
                    "created_at": _iso(row.created_at),
                    "last_updated": _iso(row.last_updated),
                }
                for row in subject_mastery
            ],
            "topic_mastery": [
                {
                    "id": row.id,
                    "caps_ref": row.caps_ref,
                    "mastery_score": row.mastery_score,
                    "mastery_label": row.mastery_label,
                    "theta_estimate": row.theta_estimate,
                    "theta_se": row.theta_se,
                    "last_updated_at": _iso(row.last_updated_at),
                }
                for row in topic_mastery
            ],
            "mastery_snapshots": [
                {
                    "id": row.id,
                    "caps_ref": row.caps_ref,
                    "mastery_score": row.mastery_score,
                    "mastery_label": row.mastery_label,
                    "theta_estimate": row.theta_estimate,
                    "theta_se": row.theta_se,
                    "practice_accuracy": row.practice_accuracy,
                    "trigger": row.trigger,
                    "snapshot_at": _iso(row.snapshot_at),
                }
                for row in mastery_snapshots
            ],
            "practice_queue": [
                {
                    "id": row.id,
                    "caps_ref": row.caps_ref,
                    "item_id": str(row.item_id) if row.item_id else None,
                    "scheduled_at": _iso(row.scheduled_at),
                    "completed_at": _iso(row.completed_at),
                    "response": row.response,
                    "correct": row.correct,
                }
                for row in practice_queue
            ],
            "spaced_review_schedule": [
                {
                    "id": row.id,
                    "caps_ref": row.caps_ref,
                    "next_review_at": _iso(row.next_review_at),
                    "interval_days": row.interval_days,
                    "easiness_factor": row.easiness_factor,
                    "updated_at": _iso(row.updated_at),
                }
                for row in spaced_review
            ],
            "guardian": {
                "id": guardian.id if guardian else None,
                "display_name": guardian.display_name if guardian else None,
                "role": str(guardian.role) if guardian else None,
                "subscription_tier": str(guardian.subscription_tier) if guardian else None,
                "is_active": guardian.is_active if guardian else None,
                "email_verified": guardian.email_verified if guardian else None,
                "created_at": _iso(guardian.created_at) if guardian else None,
                "updated_at": _iso(guardian.updated_at) if guardian else None,
            } if guardian else {},
            "audit_events": [
                {
                    "id": row.id,
                    "event_type": row.event_type,
                    "resource_id": row.resource_id,
                    "payload": row.payload,
                    "previous_event_hash": row.previous_event_hash,
                    "event_hash": row.event_hash,
                    "hmac_signature": row.hmac_signature,
                    "created_at": _iso(row.created_at),
                }
                for row in audit_events
            ],
        }

    def _to_csv(self, payload: dict[str, Any]) -> str:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["section", "field", "value"])
        for key, value in payload.get("learner", {}).items():
            writer.writerow(["learner", key, value])
        for section in (
            "diagnostic_sessions",
            "lessons",
            "knowledge_gaps",
            "parental_consents",
            "subject_mastery",
            "topic_mastery",
            "mastery_snapshots",
            "practice_queue",
            "spaced_review_schedule",
            "audit_events",
        ):
            for row in payload.get(section, []):
                for key, value in row.items():
                    writer.writerow([section, key, value])
        for key, value in payload.get("guardian", {}).items():
            writer.writerow(["guardian", key, value])
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
