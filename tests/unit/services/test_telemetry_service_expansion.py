"""Batch 199: Unit tests for telemetry service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.telemetry import (
    ALLOWED_ANALYTICS_PROPERTIES,
    TelemetryService,
    validate_event_payload,
)


# ─────────────────────────────────────────────
# validate_event_payload
# ─────────────────────────────────────────────


class TestValidateEventPayload:
    def test_valid_payload_returns_dict(self):
        result = validate_event_payload(
            "lesson_completed",
            "pseudonym_abc123",
            {"subject": "Mathematics", "grade_band": "intermediate"},
        )
        assert result["event"] == "lesson_completed"
        assert result["distinct_id"] == "pseudonym_abc123"
        assert result["properties"]["subject"] == "Mathematics"

    def test_filters_out_disallowed_properties(self):
        result = validate_event_payload(
            "lesson_completed",
            "pseudonym_abc123",
            {"subject": "Maths", "email": "user@example.com", "pii_field": "sensitive"},
        )
        assert "email" not in result["properties"]
        assert "pii_field" not in result["properties"]
        assert "subject" in result["properties"]

    def test_empty_event_name_raises(self):
        with pytest.raises(ValueError, match="event_name"):
            validate_event_payload("", "pseudonym_abc123", {})

    def test_event_name_with_special_chars_raises(self):
        with pytest.raises(ValueError, match="event_name"):
            validate_event_payload("lesson.completed!", "pseudonym_abc123", {})

    def test_email_in_distinct_id_raises(self):
        with pytest.raises(ValueError, match="distinct_id"):
            validate_event_payload("lesson_completed", "user@example.com", {})

    def test_long_distinct_id_raises(self):
        with pytest.raises(ValueError, match="distinct_id"):
            validate_event_payload("lesson_completed", "x" * 129, {})

    def test_empty_distinct_id_falls_back_to_anonymous(self):
        # Empty string is allowed but replaced with 'anonymous'
        # Note: "" doesn't contain "@" and len <= 128 so passes validation
        result = validate_event_payload("lesson_completed", "", {})
        assert result["distinct_id"] == "anonymous"

    def test_all_allowed_properties_pass_through(self):
        props = {key: "value" for key in ALLOWED_ANALYTICS_PROPERTIES}
        result = validate_event_payload("test_event", "pseudonym_xyz", props)
        for key in ALLOWED_ANALYTICS_PROPERTIES:
            assert key in result["properties"]

    def test_numeric_event_name_is_valid(self):
        result = validate_event_payload("event123", "pseudonym_abc123", {})
        assert result["event"] == "event123"


# ─────────────────────────────────────────────
# TelemetryService.sanitize_properties
# ─────────────────────────────────────────────


class TestTelemetryServiceSanitizeProperties:
    def _service(self):
        return TelemetryService()

    def test_allowed_properties_kept(self):
        props = {"subject": "Maths", "grade_band": "senior", "pii": "secret"}
        result = self._service().sanitize_properties(props)
        assert "subject" in result
        assert "grade_band" in result
        assert "pii" not in result

    def test_empty_props_returns_empty(self):
        result = self._service().sanitize_properties({})
        assert result == {}

    def test_all_disallowed_props_returns_empty(self):
        props = {"email": "user@e.com", "name": "John", "id_number": "9001015009087"}
        result = self._service().sanitize_properties(props)
        assert result == {}


# ─────────────────────────────────────────────
# TelemetryService.track_event_async
# ─────────────────────────────────────────────


class TestTelemetryServiceTrackEventAsync:
    def _service(self):
        return TelemetryService()

    @pytest.mark.asyncio
    async def test_noop_when_analytics_unavailable(self):
        """When analytics capability is not available, method should return without error."""
        service = self._service()
        from unittest.mock import patch
        mock_capability = MagicMock()
        mock_capability.status = "unavailable"
        mock_capability.reason = "not configured"

        with patch("app.services.telemetry.get_runtime_capabilities", return_value={"analytics": mock_capability}):
            # Should not raise
            await service.track_event_async("lesson_completed", "pseudonym_abc", {"subject": "Maths"})

    @pytest.mark.asyncio
    async def test_dispatches_when_analytics_available(self):
        """When analytics is available, it should attempt posthog.capture."""
        service = self._service()
        mock_capability = MagicMock()
        mock_capability.status = "available"

        mock_posthog = MagicMock()

        with patch("app.services.telemetry.get_runtime_capabilities", return_value={"analytics": mock_capability}):
            with patch.dict("sys.modules", {"posthog": mock_posthog}):
                await service.track_event_async("lesson_completed", "pseudonym_abc", {"subject": "Maths"})
                mock_posthog.capture.assert_called_once()

    @pytest.mark.asyncio
    async def test_swallows_dispatch_exception_gracefully(self):
        """Exception in posthog dispatch should not propagate to caller."""
        service = self._service()
        mock_capability = MagicMock()
        mock_capability.status = "available"

        mock_posthog = MagicMock()
        mock_posthog.capture.side_effect = RuntimeError("posthog down")

        with patch("app.services.telemetry.get_runtime_capabilities", return_value={"analytics": mock_capability}):
            with patch.dict("sys.modules", {"posthog": mock_posthog}):
                # Should not raise despite posthog error
                await service.track_event_async("lesson_completed", "pseudonym_abc", {})

    @pytest.mark.asyncio
    async def test_invalid_event_name_raises_value_error(self):
        """Invalid event_name raises ValueError before any dispatch attempt."""
        service = self._service()
        with pytest.raises(ValueError, match="event_name"):
            await service.track_event_async("bad.event!", "pseudonym_abc", {})

    @pytest.mark.asyncio
    async def test_email_as_distinct_id_raises_value_error(self):
        service = self._service()
        with pytest.raises(ValueError, match="distinct_id"):
            await service.track_event_async("lesson_completed", "user@example.com", {})


# ─────────────────────────────────────────────
# ALLOWED_ANALYTICS_PROPERTIES
# ─────────────────────────────────────────────


class TestAllowedAnalyticsProperties:
    def test_is_a_set(self):
        assert isinstance(ALLOWED_ANALYTICS_PROPERTIES, set)

    def test_contains_expected_keys(self):
        expected = {"path", "grade_band", "subject", "activity_type", "correctness"}
        assert expected.issubset(ALLOWED_ANALYTICS_PROPERTIES)

    def test_does_not_contain_pii_keys(self):
        pii_keys = {"email", "name", "phone", "id_number", "address"}
        assert pii_keys.isdisjoint(ALLOWED_ANALYTICS_PROPERTIES)
