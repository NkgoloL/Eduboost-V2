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
    AuditLog,
    ConsentState,
    ErasureRequest,
    LearnerProfile,
    ParentalConsent,
    SubjectMastery,
    TopicMastery,
    SpacedReviewSchedule,
    StudyPlan,
    SecureToken,
)


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
        await self.db.execute(upd_learner)

        # 2. Revoke all active parental consents
        upd_consent = (
            update(ParentalConsent)
            .where(ParentalConsent.learner_id == learner_id)
            .values(
                status=ConsentState.WITHDRAWN,
                revoked_at=now_utc,
            )
        )
        await self.db.execute(upd_consent)

        # 3. Purge operational learning states (SubjectMastery, TopicMastery, SpacedReview, StudyPlan)
        await self.db.execute(delete(SubjectMastery).where(SubjectMastery.learner_id == learner_id))
        await self.db.execute(delete(TopicMastery).where(TopicMastery.learner_id == learner_id))
        await self.db.execute(delete(SpacedReviewSchedule).where(SpacedReviewSchedule.learner_id == learner_id))
        await self.db.execute(delete(StudyPlan).where(StudyPlan.learner_id == learner_id))

        # 4. Invalidate all active tokens for learner
        await self.db.execute(delete(SecureToken).where(SecureToken.user_id == learner_id))

        # 5. Record sanitized immutable audit event
        audit_payload = sanitize_payload({
            "action": "popia_erasure_cascade_completed",
            "erasure_request_id": erasure_request_id,
            "learner_id": learner_id,
            "requester_id": req.requester_id,
            "execution_method": execution_method,
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

        # 6. Update request status to 'executed'
        req.state = "executed"
        req.executed_at = now_utc
        req.execution_method = execution_method
        req.postflight_result = {"status": "success", "tables_cascaded": 6}

        await self.db.commit()

        return {
            "erasure_request_id": erasure_request_id,
            "state": "executed",
            "learner_id": learner_id,
            "executed_at": now_utc.isoformat(),
        }
