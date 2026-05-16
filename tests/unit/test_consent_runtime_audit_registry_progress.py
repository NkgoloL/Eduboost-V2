from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.audit_canonicalization_registry import ready_candidates, unsafe_candidates
from app.services.consent_runtime_compatibility import normalize_consent_runtime_operation, probe_constructor


ROOT = Path(__file__).resolve().parents[2]


def test_consent_runtime_operation_normalizes_to_audit_event():
    operation = normalize_consent_runtime_operation(
        action="consent.revoked",
        actor_id="guardian-1",
        learner_id="learner-1",
    )
    event = operation.to_audit_event()
    assert event["action"] == "consent.revoked"
    assert event["resource_id"] == "learner-1"
    assert event["metadata"]["operation_type"] == "write"


def test_constructor_probe_handles_missing_module_gracefully():
    probe = probe_constructor("missing.module.Service")
    assert probe.importable is False
    assert probe.class_found is False
    assert probe.error


def test_audit_registry_has_ready_non_destructive_candidates():
    assert ready_candidates()
    assert unsafe_candidates() == ()


def test_slice_checks_and_progress_report_run():
    for command in [
        [sys.executable, "scripts/check_consent_runtime_compatibility_slice.py"],
        [sys.executable, "scripts/check_audit_canonicalization_registry.py"],
        [sys.executable, "scripts/generate_backend_consolidation_progress_report.py"],
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


def test_makefile_contains_progress_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "consent-runtime-compatibility-slice-check:" in text
    assert "audit-canonicalization-registry-check:" in text
    assert "backend-consolidation-progress-report:" in text
    assert "backend-implementation-367-370-full-check:" in text
