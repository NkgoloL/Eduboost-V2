"""
Content Factory startup feature flag smoke tests.
Verifies that the Content Factory control plane initializes safely
with generation and startup seed disabled by default.
"""
import pytest

pytestmark = pytest.mark.smoke


class TestContentFactoryStartupFlags:
    """Test that feature flags keep Content Factory safely disabled."""

    def test_app_imports_with_generation_disabled(self, monkeypatch):
        """App should import successfully with CONTENT_FACTORY_GENERATION_ENABLED=false."""
        monkeypatch.setenv("CONTENT_FACTORY_GENERATION_ENABLED", "false")
        from app.api_v2 import app
        assert app is not None

    def test_app_imports_with_startup_seed_disabled(self, monkeypatch):
        """App should import successfully with CONTENT_STARTUP_SEED_ENABLED=false."""
        monkeypatch.setenv("CONTENT_STARTUP_SEED_ENABLED", "false")
        from app.api_v2 import app
        assert app is not None

    def test_no_public_content_factory_route(self):
        """No public /api/v2/content-factory route should exist."""
        from app.api_v2 import app
        routes = [route.path for route in app.routes]
        public_cf_routes = [
            r for r in routes
            if "/api/v2/content-factory" in r and "/admin" not in r
        ]
        assert len(public_cf_routes) == 0, (
            f"Found public content-factory routes: {public_cf_routes}. "
            "Content Factory must be admin-only."
        )

    def test_both_safety_flags_default_false(self):
        """Both safety flags should default to false in config."""
        from app.core.config import settings
        assert settings.CONTENT_FACTORY_GENERATION_ENABLED is False
        assert settings.CONTENT_STARTUP_SEED_ENABLED is False

    def test_admin_routers_registered(self):
        """Admin Content Factory routers must be registered."""
        from app.api_v2 import app
        routes = [route.path for route in app.routes]
        admin_routes = [r for r in routes if "/api/v2/admin/content-factory" in r]
        assert len(admin_routes) > 0, "No admin content-factory routes registered"
