from __future__ import annotations

import importlib


def test_fourth_estate_legacy_import_boundary_resolves() -> None:
    module = importlib.import_module("app.services.fourth_estate")
    assert hasattr(module, "FourthEstateService")


def test_llm_gateway_legacy_import_boundary_resolves() -> None:
    module = importlib.import_module("app.core.llm_gateway")
    assert hasattr(module, "ExecutiveService")
    assert callable(module.active_provider_label)
