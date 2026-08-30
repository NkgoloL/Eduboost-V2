"""Comprehensive unit tests for SystemServiceV2."""
from __future__ import annotations

import pytest

from app.services.system_service_v2 import SystemServiceV2


class TestSystemServiceV2:
    @pytest.mark.asyncio
    async def test_health_check(self):
        service = SystemServiceV2()
        res = await service.health()
        assert res["status"] == "ok"
        assert res["mode"] == "v2-baseline"
        assert "version" in res

    @pytest.mark.asyncio
    async def test_pillars_response(self):
        service = SystemServiceV2()
        res = await service.pillars()
        assert res["architecture"] == "modular-monolith"
        assert "diagnostics" in res["pillars"]
        assert "lessons" in res["pillars"]
        assert "gamification" in res["pillars"]

    @pytest.mark.asyncio
    async def test_schema_status(self):
        service = SystemServiceV2()
        res = await service.schema_status()
        assert res["status"] == "ok"
        assert res["schema"] == "v2"
