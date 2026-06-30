"""tests/unit/test_llm_init.py
Ensure app.services.llm package exposes the canonical API surface.
"""
from __future__ import annotations

import importlib


def test_llm_init_exports_all_symbols():
    mod = importlib.import_module("app.services.llm")
    assert hasattr(mod, "__all__")
    expected = [
        "CanonicalLLMGateway",
        "DeterministicMockProvider",
        "LLMGatewayMetadata",
        "LLMGatewayRequest",
        "LLMGatewayResponse",
        "ProviderHealth",
        "ProviderPolicy",
        "ProviderResult",
    ]
    assert sorted(mod.__all__) == sorted(expected)


def test_llm_init_reexports_are_importable():
    # Import re-exported names directly from the package
    from app.services.llm import (
        CanonicalLLMGateway,
        DeterministicMockProvider,
        LLMGatewayMetadata,
        LLMGatewayRequest,
        LLMGatewayResponse,
        ProviderHealth,
        ProviderPolicy,
        ProviderResult,
    )

    # Only type checks to ensure names are bound; no heavy instantiation
    assert CanonicalLLMGateway is not None
    assert DeterministicMockProvider is not None
    assert LLMGatewayMetadata is not None
    assert LLMGatewayRequest is not None
    assert LLMGatewayResponse is not None
    assert ProviderHealth is not None
    assert ProviderPolicy is not None
    assert ProviderResult is not None
