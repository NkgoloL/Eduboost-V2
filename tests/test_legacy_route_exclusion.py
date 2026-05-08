"""Legacy route exclusion tests for the EduBoost V2 runtime.

The production runtime is ``app.api_v2:app``. Archived compatibility shims may
exist, but importing the canonical V2 app alone must not expose legacy V1 route
patterns. Tests use subprocess isolation where import order matters because the
legacy shim intentionally imports the canonical app object before attaching its
410 Gone compatibility route.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _run_python(code: str) -> dict[str, Any]:
    """Run a small Python snippet from the repo root and decode JSON stdout."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _route_paths(app: FastAPI) -> set[str]:
    return {route.path for route in app.routes if isinstance(route, APIRoute)}


@pytest.mark.unit
def test_canonical_v2_import_does_not_register_legacy_v1_routes() -> None:
    """Importing ``app.api_v2:app`` alone must not expose archived V1 routes."""
    payload = _run_python(
        """
import json
from fastapi.routing import APIRoute
from app.api_v2 import app

paths = sorted(route.path for route in app.routes if isinstance(route, APIRoute))
print(json.dumps({"paths": paths}))
"""
    )

    legacy_paths = [path for path in payload["paths"] if path.startswith("/api/v1")]
    assert legacy_paths == []


@pytest.mark.unit
def test_canonical_v2_openapi_schema_excludes_legacy_v1_routes() -> None:
    """The production OpenAPI schema must remain V2-only."""
    payload = _run_python(
        """
import json
from app.api_v2 import app

paths = sorted(app.openapi().get("paths", {}).keys())
print(json.dumps({"paths": paths}))
"""
    )

    legacy_paths = [path for path in payload["paths"] if path.startswith("/api/v1")]
    assert legacy_paths == []


@pytest.mark.unit
def test_archived_app_api_package_is_not_importable() -> None:
    """The removed V1 package path must not return as an active runtime surface."""
    payload = _run_python(
        """
import importlib.util
import json

print(json.dumps({"app_api_exists": importlib.util.find_spec("app.api") is not None}))
"""
    )

    assert payload["app_api_exists"] is False


@pytest.mark.unit
def test_legacy_compatibility_route_is_hidden_from_schema_when_shim_is_imported() -> None:
    """If the shim is imported, its V1 410 route must remain out of OpenAPI."""
    from app.legacy.api.main import app

    assert "/api/v1/lessons/generate" in _route_paths(app)
    assert "/api/v1/lessons/generate" not in app.openapi().get("paths", {})


@pytest.mark.unit
def test_legacy_compatibility_route_returns_410_gone() -> None:
    """The retained compatibility shim must fail closed with HTTP 410 Gone."""
    from app.legacy.api.main import app

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post("/api/v1/lessons/generate", json={})

    assert response.status_code == 410
    payload = response.json()
    assert payload["data"] is None
    assert payload["error"]["code"] == "http_error"
    assert "moved to /api/v2/lessons/generate" in payload["error"]["message"]
    assert payload["meta"]["api_version"] == "v2"
