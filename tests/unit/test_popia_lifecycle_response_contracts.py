from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_popia_adapter_contains_response_contract_normalizer():
    source = (ROOT / "app/services/popia_consent_lifecycle_adapter.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "_coerce_consent_record" in source
    assert "ConsentRecord" in source
    assert "fallback_state=ConsentState.DENIED" in source
    assert "fallback_state=ConsentState.WITHDRAWN" in source


def test_popia_router_declares_consent_record_response_models():
    source = (ROOT / "app/api_v2_routers/popia.py").read_text(encoding="utf-8")
    assert '@router.post("/consent/grant", response_model=ConsentRecord)' in source
    assert '@router.post("/consent/deny", response_model=ConsentRecord)' in source
    assert '@router.post("/consent/withdraw", response_model=ConsentRecord)' in source
    assert '@router.post("/consent/renew", response_model=ConsentRecord)' in source


def test_popia_lifecycle_response_checker_runs():
    import os
    if os.environ.get("IN_SUBPROCESS_CHECK"):
        return
    env = os.environ.copy()
    env["IN_SUBPROCESS_CHECK"] = "1"
    result = subprocess.run(
        [sys.executable, "scripts/check_popia_lifecycle_response_contract.py"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
