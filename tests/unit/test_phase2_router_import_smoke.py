from __future__ import annotations

import importlib

import pytest


ROUTERS = [
    "app.api_v2_routers.assessments",
    "app.api_v2_routers.onboarding",
    "app.api_v2_routers.gamification",
    "app.api_v2_routers.consent",
    "app.api_v2_routers.parents",
    "app.api_v2_routers.popia",
    "app.api_v2_routers.diagnostics",
    "app.api_v2_routers.lessons",
    "app.api_v2_routers.learners",
    "app.api_v2_routers.study_plans",
]


@pytest.mark.unit
@pytest.mark.parametrize("module_name", ROUTERS)
def test_phase2_router_imports(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert hasattr(module, "router")


@pytest.mark.unit
def test_canonical_v2_app_imports_with_phase2_routers() -> None:
    module = importlib.import_module("app.api_v2")
    assert hasattr(module, "app")
