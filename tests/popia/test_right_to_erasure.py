"""
tests/popia/test_right_to_erasure.py
POPIA §4.3 – right to erasure: end-to-end erasure lifecycle assertions.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone


from app.domain.data_subject_rights import ErasureRequest, RequestStatus


class TestRightToErasure:
    def test_new_erasure_request_is_pending(self):
        req = ErasureRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
        )
        assert req.status == RequestStatus.PENDING

    def test_legal_hold_blocks_execution(self):
        req = ErasureRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            status=RequestStatus.IN_PROGRESS,
            legal_hold=True,
        )
        assert req.can_execute() is False

    def test_approved_without_hold_can_execute(self):
        req = ErasureRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            status=RequestStatus.IN_PROGRESS,
            legal_hold=False,
        )
        assert req.can_execute() is True

    def test_erasure_sla_deadline_set_on_creation(self):
        req = ErasureRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
        )
        assert req.sla_deadline > datetime.now(timezone.utc)

    def test_completed_erasure_has_executed_at(self):
        now = datetime.now(timezone.utc)
        req = ErasureRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            status=RequestStatus.COMPLETED,
            executed_at=now,
        )
        assert req.executed_at == now
