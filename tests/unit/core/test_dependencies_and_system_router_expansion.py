"""Comprehensive unit tests for FastAPI core dependencies and system router endpoints."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch
import pytest

from app.core.dependencies import (
    get_current_guardian_id,
    get_current_user_id,
)
from app.core.exceptions import AuthenticationError
from app.api_v2_routers.system import router as system_router


class TestCoreDependencies:
    @pytest.mark.asyncio
    async def test_get_current_guardian_id_alias(self):
        uid = uuid.uuid4()
        guardian_id = await get_current_guardian_id(user_id=uid)
        assert guardian_id == uid

    @pytest.mark.asyncio
    async def test_get_current_user_id_missing_credentials_raises(self):
        with pytest.raises(AuthenticationError, match="Authorization header missing"):
            await get_current_user_id(credentials=None)


class TestSystemRouterDefinition:
    def test_system_router_routes(self):
        route_paths = [route.path for route in system_router.routes]
        assert "/system/health" in route_paths
        assert "/system/pillars" in route_paths
        assert "/system/schema-status" in route_paths
        assert "/system/capabilities" in route_paths
