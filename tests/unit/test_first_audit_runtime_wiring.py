from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path

from app.services.first_audit_runtime_wiring import (
    InMemoryFirstAuditRuntimeSink,
    build_first_audit_runtime_payload,
    load_first_audit_runtime_candidate,
    record_first_audit_runtime_candidate,
)


ROOT = Path(__file__).resolve().parents[2]


def test_selected_candidate_is_safe_and_scoped():
    candidate = load_first_audit_runtime_candidate()
    assert candidate.id == "BCW-421-AUDIT-CONSENT-GRANTED"
    assert candidate.approved_for_runtime_pr is True
    assert candidate.destructive is False
    assert candidate.requires_route_change is False
    assert candidate.requires_schema_change is False
    assert candidate.requires_database_write_in_test is False


def test_first_audit_runtime_payload_is_canonical():
    payload = build_first_audit_runtime_payload()
    assert payload.candidate_id == "BCW-421-AUDIT-CONSENT-GRANTED"
    assert payload.payload["action"] == "consent.granted"
    assert payload.payload["resource_id"] == "learner-runtime-pr"
    assert payload.payload["payload"]["runtime_wiring_candidate_id"] == "BCW-421-AUDIT-CONSENT-GRANTED"
    assert payload.payload["payload"]["first_runtime_wiring_pr"] is True


def test_first_audit_runtime_candidate_records_to_non_db_sink():
    async def run():
        sink = InMemoryFirstAuditRuntimeSink()
        result = await record_first_audit_runtime_candidate(sink)
        assert result.recorded is True
        assert len(sink.events) == 1
        assert sink.events[0]["action"] == "consent.granted"
        assert sink.events[0]["resource_id"] == "learner-runtime-pr"

    asyncio.run(run())


def test_first_audit_runtime_wiring_scripts_run():
    for command in [
        [sys.executable, "scripts/check_first_audit_runtime_wiring.py"],
        [sys.executable, "scripts/check_first_audit_runtime_wiring_no_destructive_actions.py"],
        [sys.executable, "scripts/generate_first_audit_runtime_wiring_report.py"],
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


def test_makefile_contains_421_430_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "first-audit-runtime-wiring-check:" in text
    assert "first-audit-runtime-wiring-report:" in text
    assert "backend-implementation-421-430-full-check:" in text
