from app.core.analytics import build_analytics_payload
from app.services.telemetry import TelemetryService


def test_telemetry_uses_distinct_id_and_path_only():
    payload = build_analytics_payload(
        "lesson_viewed",
        "pseudo-123",
        "/api/v2/lessons/abc",
        {"subject": "Mathematics"},
    )

    assert payload["analytics_event"] == "lesson_viewed"
    assert payload["distinct_id"] == "pseudo-123"
    assert payload["properties"]["path"] == "/api/v2/lessons/abc"
    assert "user_id" not in payload


def test_telemetry_sanitises_pii_properties():
    properties = TelemetryService.sanitize_properties(
        {
            "subject": "Mathematics",
            "email": "parent@example.com",
            "display_name": "Sipho",
            "guardian_id": "guardian-123",
            "notes": "contact me at parent@example.com",
            "safe_flag": True,
        }
    )

    assert properties == {"subject": "Mathematics", "safe_flag": True}
