import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.modules.jobs import (
    _get_arq_pool,
    generate_lesson_job,
    generate_study_plan_job,
    run_database_backup,
    _send_renewal_email,
)



@pytest.mark.asyncio
async def test_get_arq_pool_branches():
    import app.modules.jobs as jobs_mod
    jobs_mod._ARQ_POOL = None

    mock_pool = MagicMock()
    with patch("arq.connections.create_pool", AsyncMock(return_value=mock_pool)):
        pool1 = await _get_arq_pool()
        assert pool1 == mock_pool

        # Second call returns cached global pool
        pool2 = await _get_arq_pool()
        assert pool2 == mock_pool


@pytest.mark.asyncio
async def test_generate_lesson_job_flow():
    mock_db = AsyncMock()
    mock_db_cm = MagicMock()
    mock_db_cm.__aenter__.return_value = mock_db
    mock_db_cm.__aexit__.return_value = None

    mock_lesson = MagicMock()
    mock_lesson.model_dump.return_value = {"id": "lesson-1", "title": "Fractions"}

    mock_service = MagicMock()
    mock_service.generate_lesson_for_learner = AsyncMock(return_value=(mock_lesson, False, "openai"))

    async def mock_exec_durable(jid, fn):
        return await fn()

    user_id = str(uuid.uuid4())
    with patch("app.core.database.AsyncSessionFactory", return_value=mock_db_cm), \
         patch("app.modules.lessons.service.LessonService", return_value=mock_service), \
         patch("app.modules.jobs._execute_durable_job", side_effect=mock_exec_durable):
        res = await generate_lesson_job(
            learner_id="lrn-1",
            subject="mathematics",
            topic="fractions",
            language="en",
            current_user_id=user_id,
        )
        assert res["lesson"]["title"] == "Fractions"
        assert res["cache_hit"] is False
        assert res["provider"] == "openai"


@pytest.mark.asyncio
async def test_generate_study_plan_job_flow():
    mock_db = AsyncMock()
    mock_db_cm = MagicMock()
    mock_db_cm.__aenter__.return_value = mock_db
    mock_db_cm.__aexit__.return_value = None

    mock_service = MagicMock()
    mock_service.generate_plan = AsyncMock(return_value={"plan_id": "plan-123", "items": []})

    mock_audit = MagicMock()
    mock_audit.log_event = AsyncMock()

    mock_tel = MagicMock()
    mock_tel.track_event_async = AsyncMock()

    async def mock_exec_durable(jid, fn):
        return await fn()

    with patch("app.core.database.AsyncSessionFactory", return_value=mock_db_cm), \
         patch("app.services.study_plan_service_v2.StudyPlanServiceV2", return_value=mock_service), \
         patch("app.services.audit_service.AuditService", return_value=mock_audit), \
         patch("app.services.telemetry.TelemetryService", return_value=mock_tel), \
         patch("app.modules.jobs._execute_durable_job", side_effect=mock_exec_durable):
        plan = await generate_study_plan_job(
            learner_id="lrn-2",
            gap_ratio=0.5,
        )

        assert plan["plan_id"] == "plan-123"
        mock_audit.log_event.assert_awaited_once()
        mock_tel.track_event_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_backup_database_job_encryption_and_chmod():
    mock_cfg = MagicMock(
        BACKUP_ENCRYPTION_KEY="secret-key-123",
        BACKUP_RETENTION_DAYS=7,
    )
    mock_run_res = MagicMock(stdout="Line 1\nLine 2\nDone")

    with patch("app.modules.jobs.get_settings", return_value=mock_cfg), \
         patch("os.access", return_value=False), \
         patch("os.chmod") as mock_chmod, \
         patch("scripts._subprocess.run", return_value=mock_run_res):
        res = await run_database_backup({})
        assert res["status"] == "success"
        mock_chmod.assert_called_once()



@pytest.mark.asyncio
async def test_send_renewal_email_guardian_none():
    mock_cfg = MagicMock(
        SENDGRID_API_KEY="SG.test",
        SENDGRID_FROM_EMAIL="noreply@test.com",
        SENDGRID_FROM_NAME="EduBoost",
    )

    consent = MagicMock(
        guardian_id="g-123",
        expires_at=datetime.now(timezone.utc),
    )

    mock_db = AsyncMock()
    mock_db_cm = MagicMock()
    mock_db_cm.__aenter__.return_value = mock_db
    mock_db_cm.__aexit__.return_value = None

    mock_guardian_repo = MagicMock()
    mock_guardian_repo.get = AsyncMock(return_value=None)

    with patch("app.modules.jobs.get_settings", return_value=mock_cfg), \
         patch("app.modules.jobs.durable_job_session", return_value=mock_db_cm), \
         patch("app.repositories.GuardianRepository", return_value=mock_guardian_repo):
        # Should return early without raising error
        await _send_renewal_email(consent)
        mock_guardian_repo.get.assert_awaited_once()
