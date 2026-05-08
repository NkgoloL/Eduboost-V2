import pytest

from app.services.telemetry import validate_event_payload


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
