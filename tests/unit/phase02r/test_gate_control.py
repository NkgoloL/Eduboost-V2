from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/phase02r_gate_control.py"
spec = importlib.util.spec_from_file_location("phase02r_gate_control", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_current_control_authorises_gate_2r1_only(tmp_path, monkeypatch) -> None:
    import json
    control = json.loads(module.CONTROL_PATH.read_text(encoding="utf-8"))
    control.update({
        "approved_gate": "2R.0",
        "authorised_next_gate": "2R.1",
        "start_approved": True,
        "approval_decision_commit_sha": "d2b243ca4a3f75e4b50a0afaed046bacabf7c7b9",
        "evidence_commit_sha": "851f3e16b83d8d1cd9b531ed29dbfe2f5b278e73",
        "transition_commit_sha": "f" * 40,
        "remote_branch_sha_at_transition": "f" * 40,
        "approved_at": "2026-06-16T15:40:33Z"
    })
    path = tmp_path / "control.json"
    path.write_text(json.dumps(control), encoding="utf-8")
    monkeypatch.setattr(module, "CONTROL_PATH", path)

    plan_path = tmp_path / "plan.md"
    plan_content = "\n".join([
        "**Status:** Gate 2R.1 in progress; Gate 2R.2 blocked",
        "**Execution authorisation:** Gate 2R.1 only",
        "**Current decision:** Gate 2R.1 is In Progress. Gate 2R.2 is Blocked."
    ])
    plan_path.write_text(plan_content, encoding="utf-8")
    monkeypatch.setattr(module, "PLAN_PATH", plan_path)
    assert module.validate_state(expected_authorised_gate="2R.1") == []


def test_premature_gate_2r2_transition_is_rejected(tmp_path, monkeypatch) -> None:
    import json

    control = json.loads(module.CONTROL_PATH.read_text(encoding="utf-8"))
    control.update({
        "approved_gate": "2R.1",
        "authorised_next_gate": "2R.2",
        "approval_decision_commit_sha": "a" * 40,
        "evidence_commit_sha": "b" * 40,
        "transition_commit_sha": "c" * 40,
        "remote_branch_sha_at_transition": "c" * 40,
    })
    path = tmp_path / "control.json"
    path.write_text(json.dumps(control), encoding="utf-8")
    monkeypatch.setattr(module, "CONTROL_PATH", path)

    approvals_path = tmp_path / "approvals.json"
    approvals_path.write_text(json.dumps({
        "phase": "02R",
        "gate": "2R.1",
        "decision": "pending",
        "evidence_source_sha": "d" * 40,
        "evidence_commit_sha": "b" * 40,
        "authorised_next_gate": None,
        "decisions": []
    }), encoding="utf-8")
    monkeypatch.setattr(module, "_approvals_path", lambda gate: approvals_path)

    evidence_index_path = tmp_path / "evidence_index.md"
    evidence_index_path.write_text("\n".join([
        "# Phase 2R Gate 2R.1 Evidence Index",
        "",
        "**Generated:** 2026-06-16T15:40:33Z",
        "**Status:** Candidate verification passed — human approval pending",
        f"**Source commit:** `{'d' * 40}`",
    ]), encoding="utf-8")
    monkeypatch.setattr(module, "_evidence_index_path", lambda gate: evidence_index_path)

    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    raw_artifact = raw_dir / "artifact.txt"
    raw_artifact.write_text("ok\n", encoding="utf-8")
    import hashlib
    (raw_dir / "SHA256SUMS.txt").write_text(
        f"{hashlib.sha256(raw_artifact.read_bytes()).hexdigest()}  artifact.txt\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "_evidence_raw_dir", lambda gate: raw_dir)

    plan_path = tmp_path / "plan.md"
    plan_path.write_text("Dummy plan without transition statements.", encoding="utf-8")
    monkeypatch.setattr(module, "PLAN_PATH", plan_path)

    errors = module.validate_state(require_approval_roles=True)
    assert any("current execution authorisation statement" in error for error in errors)
    assert any("current gate status phrase" in error for error in errors)
    assert any("Gate 2R.1 approvals do not authorise Gate 2R.2" in error for error in errors)
    assert any("Gate 2R.1 approvals missing roles" in error for error in errors)


def test_placeholder_commit_references_are_rejected(tmp_path, monkeypatch) -> None:
    import json

    control = json.loads(module.CONTROL_PATH.read_text(encoding="utf-8"))
    control["approval_decision_commit_sha"] = "approval_commit_is_authority"
    path = tmp_path / "control.json"
    path.write_text(json.dumps(control), encoding="utf-8")
    monkeypatch.setattr(module, "CONTROL_PATH", path)

    errors = module.validate_state(expected_authorised_gate="2R.1")
    assert "control.approval_decision_commit_sha must be a real 40-character lowercase Git SHA" in errors
