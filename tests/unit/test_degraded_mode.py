from app.core.degraded_mode import capabilities_payload, get_runtime_capabilities


def test_runtime_capabilities_have_fallbacks():
    capabilities = get_runtime_capabilities()
    assert {"llm_generation", "billing", "email", "analytics"}.issubset(capabilities)
    for capability in capabilities.values():
        assert capability.criticality == "optional"
        assert capability.fallback
        assert capability.status in {"available", "degraded", "disabled"}


def test_capabilities_payload_is_non_sensitive():
    payload = capabilities_payload()
    rendered = str(payload).lower()
    assert "secret" not in rendered
    assert "api_key" not in rendered
    assert "bearer" not in rendered
    assert payload["status"] in {"ok", "degraded"}
