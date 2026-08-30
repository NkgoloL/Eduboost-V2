"""Batch 195: Unit tests for consent_runtime_compatibility and consent_runtime_orchestrator."""
import pytest

from app.services.consent_runtime_compatibility import (
    ConsentRuntimeOperation,
    ConstructorProbe,
    normalize_consent_runtime_operation,
    probe_constructor,
    probe_known_consent_surfaces,
    CONSENT_SERVICE_CANDIDATES,
    POPIA_SERVICE_CANDIDATES,
)
from app.services.consent_runtime_orchestrator import (
    ConsentRuntimeCompatibilitySummary,
    build_consent_runtime_audit_payload,
    summarize_consent_runtime_surfaces,
)


# ─────────────────────────────────────────────
# ConsentRuntimeOperation
# ─────────────────────────────────────────────


class TestConsentRuntimeOperation:
    def test_to_audit_event_basic(self):
        op = ConsentRuntimeOperation(
            action="consent.granted",
            actor_id="guardian-1",
            learner_id="learner-1",
            operation_type="write",
        )
        event = op.to_audit_event()
        assert event["action"] == "consent.granted"
        assert event["actor_id"] == "guardian-1"
        assert event["resource_type"] == "learner_consent"
        assert event["resource_id"] == "learner-1"
        assert event["metadata"]["learner_id"] == "learner-1"
        assert event["metadata"]["operation_type"] == "write"

    def test_to_audit_event_with_metadata(self):
        op = ConsentRuntimeOperation(
            action="consent.revoked",
            actor_id="guardian-2",
            learner_id="learner-2",
            operation_type="write",
            metadata={"policy_version": "v2"},
        )
        event = op.to_audit_event()
        assert event["metadata"]["policy_version"] == "v2"

    def test_frozen_immutable(self):
        op = ConsentRuntimeOperation(
            action="consent.granted",
            actor_id="a",
            learner_id="b",
            operation_type="write",
        )
        with pytest.raises(Exception):
            op.action = "mutated"


# ─────────────────────────────────────────────
# normalize_consent_runtime_operation
# ─────────────────────────────────────────────


class TestNormalizeConsentRuntimeOperation:
    def test_read_action_inferred(self):
        op = normalize_consent_runtime_operation(
            action="consent.status.read",
            actor_id="a",
            learner_id="b",
        )
        assert op.operation_type == "read"

    def test_write_action_inferred_granted(self):
        op = normalize_consent_runtime_operation(
            action="consent.granted",
            actor_id="a",
            learner_id="b",
        )
        assert op.operation_type == "write"

    def test_write_action_inferred_revoked(self):
        op = normalize_consent_runtime_operation(
            action="consent.revoked",
            actor_id="a",
            learner_id="b",
        )
        assert op.operation_type == "write"

    def test_write_action_inferred_request(self):
        op = normalize_consent_runtime_operation(
            action="consent.erasure.request",
            actor_id="a",
            learner_id="b",
        )
        assert op.operation_type == "write"

    def test_unknown_action_type_fallback(self):
        op = normalize_consent_runtime_operation(
            action="consent.some.unknown",
            actor_id="a",
            learner_id="b",
        )
        assert op.operation_type == "unknown"

    def test_explicit_operation_type_overrides(self):
        op = normalize_consent_runtime_operation(
            action="consent.status.read",
            actor_id="a",
            learner_id="b",
            operation_type="custom_type",
        )
        assert op.operation_type == "custom_type"

    def test_extra_kwargs_merged_into_metadata(self):
        op = normalize_consent_runtime_operation(
            action="consent.granted",
            actor_id="a",
            learner_id="b",
            metadata={"base": "v"},
            extra_field="extra_val",
        )
        assert op.metadata["base"] == "v"
        assert op.metadata["extra_field"] == "extra_val"

    def test_missing_action_raises(self):
        with pytest.raises(ValueError, match="action"):
            normalize_consent_runtime_operation(action="", actor_id="a", learner_id="b")

    def test_missing_actor_id_raises(self):
        with pytest.raises(ValueError, match="actor_id"):
            normalize_consent_runtime_operation(action="a", actor_id="", learner_id="b")

    def test_missing_learner_id_raises(self):
        with pytest.raises(ValueError, match="learner_id"):
            normalize_consent_runtime_operation(action="a", actor_id="b", learner_id="")


# ─────────────────────────────────────────────
# probe_constructor
# ─────────────────────────────────────────────


class TestProbeConstructor:
    def test_probe_importable_valid_class(self):
        # ConsentService is a real class in app.services.consent_service
        probe = probe_constructor("app.services.consent_service.ConsentService")
        # Even if class not importable, should return ConstructorProbe
        assert isinstance(probe, ConstructorProbe)

    def test_probe_nonexistent_module_returns_not_importable(self):
        probe = probe_constructor("app.services.nonexistent_module_xyz.FakeClass")
        assert probe.importable is False
        assert probe.class_found is False
        assert probe.error is not None

    def test_probe_existing_module_missing_class(self):
        probe = probe_constructor("app.services.audit_service.NonExistentClass")
        assert probe.importable is True
        assert probe.class_found is False
        assert probe.error is not None

    def test_probe_returns_required_parameters(self):
        probe = probe_constructor("app.services.audit_service.AuditService")
        assert probe.importable is True
        assert probe.class_found is True
        # AuditService.__init__ has 'repository' with a default, so required params should be empty
        assert isinstance(probe.required_parameters, tuple)


class TestProbeKnownConsentSurfaces:
    def test_returns_list_of_probes(self):
        probes = probe_known_consent_surfaces()
        total_candidates = len(CONSENT_SERVICE_CANDIDATES) + len(POPIA_SERVICE_CANDIDATES)
        assert len(probes) == total_candidates
        for probe in probes:
            assert isinstance(probe, ConstructorProbe)


# ─────────────────────────────────────────────
# consent_runtime_orchestrator
# ─────────────────────────────────────────────


class TestSummarizeConsentRuntimeSurfaces:
    def test_returns_compatibility_summary(self):
        summary = summarize_consent_runtime_surfaces()
        assert isinstance(summary, ConsentRuntimeCompatibilitySummary)
        assert summary.write_operation_supported is True
        assert summary.read_operation_supported is True
        assert isinstance(summary.importable_surfaces, int)
        assert isinstance(summary.missing_surfaces, int)

    def test_importable_plus_missing_equals_total_candidates(self):
        summary = summarize_consent_runtime_surfaces()
        total = len(CONSENT_SERVICE_CANDIDATES) + len(POPIA_SERVICE_CANDIDATES)
        assert summary.importable_surfaces + summary.missing_surfaces == total


class TestBuildConsentRuntimeAuditPayload:
    def test_builds_payload_with_granted_action(self):
        payload = build_consent_runtime_audit_payload(
            action="consent.granted",
            actor_id="guardian-1",
            learner_id="learner-1",
        )
        assert payload["action"] == "consent.granted"
        assert payload["actor_id"] == "guardian-1"
        assert payload["metadata"]["consent_runtime_orchestrated"] is True
        assert payload["metadata"]["operation_type"] == "write"

    def test_builds_payload_with_read_action(self):
        payload = build_consent_runtime_audit_payload(
            action="consent.status.read",
            actor_id="guardian-2",
            learner_id="learner-2",
        )
        assert payload["metadata"]["operation_type"] == "read"

    def test_builds_payload_with_extra_metadata(self):
        payload = build_consent_runtime_audit_payload(
            action="consent.revoked",
            actor_id="a",
            learner_id="b",
            metadata={"policy": "v1"},
        )
        assert payload["metadata"]["policy"] == "v1"
        assert payload["metadata"]["consent_runtime_orchestrated"] is True

    def test_custom_operation_type_preserved(self):
        payload = build_consent_runtime_audit_payload(
            action="consent.status.read",
            actor_id="a",
            learner_id="b",
            operation_type="audit_check",
        )
        assert payload["metadata"]["operation_type"] == "audit_check"
