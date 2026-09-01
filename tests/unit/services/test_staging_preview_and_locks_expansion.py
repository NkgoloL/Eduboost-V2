"""Comprehensive unit tests for Content Generation Run Lock, Staging Preview, and Consent Renewal."""
from __future__ import annotations

import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.content_generation_run_lock import (
    ContentGenerationRunLock,
    LockAcquisitionResult,
    DEFAULT_LOCK_TTL_MINUTES,
)
from app.services.content_staging_preview_service import (
    StagingArtifactPreview,
    StagingPreviewReport,
    ContentStagingPreviewService,
)
from app.services.consent_renewal_service import (
    ConsentRenewalService,
    SendGridEmailGateway,
)


# ---------------------------------------------------------------------------
# Content Generation Run Lock Tests
# ---------------------------------------------------------------------------

class TestContentGenerationRunLock:
    def test_lock_init_default_ttl(self):
        lock = ContentGenerationRunLock()
        assert lock.ttl_minutes == DEFAULT_LOCK_TTL_MINUTES
        assert lock.ttl_seconds == DEFAULT_LOCK_TTL_MINUTES * 60

    def test_lock_init_custom_ttl(self):
        lock = ContentGenerationRunLock(ttl_minutes=45)
        assert lock.ttl_minutes == 45
        assert lock.ttl_seconds == 2700

    def test_lock_acquisition_result_dataclass(self):
        res = LockAcquisitionResult(
            acquired=True,
            lock_holder="worker-node-1",
            lock_acquired_at="2026-08-28T00:00:00Z",
            lock_expires_at="2026-08-28T03:00:00Z",
        )
        assert res.acquired is True
        assert res.lock_holder == "worker-node-1"

    @pytest.mark.asyncio
    async def test_acquire_and_release_flows(self):
        lock = ContentGenerationRunLock(ttl_minutes=60)
        session = AsyncMock()
        now = time.time()

        # 1. Existing active lock held by someone else
        active_run = MagicMock()
        active_run.run_metadata = {
            "full_generation_lock": {
                "holder": "other_worker",
                "lock_acquired_at": now,
                "lock_expires_at": now + 3600,
            }
        }
        mock_active_res = MagicMock()
        mock_active_res.scalar_one_or_none.return_value = active_run
        session.execute.return_value = mock_active_res

        res_blocked = await lock.acquire(session, holder="my_worker")
        assert res_blocked.acquired is False
        assert res_blocked.error == "Lock already held"

        # 2. Acquire when latest_run exists with stale lock
        stale_run = MagicMock()
        stale_run.run_metadata = {
            "full_generation_lock": {
                "holder": "stale_worker",
                "lock_acquired_at": now - 7200,
                "lock_expires_at": now - 3600,
            }
        }
        mock_stale_res = MagicMock()
        mock_stale_res.scalar_one_or_none.return_value = stale_run
        session.execute.return_value = mock_stale_res

        res_acquired = await lock.acquire(session, holder="my_worker")
        assert res_acquired.acquired is True
        assert res_acquired.lock_holder == "my_worker"
        assert stale_run.run_metadata["full_generation_lock"]["holder"] == "my_worker"

        # 3. Release lock matching holder
        mock_release_res = MagicMock()
        mock_release_res.scalar_one_or_none.return_value = stale_run
        session.execute.return_value = mock_release_res

        released = await lock.release(session, holder="my_worker")
        assert released is True
        assert stale_run.run_metadata["full_generation_lock"]["holder"] is None

        # 4. Release lock wrong holder
        released_wrong = await lock.release(session, holder="wrong_worker")
        assert released_wrong is False

        # 5. Acquire when no run exists (creates placeholder)
        mock_empty_res = MagicMock()
        mock_empty_res.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_empty_res

        res_placeholder = await lock.acquire(session, holder="my_worker")
        assert res_placeholder.acquired is True
        session.add.assert_called()


# ---------------------------------------------------------------------------
# Staging Preview Dataclass & Service Tests
# ---------------------------------------------------------------------------

class TestStagingPreview:
    def test_staging_artifact_preview_dataclass(self):
        preview = StagingArtifactPreview(
            artifact_id=str(uuid.uuid4()),
            scope_id="caps-math-g4",
            caps_ref="4.M.1.1",
            layer="lesson_plan",
            artifact_type="lesson",
            staging_status="staged",
            learner_visible=False,
            seed_run_id=str(uuid.uuid4()),
            seed_run_status="completed",
            verification_passed=True,
            payload={"title": "Math Grade 4"},
            source_artifact_hash="sha256:12345",
            created_at="2026-08-28T00:00:00Z",
        )
        assert preview.scope_id == "caps-math-g4"
        assert preview.learner_visible is False

    def test_staging_preview_report_dataclass(self):
        report = StagingPreviewReport(
            scope_id="caps-math-g4",
            layers=["lesson_plan", "assessment"],
            total_artifacts_count=25,
            active_artifacts_count=20,
            pending_artifacts_count=5,
            learner_visible_count=0,
            artifacts=[],
        )
        assert report.total_artifacts_count == 25
        assert report.learner_visible_count == 0

    def test_staging_preview_service_init(self):
        service = ContentStagingPreviewService()
        assert service is not None


# ---------------------------------------------------------------------------
# Consent Renewal Service Tests
# ---------------------------------------------------------------------------

class TestConsentRenewalService:
    def test_consent_renewal_service_init(self):
        mock_db = AsyncMock()
        mock_email = AsyncMock()
        mock_settings = MagicMock()
        service = ConsentRenewalService(db=mock_db, email_gateway=mock_email, settings=mock_settings)
        assert service._db == mock_db
        assert service._email_gateway == mock_email

    def test_sendgrid_email_gateway_init(self):
        mock_settings = MagicMock()
        mock_settings.SENDGRID_API_KEY = "SG.fake_key_12345"
        gw = SendGridEmailGateway(settings=mock_settings)
        assert gw._settings.SENDGRID_API_KEY == "SG.fake_key_12345"
