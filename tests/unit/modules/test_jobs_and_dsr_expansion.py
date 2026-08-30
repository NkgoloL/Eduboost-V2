"""Comprehensive unit tests for Jobs execution helpers and POPIA DSR service."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.modules.jobs import (
    _error_payload,
    _update_durable_job,
    _execute_durable_job,
)
from app.services.popia_dsr_service import (
    POPIADSRService,
    DSRServiceError,
)


# ---------------------------------------------------------------------------
# ARQ / Durable Jobs Execution Helper Tests
# ---------------------------------------------------------------------------

class TestJobsExecutionHelpers:
    def test_error_payload_formatter(self):
        exc = ValueError("Invalid job argument passed")
        payload = _error_payload(exc)
        assert payload["type"] == "ValueError"
        assert payload["message"] == "Invalid job argument passed"

    @pytest.mark.asyncio
    async def test_update_durable_job_none_id(self):
        # Should cleanly no-op when job_id is None
        await _update_durable_job(None, status="running")

    @pytest.mark.asyncio
    async def test_execute_durable_job_success(self):
        with patch("app.modules.jobs.update_job", new_callable=AsyncMock) as mock_update:
            async def dummy_runner():
                return {"status": "success", "processed": 10}

            res = await _execute_durable_job("job_123", dummy_runner)
            assert res == {"status": "success", "processed": 10}
            assert mock_update.call_count >= 2

    @pytest.mark.asyncio
    async def test_execute_durable_job_failure(self):
        with patch("app.modules.jobs.update_job", new_callable=AsyncMock) as mock_update:
            async def failing_runner():
                raise RuntimeError("Worker process crashed")

            with pytest.raises(RuntimeError, match="Worker process crashed"):
                await _execute_durable_job("job_456", failing_runner)
            assert mock_update.call_count >= 2


# ---------------------------------------------------------------------------
# POPIA DSR Service Tests
# ---------------------------------------------------------------------------

class TestPOPIADSRService:
    def test_dsr_service_init(self):
        mock_db = AsyncMock()
        service = POPIADSRService(db=mock_db)
        assert service.db == mock_db

    @pytest.mark.asyncio
    async def test_initiate_erasure_learner_not_found(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = POPIADSRService(db=mock_db)
        with pytest.raises(DSRServiceError, match="not found"):
            await service.initiate_erasure_request(
                learner_id=str(uuid.uuid4()),
                requester_id="guardian_1",
                requester_role="parent",
            )
