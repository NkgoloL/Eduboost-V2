"""Runtime entrypoint contract tests for the EduBoost V2 FastAPI app.

These tests intentionally avoid live database/Redis calls. They prove that the
canonical production runtime imports cleanly and exposes the expected route
surface for smoke checks, deployment commands, and later OpenAPI generation.
"""
from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI

# Some local/CI invocations do not automatically place the repository root on
# sys.path before collection. Make the runtime import contract explicit so
# ``import_module("app.api_v2")`` behaves the same way uvicorn resolves
# ``app.api_v2:app`` from the repository root.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_app(spec: str) -> FastAPI:
    """Load an ASGI app from a uvicorn-style ``module:attribute`` spec."""
    module_path, separator, attribute = spec.partition(":")
    assert separator == ":", f"Invalid ASGI app spec: {spec!r}"

    module = import_module(module_path)
    app = getattr(module, attribute)

    assert isinstance(app, FastAPI)
    return app


@pytest.mark.unit
def test_canonical_v2_app_import_contract() -> None:
    """The production runtime must be importable as ``app.api_v2:app``."""
    app = _load_app("app.api_v2:app")

    assert app.title == "EduBoost SA V2"
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"
    assert app.openapi_url == "/openapi.json"


@pytest.mark.unit
def test_v2_runtime_exposes_required_operational_routes() -> None:
    """Deployment and monitoring depend on these process-local routes existing."""
    app = _load_app("app.api_v2:app")
    route_paths = {route.path for route in app.routes}

    assert {
        "/",
        "/health",
        "/ready",
        "/metrics",
        "/v2/health/deep",
        "/docs",
        "/redoc",
        "/openapi.json",
    }.issubset(route_paths)


@pytest.mark.unit
def test_v2_runtime_registers_dual_api_prefixes() -> None:
    """During migration, V2 routers must be reachable under both supported prefixes."""
    app = _load_app("app.api_v2:app")
    route_paths = {route.path for route in app.routes}

    required_prefixes = ("/api/v2", "/v2")
    required_router_fragments = (
        "/auth",
        "/learners",
        "/lessons",
        "/study-plans",
        "/diagnostics",
        "/gamification",
        "/onboarding",
        "/parents",
        "/billing",
        "/consent",
        "/popia",
        "/jobs",
        "/system",
    )

    missing: list[str] = []
    for prefix in required_prefixes:
        for fragment in required_router_fragments:
            if not any(path.startswith(f"{prefix}{fragment}") for path in route_paths):
                missing.append(f"{prefix}{fragment}")

    assert missing == []


@pytest.mark.unit
def test_legacy_compatibility_shim_reuses_canonical_v2_app() -> None:
    """The archived legacy entrypoint must not construct a separate FastAPI app."""
    canonical_app = _load_app("app.api_v2:app")
    legacy_app = _load_app("app.legacy.api.main:app")

    canonical_routes = {route.path for route in canonical_app.routes}
    legacy_routes = {route.path for route in legacy_app.routes}

    assert canonical_routes.issubset(legacy_routes)


@pytest.mark.unit
def test_legacy_routes_hidden_from_v2_openapi_schema() -> None:
    """Legacy compatibility routes must not appear in the production API schema."""
    app = _load_app("app.api_v2:app")
    paths: dict[str, Any] = app.openapi().get("paths", {})

    assert "/api/v1/lessons/generate" not in paths


@pytest.mark.unit
def test_api_main_compatibility_shim_import_contract() -> None:
    """The compatibility shim must expose the canonical V2 FastAPI app."""
    shim_app = _load_app("app.api.main:app")
    canonical_app = _load_app("app.api_v2:app")

    assert shim_app is canonical_app
    assert shim_app.title == canonical_app.title


@pytest.mark.unit
def test_api_main_compatibility_shim_exposes_health_and_ready() -> None:
    """Smoke checks can keep using app.api.main while resolving to V2 routes."""
    app = _load_app("app.api.main:app")
    route_paths = {route.path for route in app.routes}

    assert "/health" in route_paths
    assert "/ready" in route_paths
