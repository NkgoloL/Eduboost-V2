"""Comprehensive unit tests for ItemBankRepository methods and durable job execution lifecycle."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.repositories.item_bank_repository import ItemBankRepository
from app.modules.jobs import _error_payload, _execute_durable_job


class TestItemBankRepositoryMethods:
    def test_repo_init(self):
        mock_db = AsyncMock()
        repo = ItemBankRepository(db=mock_db)
        assert repo.db == mock_db

    @pytest.mark.asyncio
    async def test_get_item(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_res

        repo = ItemBankRepository(db=mock_db)
        item_id = uuid.uuid4()
        item = await repo.get_item(item_id)
        assert item is not None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_by_caps_ref(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalars.return_value.all.return_value = [MagicMock()]
        mock_db.execute.return_value = mock_res

        repo = ItemBankRepository(db=mock_db)
        items = await repo.list_by_caps_ref("4.M.1.1", limit=10)
        assert len(items) == 1


class TestDurableJobsLifecycle:
    def test_error_payload(self):
        exc = ValueError("Invalid topic code provided")
        payload = _error_payload(exc)
        assert payload["type"] == "ValueError"
        assert payload["message"] == "Invalid topic code provided"

    @pytest.mark.asyncio
    async def test_execute_durable_job_success(self):
        async def mock_runner():
            return {"status": "ok", "items_processed": 5}

        with patch("app.modules.jobs.update_job", new_callable=AsyncMock) as mock_update:
            res = await _execute_durable_job("job-123", mock_runner)
            assert res["items_processed"] == 5
            assert mock_update.call_count == 2
            mock_update.assert_any_call("job-123", status="running", result=None, error=None)
            mock_update.assert_any_call("job-123", status="completed", result={"status": "ok", "items_processed": 5}, error=None)

    @pytest.mark.asyncio
    async def test_execute_durable_job_failure_raises(self):
        async def failing_runner():
            raise RuntimeError("Database connection dropped during job")

        with patch("app.modules.jobs.update_job", new_callable=AsyncMock) as mock_update:
            with pytest.raises(RuntimeError, match="Database connection dropped"):
                await _execute_durable_job("job-456", failing_runner)
            mock_update.assert_any_call(
                "job-456",
                status="failed",
                result=None,
                error={"type": "RuntimeError", "message": "Database connection dropped during job"},
            )
