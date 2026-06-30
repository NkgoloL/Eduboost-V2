"""
Regression tests for EduBoost V2 deployment entrypoints.
Verifies that the app can be imported and initialized via all supported paths.
"""
import pytest
from importlib import import_module

@pytest.mark.parametrize("import_path", [
    "app.api_v2",
    "app.legacy.api.main",
])
def test_app_importable(import_path):
    """Verify that the FastAPI app instance is available at each entrypoint."""
    module = import_module(import_path)
    assert hasattr(module, "app"), f"Module {import_path} missing 'app' attribute"
    assert module.app.title == "EduBoost SA V2", f"App title mismatch in {import_path}"

def test_v2_baseline_settings():
    """Verify that V2 settings are loaded correctly."""
    from app.core.config import settings
    assert settings.APP_VERSION.startswith("1.")
    assert settings.ARQ_MAX_JOBS == 10
