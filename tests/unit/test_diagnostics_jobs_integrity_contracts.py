from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from app.services.diagnostic_data_integrity import (
    DiagnosticIntegrityError,
    clamp_theta,
    extract_diagnostic_item_ids,
    validate_diagnostic_submission_payload,
    validate_mastery_update_payload,
    validate_theta_update,
)
from app.services.job_runtime_integrity import JobRuntimeIntegrityError, validate_arq_job_payload


ROOT = Path(__file__).resolve().parents[2]


def test_extract_diagnostic_item_ids_nested_payloads():
    payload = {"responses": [{"item_id": "item-a"}, {"nested": {"itemId": "item-b"}}]}
    assert extract_diagnostic_item_ids(payload) == ["item-a", "item-b"]


def test_diagnostic_submission_rejects_duplicates_and_unserved_items():
    with pytest.raises(DiagnosticIntegrityError):
        validate_diagnostic_submission_payload({"responses": [{"item_id": "a"}, {"item_id": "a"}]})

    with pytest.raises(DiagnosticIntegrityError):
        validate_diagnostic_submission_payload({"responses": [{"item_id": "b"}]}, served_item_ids={"a"})


def test_theta_update_validation_rejects_unsafe_values():
    assert validate_theta_update(old_theta=0.0, new_theta=1.0) == 1.0

    with pytest.raises(DiagnosticIntegrityError):
        validate_theta_update(old_theta=0.0, new_theta=99.0)

    with pytest.raises(DiagnosticIntegrityError):
        validate_mastery_update_payload({"old_theta": 0.0, "new_theta": float("inf")})

    assert clamp_theta(99.0) == 4.0


@dataclass
class RuntimeObjectRepository:
    value: str = "bad"


def test_arq_job_payload_rejects_runtime_objects():
    validate_arq_job_payload({"learner_id": "l1"}, event="consent")
    with pytest.raises(JobRuntimeIntegrityError):
        validate_arq_job_payload(RuntimeObjectRepository())


def test_diagnostics_router_contains_integrity_hooks():
    source = (ROOT / "app/api_v2_routers/diagnostics.py").read_text(encoding="utf-8")
    assert "app.services.diagnostic_data_integrity" in source
    assert (
        "# code_691_720_diagnostic_submission_integrity" in source
        or "# code_691_720_mastery_theta_integrity" in source
    )


def test_jobs_module_does_not_construct_consent_service_without_dependencies():
    jobs_source = (ROOT / "app/modules/jobs.py").read_text(encoding="utf-8")
    factory_source = (ROOT / "app/services/job_dependency_factory.py").read_text(encoding="utf-8")

    # Assert that ConsentService is not constructed directly in jobs.py
    assert "ConsentService()" not in jobs_source

    # Assert that jobs.py correctly delegates to factory/dependency layers
    assert "job_dependency_factory" in jobs_source or "run_consent_reminder_cycle" in jobs_source

    # Assert that actual database session factory and ConsentRepository are in the dependency factory
    assert "AsyncSessionLocal" in factory_source
    assert "ConsentRepository" in factory_source
