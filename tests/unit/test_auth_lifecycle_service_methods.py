from __future__ import annotations

import asyncio
from pathlib import Path

from app.services.auth_application_service import AuthApplicationService


ROOT = Path(__file__).resolve().parents[2]


def test_auth_application_service_has_lifecycle_methods():
    service = AuthApplicationService(db=None)
    assert hasattr(service, "register")
    assert hasattr(service, "login")
    assert hasattr(service, "refresh")


def test_auth_application_service_lifecycle_methods_delegate_to_legacy_impl():
    async def run():
        service = AuthApplicationService(db=None)

        async def legacy_impl(**kwargs):
            return {"called": True, "keys": sorted(kwargs)}

        result = await service.register(legacy_impl=legacy_impl, payload="x")
        assert result["called"] is True
        assert "payload" in result["keys"]

    asyncio.run(run())


def test_auth_router_delegates_lifecycle_methods_to_service():
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert "auth_service.register(" in source
    assert "auth_service.login(" in source
    assert "auth_service.refresh(" in source
    assert "_auth_lifecycle_legacy_register_impl" in source
    assert "_auth_lifecycle_legacy_login_impl" in source
    assert "_auth_lifecycle_legacy_refresh_impl" in source


def test_auth_router_has_no_repository_imports_or_future_annotations():
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert "from __future__ import annotations" not in source
    assert "from app.repositories" not in source
