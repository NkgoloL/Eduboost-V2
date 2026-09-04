from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path

from app.services.backend_adapter_wiring_service import InMemoryAuditSink, record_all_safe_candidates
from app.services.backend_first_wiring_candidates import build_all_safe_candidate_payloads, safe_wiring_candidates, unsafe_wiring_candidates


ROOT = Path(__file__).resolve().parents[2]


def test_safe_wiring_candidates_are_non_destructive():
    candidates = safe_wiring_candidates()
    assert candidates
    assert all(not candidate.destructive for candidate in candidates)
    assert all(not candidate.requires_route_change for candidate in candidates)
    assert unsafe_wiring_candidates() == ()


def test_safe_candidate_payloads_build():
    payloads = build_all_safe_candidate_payloads()
    assert payloads
    assert all(payload.payload["action"] for payload in payloads)
    assert all(payload.payload["resource_id"] == "learner-candidate" for payload in payloads)


def test_build_candidate_payload_error_branches():
    import pytest
    from dataclasses import replace
    from app.services.backend_first_wiring_candidates import (
        WiringArea,
        WiringCandidate,
        build_candidate_payload,
        safe_wiring_candidates,
    )

    base = safe_wiring_candidates()[0]

    # 1. destructive
    with pytest.raises(ValueError, match="destructive candidate is blocked"):
        build_candidate_payload(replace(base, destructive=True))

    # 2. requires_route_change
    with pytest.raises(ValueError, match="route-change candidate is blocked"):
        build_candidate_payload(replace(base, requires_route_change=True))

    # 3. not approved_for_wiring
    with pytest.raises(ValueError, match="candidate not approved for wiring"):
        build_candidate_payload(replace(base, approved_for_wiring=False))

    # 4. audit candidate missing candidate_name
    audit_base = next(c for c in safe_wiring_candidates() if c.area == WiringArea.AUDIT)
    with pytest.raises(ValueError, match="audit candidate missing candidate_name"):
        build_candidate_payload(replace(audit_base, candidate_name=None))

    # 5. unknown wiring area
    fake_area = "UNKNOWN_AREA"
    with pytest.raises(ValueError, match="unknown wiring area"):
        build_candidate_payload(replace(base, area=fake_area))



def test_adapter_wiring_service_records_to_in_memory_sink():
    async def run():
        sink = InMemoryAuditSink()
        results = await record_all_safe_candidates(sink)
        assert len(results) == len(sink.events)
        assert all(result.recorded for result in results)
        assert all(event["resource_id"] == "learner-candidate" for event in sink.events)

    asyncio.run(run())


def test_first_wiring_candidate_scripts_run():
    for command in [
        [sys.executable, "scripts/check_backend_first_wiring_candidates.py"],
        [sys.executable, "scripts/generate_backend_first_wiring_candidates_report.py"],
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


def test_makefile_contains_391_400_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-first-wiring-candidates-check:" in text
    assert "backend-first-wiring-candidates-report:" in text
    assert "backend-implementation-391-400-full-check:" in text
