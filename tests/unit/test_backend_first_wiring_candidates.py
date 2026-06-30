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
