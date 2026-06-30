from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.audit_migration_orchestrator import allowed_candidate_names, build_audit_migration_event
from app.services.consent_runtime_orchestrator import build_consent_runtime_audit_payload, summarize_consent_runtime_surfaces
from app.services.deep_readiness_route_contracts import public_deep_readiness_checks, unsafe_public_checks


ROOT = Path(__file__).resolve().parents[2]


def test_audit_migration_orchestrator_builds_adapter_ready_event():
    candidate = allowed_candidate_names()[0]
    event = build_audit_migration_event(
        candidate_name=candidate,
        action="audit.test",
        actor_id="tester",
        learner_id="learner-1",
    )
    payload = event.to_event_input().to_canonical_payload()
    assert payload["action"] == "audit.test"
    assert payload["resource_id"] == "learner-1"
    assert payload["payload"]["migration_candidate"] == candidate


def test_consent_runtime_orchestrator_builds_audit_payload():
    payload = build_consent_runtime_audit_payload(
        action="consent.status.read",
        actor_id="guardian-1",
        learner_id="learner-1",
    )
    assert payload["resource_type"] == "learner_consent"
    assert payload["metadata"]["operation_type"] == "read"
    assert payload["metadata"]["consent_runtime_orchestrated"] is True


def test_consent_runtime_summary_is_stable():
    summary = summarize_consent_runtime_surfaces()
    assert summary.write_operation_supported is True
    assert summary.read_operation_supported is True
    assert summary.importable_surfaces >= 0


def test_deep_readiness_catalogue_has_no_unsafe_public_checks():
    assert public_deep_readiness_checks()
    assert unsafe_public_checks() == ()


def test_check_and_report_scripts_run():
    for command in [
        [sys.executable, "scripts/check_backend_implementation_371_375.py"],
        [sys.executable, "scripts/generate_backend_implementation_371_375_report.py"],
    ]:
        result = subprocess.run(
            command,
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert result.returncode == 0, result.stdout


def test_makefile_contains_371_375_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-implementation-371-375-check:" in text
    assert "backend-implementation-371-375-report:" in text
    assert "backend-implementation-371-375-full-check:" in text
