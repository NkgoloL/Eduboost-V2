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
