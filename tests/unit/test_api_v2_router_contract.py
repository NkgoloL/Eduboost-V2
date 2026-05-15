from __future__ import annotations

import pytest

from app.api_v2 import API_PREFIXES, ROUTER_REGISTRY, app


@pytest.mark.unit
def test_router_registry_has_unique_names() -> None:
    names = [name for name, _router in ROUTER_REGISTRY]

    assert len(names) == len(set(names))
    assert "system" in names
    assert "diagnostics" in names
    assert "popia" in names


@pytest.mark.unit
def test_registered_router_fragments_are_exposed_under_each_v2_prefix() -> None:
    route_paths = {route.path for route in app.routes}
    expected_fragments = {
        "auth": "/auth",
        "learners": "/learners",
        "lessons": "/lessons",
        "study_plans": "/study-plans",
        "diagnostics": "/diagnostics",
        "practice": "/practice",
        "gamification": "/gamification",
        "onboarding": "/onboarding",
        "parents": "/parents",
        "billing": "/billing",
        "consent": "/consent",
        "consent_renewal": "/consent",
        "audit": "/audit",
        "popia": "/popia",
        "jobs": "/jobs",
        "system": "/system",
    }

    missing: list[str] = []
    for prefix in API_PREFIXES:
        for router_name, _router in ROUTER_REGISTRY:
            fragment = expected_fragments[router_name]
            expected_prefix = f"{prefix}{fragment}"
            if not any(path == expected_prefix or path.startswith(f"{expected_prefix}/") for path in route_paths):
                missing.append(f"{router_name}:{expected_prefix}")

    assert missing == []


@pytest.mark.unit
def test_legacy_prefixes_are_not_exposed_by_canonical_runtime() -> None:
    forbidden_prefixes = ("/api/v1", "/v1", "/api/legacy", "/legacy")
    route_paths = {route.path for route in app.routes}

    assert [
        path for path in route_paths if path.startswith(forbidden_prefixes)
    ] == []
