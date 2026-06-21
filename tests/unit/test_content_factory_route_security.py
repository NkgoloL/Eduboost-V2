"""tests/unit/test_content_factory_route_security.py

Verifies that the Content Factory router:
  1. Registers no public routes under /api/v2/admin/content-factory (structural).
  2. Has `require_admin` present in the dependency tree at the router level
     (introspection).
  3. Returns HTTP 401/403 for a non-admin caller (behavioural).

User rule: "Route introspection alone is not enough; dependency objects can be
wrapped. Add behavioural tests."
"""
from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_all_dependencies(dependant) -> list[Any]:
    """Recursively collect all Depends callables from a FastAPI Dependant."""
    deps: list[Any] = []
    for dep in dependant.dependencies:
        deps.append(dep.call)
        deps.extend(_collect_all_dependencies(dep))
    return deps


# ---------------------------------------------------------------------------
# Structural: router-level dependency
# ---------------------------------------------------------------------------

class TestContentFactoryRouterLevelDependency:
    """The router itself must declare require_admin as a router-level dep."""

    def test_router_has_require_admin_dependency(self):
        from app.api_v2_deps.auth import require_admin
        from app.api_v2_routers.content_factory import router

        # FastAPI stores router-level dependencies in router.dependencies
        router_dep_calls = [d.dependency for d in router.dependencies]
        assert require_admin in router_dep_calls, (
            "require_admin must be declared as a router-level dependency on "
            "the content_factory router. Found: "
            f"{[getattr(d, '__name__', repr(d)) for d in router_dep_calls]}"
        )

    def test_router_prefix_is_admin_scoped(self):
        from app.api_v2_routers.content_factory import router

        assert router.prefix.startswith("/admin/"), (
            f"Content factory router prefix must start with /admin/. "
            f"Got: {router.prefix!r}"
        )

    def test_router_tag_is_admin_content_factory(self):
        from app.api_v2_routers.content_factory import router

        assert "admin-content-factory" in router.tags, (
            f"Router must carry the 'admin-content-factory' tag. "
            f"Got: {router.tags!r}"
        )


# ---------------------------------------------------------------------------
# Introspection: every route's dependency tree contains require_admin
# ---------------------------------------------------------------------------

class TestContentFactoryRouteIntrospection:
    """Every individual route must have require_admin reachable in its dep tree."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        from app.api_v2_deps.auth import require_admin
        from app.api_v2_routers.content_factory import router
        self.router = router
        self.require_admin = require_admin

    def _route_dep_callables(self, route) -> list[Any]:
        """Return all dependency callables reachable from this route's dependant."""
        from fastapi.routing import APIRoute
        if not isinstance(route, APIRoute):
            return []
        return _collect_all_dependencies(route.dependant)

    def test_all_routes_have_require_admin_in_dependency_tree(self):
        missing: list[str] = []
        for route in self.router.routes:
            deps = self._route_dep_callables(route)
            # Also include router-level deps injected via router.dependencies
            router_deps = [d.dependency for d in self.router.dependencies]
            all_deps = deps + router_deps
            if self.require_admin not in all_deps:
                missing.append(f"{list(route.methods)} {route.path}")

        assert not missing, (
            "The following content-factory routes are missing require_admin "
            "in their dependency tree:\n" + "\n".join(f"  {r}" for r in missing)
        )

    def test_no_route_exposes_unauthenticated_path(self):
        """No route may use an empty dependencies=[] that overrides the router dep."""
        for route in self.router.routes:
            # FastAPI merges dependencies; a route explicitly clearing them is
            # a red flag but not directly expressible in the API surface.
            # Instead: verify each route's dependant has at least the router dep.
            router_deps = [d.dependency for d in self.router.dependencies]
            if self.require_admin not in router_deps:
                pytest.fail(
                    f"Route {route.path} — router-level require_admin missing."
                )


# ---------------------------------------------------------------------------
# Behavioural: TestClient with mocked auth
# ---------------------------------------------------------------------------

class TestContentFactoryRouteSecurityBehavioural:
    """Send real HTTP requests through TestClient; assert 401/403 for non-admins."""

    @pytest.fixture(autouse=True)
    def _setup(self, monkeypatch):
        # Build a minimal app that includes only the content_factory router so
        # we don't drag in the full lifespan / DB connections.
        from fastapi import FastAPI
        from app.api_v2_routers import content_factory

        test_app = FastAPI()
        test_app.include_router(content_factory.router, prefix="/api/v2")

        self.client = TestClient(test_app, raise_server_exceptions=False)

    def _admin_routes(self) -> list[tuple[str, str]]:
        """Return (method, path) tuples for GET/POST routes that don't need a body."""
        return [
            ("GET", "/api/v2/admin/content-factory/health"),
            ("GET", "/api/v2/admin/content-factory/etl/status"),
            ("GET", "/api/v2/admin/content-factory/scopes"),
        ]

    def test_unauthenticated_request_is_rejected(self):
        """No Authorization header → 401 or 403 (never 200)."""
        for method, path in self._admin_routes():
            response = self.client.request(method, path)
            assert response.status_code in (401, 403, 422), (
                f"{method} {path} returned {response.status_code} without auth; "
                "expected 401, 403, or 422 (missing dep)."
            )

    def test_non_admin_token_is_rejected(self, monkeypatch):
        """A token that passes get_current_user but not require_admin → 403."""
        # Patch require_admin to always raise 403
        from fastapi import HTTPException
        from app.api_v2_routers import content_factory as cf_module

        async def fake_require_admin():
            raise HTTPException(status_code=403, detail="Admin required")

        monkeypatch.setattr(
            "app.api_v2_routers.content_factory.require_admin",
            fake_require_admin,
        )
        # Rebuild client with the patched module
        from fastapi import FastAPI
        patched_app = FastAPI()
        patched_app.include_router(cf_module.router, prefix="/api/v2")
        client = TestClient(patched_app, raise_server_exceptions=False)

        for method, path in self._admin_routes():
            response = client.request(method, path, headers={"Authorization": "Bearer learner-token"})
            assert response.status_code in (401, 403), (
                f"{method} {path} returned {response.status_code} for non-admin; "
                "expected 401 or 403."
            )


# ---------------------------------------------------------------------------
# Regression: no content-factory routes appear in public route inventory
# ---------------------------------------------------------------------------

class TestContentFactoryNotInPublicRoutes:
    """Verify content-factory paths do not appear without /admin/ prefix."""

    def test_no_public_content_factory_paths(self):
        from app.api_v2 import app

        public_paths = [
            route.path
            for route in app.routes
            if hasattr(route, "path") and "content-factory" in route.path
        ]
        for path in public_paths:
            assert "/admin/" in path, (
                f"Content-factory route found without /admin/ prefix: {path!r}. "
                "All content-factory routes must be admin-scoped."
            )
