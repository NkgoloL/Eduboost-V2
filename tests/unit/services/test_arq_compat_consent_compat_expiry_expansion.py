"""Batch 194: Unit tests for arq_import_compat and consent_compat services."""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.arq_import_compat import (
    ARQ_AVAILABLE,
    ARQ_IMPORT_ERROR,
    arq_dependency_status,
    RedisSettings,
    cron,
)
from app.services.consent_compat import (
    ConsentAuditEvent,
    READ_CONSENT_ACTIONS,
    WRITE_CONSENT_ACTIONS,
    classify_consent_action,
    normalize_consent_audit_event,
)


# ─────────────────────────────────────────────
# arq_import_compat
# ─────────────────────────────────────────────


class TestArqImportCompat:
    def test_arq_dependency_status_returns_dict(self):
        status = arq_dependency_status()
        assert isinstance(status, dict)
        assert "available" in status
        assert "import_error" in status

    def test_arq_available_is_bool(self):
        assert isinstance(ARQ_AVAILABLE, bool)

    def test_arq_import_error_is_string(self):
        assert isinstance(ARQ_IMPORT_ERROR, str)

    def test_redis_settings_instantiation(self):
        # The RedisSettings class should always be importable regardless of arq availability
        rs = RedisSettings()
        assert hasattr(rs, "host")
        assert hasattr(rs, "port")

    def test_redis_settings_custom(self):
        rs = RedisSettings(host="redis-host", port=6380)
        assert rs.host == "redis-host"
        assert rs.port == 6380

    def test_cron_callable_returns_function(self):
        async def my_task():
            pass

        result = cron(my_task, hour=1, minute=0)
        # result is either CronJob (when arq installed) or decorated function (fallback)
        assert result is not None
        assert callable(result) or hasattr(result, "coroutine") or type(result).__name__ == "CronJob"


# ─────────────────────────────────────────────
# consent_compat
# ─────────────────────────────────────────────


class TestConsentAuditEvent:
    def test_to_audit_kwargs_basic(self):
        event = ConsentAuditEvent(
            action="consent.granted",
            actor_id="guardian-1",
            learner_id="learner-1",
        )
        kwargs = event.to_audit_kwargs()
        assert kwargs["action"] == "consent.granted"
        assert kwargs["actor_id"] == "guardian-1"
        assert kwargs["resource_type"] == "learner_consent"
        assert kwargs["resource_id"] == "learner-1"  # falls back to learner_id
        assert kwargs["metadata"]["learner_id"] == "learner-1"

    def test_to_audit_kwargs_with_resource_id(self):
        event = ConsentAuditEvent(
            action="consent.revoked",
            actor_id="guardian-2",
            learner_id="learner-2",
            resource_id="resource-xyz",
        )
        kwargs = event.to_audit_kwargs()
        assert kwargs["resource_id"] == "resource-xyz"

    def test_to_audit_kwargs_metadata_merged(self):
        event = ConsentAuditEvent(
            action="consent.renewed",
            actor_id="guardian-3",
            learner_id="learner-3",
            metadata={"policy_version": "v2"},
        )
        kwargs = event.to_audit_kwargs()
        assert kwargs["metadata"]["policy_version"] == "v2"
        assert kwargs["metadata"]["learner_id"] == "learner-3"

    def test_frozen_dataclass_immutable(self):
        event = ConsentAuditEvent(
            action="consent.granted",
            actor_id="a",
            learner_id="b",
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            event.action = "mutated"


class TestNormalizeConsentAuditEvent:
    def test_basic_normalization(self):
        event = normalize_consent_audit_event(
            action="consent.granted",
            actor_id="guardian-1",
            learner_id="learner-1",
        )
        assert isinstance(event, ConsentAuditEvent)
        assert event.action == "consent.granted"
        assert event.learner_id == "learner-1"

    def test_uses_resource_id_when_no_learner_id(self):
        event = normalize_consent_audit_event(
            action="consent.revoked",
            actor_id="guardian-1",
            resource_id="learner-from-resource",
        )
        assert event.learner_id == "learner-from-resource"

    def test_missing_action_raises_value_error(self):
        with pytest.raises(ValueError, match="action"):
            normalize_consent_audit_event(
                action="",
                actor_id="guardian-1",
                learner_id="learner-1",
            )

    def test_missing_actor_id_raises_value_error(self):
        with pytest.raises(ValueError, match="actor_id"):
            normalize_consent_audit_event(
                action="consent.granted",
                actor_id="",
                learner_id="learner-1",
            )

    def test_missing_learner_id_and_resource_id_raises(self):
        with pytest.raises(ValueError, match="learner_id"):
            normalize_consent_audit_event(
                action="consent.granted",
                actor_id="guardian-1",
            )

    def test_extra_kwargs_merged_into_metadata(self):
        event = normalize_consent_audit_event(
            action="consent.granted",
            actor_id="guardian-1",
            learner_id="learner-1",
            metadata={"base": "value"},
            extra_key="extra_val",
        )
        assert event.metadata["base"] == "value"
        assert event.metadata["extra_key"] == "extra_val"


class TestClassifyConsentAction:
    def test_read_actions_classified_as_read(self):
        for action in READ_CONSENT_ACTIONS:
            assert classify_consent_action(action) == "read"

    def test_write_actions_classified_as_write(self):
        for action in WRITE_CONSENT_ACTIONS:
            assert classify_consent_action(action) == "write"

    def test_unknown_action_classified_as_unknown(self):
        assert classify_consent_action("consent.unknown.action") == "unknown"
        assert classify_consent_action("") == "unknown"

    def test_all_read_actions_present(self):
        expected = {"consent.status.read", "consent.export.read", "consent.audit.read"}
        assert expected == READ_CONSENT_ACTIONS

    def test_all_write_actions_present(self):
        expected = {
            "consent.granted", "consent.revoked", "consent.renewed",
            "consent.restricted", "consent.erasure.requested", "consent.erasure.cancelled",
        }
        assert expected == WRITE_CONSENT_ACTIONS


# ─────────────────────────────────────────────
# consent_expiry_service - loop logic
# ─────────────────────────────────────────────


class TestConsentExpiryLoop:
    @pytest.mark.asyncio
    async def test_loop_calls_run_once_and_stops_after_iteration(self):
        """Test that consent_expiry_loop calls run_once and handles success."""
        call_count = 0

        async def fake_run_once() -> int:
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise asyncio.CancelledError("stop loop for test")
            return 5

        from app.services.consent_expiry_service import consent_expiry_loop
        import asyncio

        # Run the loop but stop it after 2 iterations via CancelledError (inherits from BaseException in Python 3.8+)
        with pytest.raises(asyncio.CancelledError):
            await consent_expiry_loop(interval_seconds=0, run_once=fake_run_once)

        assert call_count == 2

    @pytest.mark.asyncio
    async def test_loop_handles_exception_in_run_once(self):
        """Test that consent_expiry_loop gracefully handles errors and continues."""
        import asyncio
        call_count = 0

        async def fake_run_once_with_error() -> int:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Transient failure")
            raise asyncio.CancelledError("stop loop for test")

        from app.services.consent_expiry_service import consent_expiry_loop

        with pytest.raises(asyncio.CancelledError):
            await consent_expiry_loop(interval_seconds=0, run_once=fake_run_once_with_error)

        # Both iterations executed (first errored, second stopped loop)
        assert call_count == 2
