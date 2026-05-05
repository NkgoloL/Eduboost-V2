import pytest
from importlib import import_module

def test_v2_app_importable():
    """Verify that the V2 app can be imported from the canonical entrypoint."""
    module = import_module("app.api_v2")
    assert hasattr(module, "app")
    assert module.app.title == "EduBoost SA V2"

def test_legacy_shim_importable():
    """Verify that the legacy shim correctly imports the V2 app."""
    module = import_module("app.legacy.api.main")
    assert hasattr(module, "app")
    assert module.app.title == "EduBoost SA V2"

def test_uvicorn_command_simulation():
    """Verify that the common uvicorn command strings would work."""
    # This just ensures the paths are correct for uvicorn app.api_v2:app
    # and uvicorn app.legacy.api.main:app
    import_module("app.api_v2")
    import_module("app.legacy.api.main")

def test_legacy_routes_hidden_in_schema():
    """Verify that legacy routes are not exposed in the OpenAPI schema."""
    from app.api_v2 import app
    schema = app.openapi()
    paths = schema.get("paths", {})
    # Check that /api/v1/lessons/generate is NOT in the paths
    assert "/api/v1/lessons/generate" not in paths
