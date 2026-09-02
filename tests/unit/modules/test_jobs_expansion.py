import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.jobs import (
    _error_payload,
    _update_durable_job,
    _execute_durable_job,
    send_consent_reminders,
    send_consent_renewal_reminders,
)


def test_error_payload():
    err = ValueError("Invalid argument supplied")
    payload = _error_payload(err)
    assert payload["type"] == "ValueError"
    assert payload["message"] == "Invalid argument supplied"


@pytest.mark.asyncio
async def test_update_durable_job():
    with patch("app.modules.jobs.update_job", new_callable=AsyncMock) as mock_update:
        # None job_id should no-op
        await _update_durable_job(None, status="completed")
        mock_update.assert_not_called()

        # Valid job_id
        await _update_durable_job("job-123", status="running")
        mock_update.assert_called_once_with("job-123", status="running", result=None, error=None)


@pytest.mark.asyncio
async def test_execute_durable_job_success():
    with patch("app.modules.jobs._update_durable_job", new_callable=AsyncMock) as mock_update:
        runner = AsyncMock(return_value={"status": "ok"})
        res = await _execute_durable_job("job-123", runner)

        assert res == {"status": "ok"}
        assert mock_update.call_count == 2
        mock_update.assert_any_call("job-123", status="running")
        mock_update.assert_any_call("job-123", status="completed", result={"status": "ok"})


@pytest.mark.asyncio
async def test_execute_durable_job_failure():
    with patch("app.modules.jobs._update_durable_job", new_callable=AsyncMock) as mock_update:
        runner = AsyncMock(side_effect=RuntimeError("Job failed"))
        with pytest.raises(RuntimeError, match="Job failed"):
            await _execute_durable_job("job-123", runner)

        assert mock_update.call_count == 2
        mock_update.assert_any_call("job-123", status="running")
        # Second call status failed
        call_args = mock_update.call_args_list[1]
        assert call_args.kwargs["status"] == "failed"


@pytest.mark.asyncio
async def test_consent_reminders_jobs():
    with patch("app.modules.jobs.run_consent_reminder_cycle", new_callable=AsyncMock) as mock_cycle, \
         patch("app.modules.jobs._update_durable_job", new_callable=AsyncMock):

        res1 = await send_consent_reminders({}, job_id="job-1")
        assert res1 == {"status": "sent"}
        mock_cycle.assert_called_once()

        res2 = await send_consent_renewal_reminders({}, job_id="job-2")
        assert res2 == {"status": "sent"}


@pytest.mark.asyncio
async def test_get_arq_pool_and_enqueue_durable():
    import app.modules.jobs as jobs_mod

    # Global pool cached
    mock_pool = MagicMock()
    mock_pool.enqueue_job = AsyncMock(return_value=MagicMock())
    jobs_mod._ARQ_POOL = mock_pool

    pool = await jobs_mod._get_arq_pool()
    assert pool == mock_pool

    # Enqueue durable success
    with patch("app.modules.jobs.create_job", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"job_id": "job-100"}
        job_id = await jobs_mod.enqueue_durable("test_func", operation="test_op")
        assert job_id == "job-100"
        mock_pool.enqueue_job.assert_called_once()

    # Enqueue durable rejection
    mock_pool.enqueue_job = AsyncMock(return_value=None)
    with patch("app.modules.jobs.create_job", new_callable=AsyncMock) as mock_create, \
         patch("app.modules.jobs._update_durable_job", new_callable=AsyncMock) as mock_update:
        mock_create.return_value = {"job_id": "job-101"}
        with pytest.raises(RuntimeError, match="ARQ rejected job enqueue"):
            await jobs_mod.enqueue_durable("test_func", operation="test_op")
        mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_process_rlhf_feedback_batch_success_and_failure():
    from app.modules.jobs import process_rlhf_feedback_batch

    # Success
    res = await process_rlhf_feedback_batch({}, "batch-1")
    assert res["batch_id"] == "batch-1"
    assert res["status"] == "exported"

    # Failure
    with patch("app.modules.jobs.logger.info", side_effect=ValueError("Boom")):
        with pytest.raises(ValueError, match="Boom"):
            await process_rlhf_feedback_batch({}, "batch-2")


@pytest.mark.asyncio
async def test_expire_stale_diagnostic_sessions_success_and_failure():
    from app.modules.jobs import expire_stale_diagnostic_sessions

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.rowcount = 3
    mock_db.execute = AsyncMock(return_value=mock_res)
    mock_db.commit = AsyncMock()

    class MockSessionCtx:
        async def __aenter__(self):
            return mock_db
        async def __aexit__(self, *args):
            pass

    with patch("app.modules.jobs.durable_job_session", return_value=MockSessionCtx()):
        res = await expire_stale_diagnostic_sessions({})
        assert res["expired"] == 3

    # Failure path
    with patch("app.modules.jobs.durable_job_session", side_effect=RuntimeError("DB Error")):
        with pytest.raises(RuntimeError, match="DB Error"):
            await expire_stale_diagnostic_sessions({})


@pytest.mark.asyncio
async def test_process_stale_content_reviews():
    from app.modules.jobs import process_stale_content_reviews

    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()

    class MockSessionCtx:
        async def __aenter__(self):
            return mock_db
        async def __aexit__(self, *args):
            pass

    mock_svc = MagicMock()
    mock_svc.process_stale_assignments = AsyncMock(return_value={"stale": 2, "reminded": 1, "escalated": 1})

    with patch("app.modules.jobs.durable_job_session", return_value=MockSessionCtx()), \
         patch("app.services.content_review_governance.ContentReviewGovernanceService", return_value=mock_svc), \
         patch("app.modules.jobs._update_durable_job", new_callable=AsyncMock):

        res = await process_stale_content_reviews({}, job_id="job-stale")
        assert res["stale"] == 2
        assert res["reminded"] == 1


@pytest.mark.asyncio
async def test_run_database_backup_success_and_failure():
    from app.modules.jobs import run_database_backup

    mock_res = MagicMock()
    mock_res.stdout = "line1\nline2\nline3\nline4"

    with patch("scripts._subprocess.run", return_value=mock_res), \
         patch("os.access", return_value=True):
        res = await run_database_backup({})
        assert res["status"] == "success"
        assert len(res["output_tail"]) == 3

    # Failure path
    with patch("scripts._subprocess.run", side_effect=RuntimeError("Script failed")), \
         patch("os.access", return_value=True):
        with pytest.raises(RuntimeError, match="Script failed"):
            await run_database_backup({})


@pytest.mark.asyncio
async def test_send_renewal_email():
    from app.modules.jobs import _send_renewal_email

    consent = MagicMock()
    consent.guardian_id = "g-1"
    consent.expires_at = MagicMock()
    consent.expires_at.strftime = MagicMock(return_value="01 January 2027")

    # 1. Unconfigured SendGrid
    with patch("app.modules.jobs.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(SENDGRID_API_KEY="")
        await _send_renewal_email(consent)

    # 2. Configured SendGrid with guardian found
    mock_guardian = MagicMock()
    mock_guardian.email_encrypted = "encrypted_email"

    mock_repo = MagicMock()
    mock_repo.get = AsyncMock(return_value=mock_guardian)

    mock_db = AsyncMock()
    class MockSessionCtx:
        async def __aenter__(self):
            return mock_db
        async def __aexit__(self, *args):
            pass

    mock_sg_client = MagicMock()

    with patch("app.modules.jobs.get_settings") as mock_settings, \
         patch("app.modules.jobs.durable_job_session", return_value=MockSessionCtx()), \
         patch("app.repositories.GuardianRepository", return_value=mock_repo), \
         patch("app.core.security.decrypt_pii", return_value="parent@example.com"), \
         patch("sendgrid.SendGridAPIClient", return_value=mock_sg_client):

        mock_settings.return_value = MagicMock(
            SENDGRID_API_KEY="SG.test",
            SENDGRID_FROM_EMAIL="no-reply@eduboost.co.za",
            SENDGRID_FROM_NAME="EduBoost",
        )
        await _send_renewal_email(consent)
        mock_sg_client.send.assert_called_once()


@pytest.mark.asyncio
async def test_worker_startup_shutdown_and_settings():
    from app.modules.jobs import startup, shutdown, WorkerSettings

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()

    class MockSessionCtx:
        async def __aenter__(self):
            return mock_db
        async def __aexit__(self, *args):
            pass

    ctx = {"redis": MagicMock(ping=AsyncMock())}
    with patch("app.core.database.AsyncSessionFactory", return_value=MockSessionCtx()):
        await startup(ctx)
        assert ctx["db_session_factory"] is not None

    await shutdown(ctx)

    assert len(WorkerSettings.functions) >= 10
    assert len(WorkerSettings.cron_jobs) >= 5
    assert WorkerSettings.redis_settings is not None
