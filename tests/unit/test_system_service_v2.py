"""tests/unit/test_system_service_v2.py
Unit tests for SystemServiceV2 health and status endpoints.
"""
from __future__ import annotations

import pytest

from app.services.system_service_v2 import SystemServiceV2


@pytest.mark.unit
async def test_health_returns_status_and_version():
    """Verify health endpoint returns status, version, and mode."""
    service = SystemServiceV2()
    result = await service.health()

    assert result["status"] == "ok"
    assert "version" in result
    assert result["mode"] == "v2-baseline"


@pytest.mark.unit
async def test_pillars_returns_architecture_and_pillars_list():
    """Verify pillars endpoint returns architecture and pillar list."""
    service = SystemServiceV2()
    result = await service.pillars()

    assert result["architecture"] == "modular-monolith"
    assert result["audit_target"] == "postgresql-append-only"
    assert isinstance(result["pillars"], list)
    assert "diagnostics" in result["pillars"]
    assert "lessons" in result["pillars"]
    assert "gamification" in result["pillars"]
    assert "audit" in result["pillars"]
    assert "parent_portal" in result["pillars"]


@pytest.mark.unit
async def test_schema_status_returns_ok():
    """Verify schema_status endpoint returns ok status."""
    service = SystemServiceV2()
    result = await service.schema_status()

    assert result["status"] == "ok"
    assert result["schema"] == "v2"
