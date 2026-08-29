"""POPIA Data Subject Rights (DSR) Domain Service (TSR-8).

Provides transactional orchestration for:
- Data Export Request generation
- Data Rectification / Correction
- Processing Restriction
- Right to Erasure cascade across primary, derived, and session stores.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pii_sanitizer import sanitize_payload
from app.models import (
    AssessmentAttempt,
    AuditLog,
    ConsentState,
    DiagnosticSession,
    ErasureRequest,
    KnowledgeGap,
    LearnerProfile,
    Lesson,
    MasterySnapshot,
    ParentalConsent,
    PracticeQueue,
    PracticeSession,
    SecureToken,
    SpacedReviewSchedule,
    StudyPlan,
    SubjectMastery,
    TopicMastery,
)

try:
    from app.models.tutor import TutorSession
except ImportError:  # pragma: no cover
    TutorSession = None

try:
    from app.models.runtime_kg import LearnerKGNodeState
except ImportError:  # pragma: no cover
    LearnerKGNodeState = None

try:
    from app.models.item_exposure import ItemExposure
except ImportError:  # pragma: no cover
    ItemExposure = None


class DSRServiceError(RuntimeError):
    pass


class POPIADSRService:
    """Orchestrates compliant POPIA Data Subject Rights workflows."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def initiate_erasure_request(
        self,
        learner_id: str,
        requester_id: str,
        requester_role: str,
        reason: Optional[str] = None,
        legal_basis: Optional[str] = "POPIA Section 24 / Consent Revocation",
    ) -> ErasureRequest:
        """Create and stage a new Right to Erasure request."""
        # 1. Verify learner existence
        stmt = select(LearnerProfile).where(LearnerProfile.id == learner_id)
        res = await self.db.execute(stmt)
        learner = res.scalar_one_or_none()
        if not learner:
            raise DSRServiceError(f"Learner {learner_id} not found.")

        # 2. Instantiate erasure request in 'requested' state
        req = ErasureRequest(
            id=str(uuid4()),
            learner_id=learner_id,
            requester_id=requester_id,
            requester_role=requester_role,
            state="requested",
            reason=reason,
            legal_basis=legal_basis,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(req)
        await self.db.flush()
        return req

    async def execute_erasure_cascade(
        self,
        erasure_request_id: str,
        execution_method: str = "soft_and_purge",
    ) -> dict[str, Any]:
        """Execute transactional cascade across relational, derived, and session data."""
        stmt = select(ErasureRequest).where(ErasureRequest.id == erasure_request_id)
        res = await self.db.execute(stmt)
        req = res.scalar_one_or_none()
        if not req:
            raise DSRServiceError(f"Erasure request {erasure_request_id} not found.")

        learner_id = req.learner_id
        now_utc = datetime.now(timezone.utc)

        tables_affected: list[str] = []
        details: dict[str, int] = {}
        total_rows_purged = 0

        try:
            # 1. Soft-delete and pseudonymize primary LearnerProfile
            upd_learner = (
                update(LearnerProfile)
                .where(LearnerProfile.id == learner_id)
                .values(
                    is_deleted=True,
                    deletion_requested_at=now_utc,
                    display_name=f"[ERASED_LEARNER_{learner_id[:8]}]",
                )
            )
            res_learner = await self.db.execute(upd_learner)
            l_count = res_learner.rowcount if res_learner.rowcount is not None and res_learner.rowcount >= 0 else 1
            tables_affected.append("learner_profiles")
            details["learner_profiles"] = l_count

            # 2. Revoke all active parental consents
            upd_consent = (
                update(ParentalConsent)
                .where(ParentalConsent.learner_id == learner_id)
                .values(
                    status=ConsentState.WITHDRAWN,
                    revoked_at=now_utc,
                )
            )
            res_consent = await self.db.execute(upd_consent)
            c_count = res_consent.rowcount if res_consent.rowcount is not None and res_consent.rowcount >= 0 else 0
            tables_affected.append("parental_consents")
            details["parental_consents"] = c_count

            # 3. Purge operational learning and assessment states
            purge_models: list[Any] = [
                SubjectMastery,
                TopicMastery,
                MasterySnapshot,
                SpacedReviewSchedule,
                StudyPlan,
                PracticeQueue,
                PracticeSession,
                DiagnosticSession,
                KnowledgeGap,
                Lesson,
                AssessmentAttempt,
            ]
            if TutorSession is not None:
                purge_models.append(TutorSession)
            if LearnerKGNodeState is not None:
                purge_models.append(LearnerKGNodeState)
            if ItemExposure is not None:
                purge_models.append(ItemExposure)


            for model in purge_models:
                del_stmt = delete(model).where(model.learner_id == learner_id)
                res_del = await self.db.execute(del_stmt)
                count = res_del.rowcount if res_del.rowcount is not None and res_del.rowcount >= 0 else 0
                tables_affected.append(model.__tablename__)
                details[model.__tablename__] = count
                total_rows_purged += count


            # 5. Invalidate all active tokens for learner
            del_token = delete(SecureToken).where(SecureToken.user_id == learner_id)
            res_token = await self.db.execute(del_token)
            t_count = res_token.rowcount if res_token.rowcount is not None and res_token.rowcount >= 0 else 0
            tables_affected.append("secure_tokens")
            details["secure_tokens"] = t_count
            total_rows_purged += t_count

            # 6. Record sanitized immutable audit event
            audit_payload = sanitize_payload({
                "action": "popia_erasure_cascade_completed",
                "erasure_request_id": erasure_request_id,
                "learner_id": learner_id,
                "requester_id": req.requester_id,
                "execution_method": execution_method,
                "tables_cascaded": len(tables_affected),
                "total_rows_purged": total_rows_purged,
                "completed_at": now_utc.isoformat(),
            })

            audit_entry = AuditLog(
                id=str(uuid4()),
                event_type="popia_erasure_completed",
                actor_id=req.requester_id,
                learner_pseudonym=f"pseudonym_{learner_id[:8]}",
                payload=audit_payload,
                constitutional_outcome="APPROVED",
                created_at=now_utc,
            )
            self.db.add(audit_entry)

            # 7. Update request status to 'executed' with measured outcomes
            req.state = "executed"
            req.executed_at = now_utc
            req.execution_method = execution_method
            req.postflight_result = {
                "status": "success",
                "tables_cascaded": len(tables_affected),
                "tables": tables_affected,
                "records_purged": total_rows_purged,
                "details": details,
            }

            await self.db.commit()

            return {
                "erasure_request_id": erasure_request_id,
                "state": "executed",
                "learner_id": learner_id,
                "tables_cascaded": len(tables_affected),
                "records_purged": total_rows_purged,
                "executed_at": now_utc.isoformat(),
            }
        except Exception as exc:
            await self.db.rollback()
            try:
                stmt_fail = select(ErasureRequest).where(ErasureRequest.id == erasure_request_id)
                res_fail = await self.db.execute(stmt_fail)
                fail_req = res_fail.scalar_one_or_none()
                if fail_req:
                    fail_req.state = "failed"
                    fail_req.postflight_result = {"status": "failed", "error": str(exc)}
                    await self.db.commit()
            except Exception:
                pass
            raise DSRServiceError(f"POPIA erasure cascade failed for request {erasure_request_id}: {exc}") from exc

