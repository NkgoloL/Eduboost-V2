import pytest

from app.services.system_service_v2 import SystemServiceV2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_system_service_v2_pillars():
    payload = await SystemServiceV2().pillars()
    assert payload["architecture"] == "modular-monolith"
    assert payload["audit_target"] == "postgresql-append-only"
