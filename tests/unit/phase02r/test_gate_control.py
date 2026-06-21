from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/phase02r_gate_control.py"
spec = importlib.util.spec_from_file_location("phase02r_gate_control", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_current_control_authorises_gate_2r1_only() -> None:
    assert module.validate_state(expected_authorised_gate="2R.1") == []


def test_premature_gate_2r2_transition_is_rejected(tmp_path, monkeypatch) -> None:
    import json

    control = json.loads(module.CONTROL_PATH.read_text(encoding="utf-8"))
    control.update({
        "approved_gate": "2R.1",
        "authorised_next_gate": "2R.2",
        "approval_commit_sha": "a" * 40,
        "parent_evidence_commit_sha": "b" * 40,
        "remote_branch_sha": "a" * 40,
    })
    path = tmp_path / "control.json"
    path.write_text(json.dumps(control), encoding="utf-8")
    monkeypatch.setattr(module, "CONTROL_PATH", path)

    approvals_path = tmp_path / "approvals.json"
    approvals_path.write_text(json.dumps({
        "phase": "02R",
        "gate": "2R.1",
        "decision": "pending",
        "decisions": []
    }), encoding="utf-8")
    monkeypatch.setattr(module, "APPROVALS_2R1_PATH", approvals_path)

    errors = module.validate_state()
    assert any("post-transition statement" in error for error in errors)
    assert any("Gate 2R.1 approvals do not authorise Gate 2R.2" in error for error in errors)
    assert any("Gate 2R.1 approvals missing roles" in error for error in errors)


def test_placeholder_commit_references_are_rejected(tmp_path, monkeypatch) -> None:
    import json

    control = json.loads(module.CONTROL_PATH.read_text(encoding="utf-8"))
    control["approval_commit_sha"] = "approval_commit_is_authority"
    path = tmp_path / "control.json"
    path.write_text(json.dumps(control), encoding="utf-8")
    monkeypatch.setattr(module, "CONTROL_PATH", path)

    errors = module.validate_state(expected_authorised_gate="2R.1")
    assert "control.approval_commit_sha must be a real 40-character lowercase Git SHA" in errors
