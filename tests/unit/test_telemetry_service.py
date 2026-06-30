"""tests/unit/test_telemetry_service.py
Unit tests for TelemetryService POPIA-safe analytics dispatch.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.telemetry import TelemetryService, validate_event_payload


def test_analytics_payload_keeps_only_allowlisted_properties():
    payload = validate_event_payload(
        "lesson_viewed",
        "learner:abc123",
        {"topic_ref": "CAPS:demo", "email": "child@example.com", "path": "/lesson"},
    )
    assert payload["properties"] == {"topic_ref": "CAPS:demo", "path": "/lesson"}


def test_analytics_distinct_id_rejects_direct_email():
    with pytest.raises(ValueError):
        validate_event_payload("lesson_viewed", "child@example.com", {})


def test_analytics_event_name_must_be_snake_case():
    with pytest.raises(ValueError, match="event_name must be snake_case alphanumeric"):
        validate_event_payload("Invalid-Name!", "learner:abc123", {})


def test_analytics_distinct_id_rejects_long_strings():
    with pytest.raises(ValueError, match="distinct_id must be pseudonymous"):
        validate_event_payload("lesson_viewed", "a" * 129, {})


def test_analytics_payload_returns_anonymous_for_empty_pseudonym():
    payload = validate_event_payload("lesson_viewed", "", {})
    assert payload["distinct_id"] == "anonymous"


@pytest.mark.unit
async def test_telemetry_noop_when_capability_unavailable():
    """Verify telemetry logs no-op when analytics capability is unavailable."""
    service = TelemetryService()

    from types import SimpleNamespace
    capability = SimpleNamespace(status="unavailable", reason="disabled")

    with patch("app.services.telemetry.get_runtime_capabilities") as mock_caps:
        mock_caps.return_value = {"analytics": capability}
        with patch("app.services.telemetry.log") as mock_log:
            await service.track_event_async("lesson_viewed", "learner:abc123", {"path": "/lesson"})
            mock_log.info.assert_called_once()
            call_kwargs = mock_log.info.call_args[1]
            assert call_kwargs["event_name"] == "lesson_viewed"
            assert call_kwargs["distinct_id"] == "learner:abc123"
            assert call_kwargs["reason"] == "disabled"




@pytest.mark.unit
async def test_telemetry_sanitizes_properties():
    """Verify sanitize_properties filters to allowlist only."""
    service = TelemetryService()
    properties = {
        "path": "/lesson",
        "email": "child@example.com",
        "grade_band": "4",
        "subject": "mathematics",
    }
    result = service.sanitize_properties(properties)
    assert result == {"path": "/lesson", "grade_band": "4", "subject": "mathematics"}
    assert "email" not in result
