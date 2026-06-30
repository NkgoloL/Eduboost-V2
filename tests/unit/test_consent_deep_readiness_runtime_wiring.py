from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.first_consent_runtime_wiring import (
    build_first_consent_runtime_payload,
    load_first_consent_runtime_candidate,
    validate_first_consent_runtime_payload,
)
from app.services.first_deep_readiness_runtime_wiring import (
    build_first_deep_readiness_runtime_plan,
    load_first_deep_readiness_runtime_candidate,
    validate_first_deep_readiness_runtime_plan,
)


ROOT = Path(__file__).resolve().parents[2]


def test_first_consent_runtime_candidate_is_safe_and_valid():
    candidate = load_first_consent_runtime_candidate()
    assert candidate.id == "BCW-431-CONSENT-GRANT-PAYLOAD"
    assert candidate.destructive is False
    assert candidate.requires_table_merge is False
    assert validate_first_consent_runtime_payload(candidate) is True
    payload = build_first_consent_runtime_payload(candidate).payload
    assert payload["metadata"]["operation_type"] == "write"
    assert payload["metadata"]["runtime_wiring_candidate_id"] == candidate.id


def test_first_deep_readiness_runtime_candidate_is_read_only():
    candidate = load_first_deep_readiness_runtime_candidate()
    assert candidate.id == "BCW-435-DEEP-READINESS-READONLY"
    assert candidate.destructive is False
    assert candidate.allows_public_mutation is False
    assert validate_first_deep_readiness_runtime_plan(candidate) is True
    plan = build_first_deep_readiness_runtime_plan(candidate)
    assert plan.public_safe is True
    assert plan.mutates_state is False


def test_runtime_wiring_431_450_scripts_run():
    for command in [
        [sys.executable, "scripts/check_first_consent_and_deep_readiness_runtime_wiring.py"],
        [sys.executable, "scripts/check_runtime_wiring_no_destructive_actions.py"],
        [sys.executable, "scripts/generate_runtime_wiring_431_450_report.py"],
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


def test_makefile_contains_431_450_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "first-consent-deep-readiness-runtime-wiring-check:" in text
    assert "runtime-wiring-431-450-report:" in text
    assert "backend-implementation-431-450-full-check:" in text
