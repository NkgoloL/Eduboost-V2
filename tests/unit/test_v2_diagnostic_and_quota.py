import pytest

from app.services.quota_service import QuotaExceededError


class DummyQuotaService:
    def __init__(self):
        self.calls = 0

    async def assert_within_quota(self, subject: str):
        self.calls += 1
        if self.calls > 1:
            raise QuotaExceededError("limit reached")

    async def get_cached(self, namespace: str, payload: dict):
        return None

    async def set_cached(self, namespace: str, payload: dict, value):
        return None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dummy_quota_service_raises_after_limit():
    service = DummyQuotaService()
    await service.assert_within_quota("diagnostic:user-1")
    with pytest.raises(QuotaExceededError):
        await service.assert_within_quota("diagnostic:user-1")
