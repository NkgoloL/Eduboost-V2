from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_phase03a_verifier_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/audit_remediation/verify_frontend_tooling_phase03a.py", "--json"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(completed.stdout)
    assert payload["valid"] is True


def test_services_smoke_uses_canonical_popia_routes() -> None:
    text = (ROOT / "app/frontend/__tests__/services.smoke.test.ts").read_text(encoding="utf-8")
    assert "/api/backend/popia/erasure/L1/cancel" in text
    assert "/api/backend/popia/erasure/L1/status" in text
    assert "/popia/deletion-cancel" not in text
    assert "/popia/deletion-status" not in text


def test_ai_tutor_scroll_guard_is_jsdom_safe() -> None:
    text = (ROOT / "app/frontend/src/components/learner/AiTutorChat.tsx").read_text(encoding="utf-8")
    assert 'typeof bottomRef.current?.scrollIntoView === "function"' in text
    assert "bottomRef.current.scrollIntoView" in text


def test_frontend_tooling_collector_excludes_self_mutating_check() -> None:
    text = (ROOT / "scripts/audit_remediation/collect_frontend_tooling_authority_evidence.sh").read_text(encoding="utf-8")
    assert "! -name 'frontend_tooling_evidence_check.json'" in text
    assert "write_sha_manifest" in text
