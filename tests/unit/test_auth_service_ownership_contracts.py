from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_auth_router_no_longer_contains_legacy_lifecycle_helpers():
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert "_auth_lifecycle_legacy_" not in source
    assert "from app.repositories" not in source
    assert "from __future__ import annotations" not in source


def test_auth_application_service_owns_lifecycle_methods():
    service_module = importlib.import_module("app.services.auth_application_service")
    service_cls = service_module.AuthApplicationService
    for method in ("register", "login", "refresh"):
        assert hasattr(service_cls, method)


def test_auth_lifecycle_impl_module_contains_migrated_functions():
    impl = importlib.import_module("app.services.auth_lifecycle_impl")
    for method in ("register_impl", "login_impl", "refresh_impl"):
        assert hasattr(impl, method)


def test_auth_router_delegates_lifecycle_routes_to_service():
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert "auth_service.register(" in source
    assert "auth_service.login(" in source
    assert "auth_service.refresh(" in source
