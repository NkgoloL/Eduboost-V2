from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFIER_PATH = ROOT / "scripts/audit_remediation/verify_hosted_ci_merge_readiness_evidence.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_hosted_ci_merge_readiness_evidence", VERIFIER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _make_bundle(tmp_path: Path, *, claimed: bool = True, conclusion: str = "success", ci_head: str = "abc123") -> Path:
    evidence = tmp_path / "evidence"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    head = "abc123"
    _write_json(raw / "branch_state.json", {"branch": "test", "head_sha": head, "clean_worktree_before_collection": True})
    _write_json(raw / "prior_gate_evidence_summary.json", {"valid": True, "checks": {"backend_fast": {"valid": True}}})
    _write_json(raw / "hosted_ci_status.json", {
        "remote_ci_run_claimed": claimed,
        "conclusion": conclusion,
        "head_sha": ci_head,
        "workflow": "CI",
        "run_id": 123,
    })
    _write_json(raw / "merge_readiness_result.json", {
        "valid": claimed and conclusion == "success" and ci_head == head,
        "remote_ci_run_claimed": claimed,
        "release_readiness_claimed": False,
        "runtime_kg_implementation_claimed": False,
    })
    entries = []
    for item in sorted(raw.glob("*.json")):
        entries.append(f"{_sha(item)}  {item.name}\n")
    (raw / "SHA256SUMS.txt").write_text("".join(entries), encoding="utf-8")
    index = "# Evidence\n\n- Status: Hosted CI merge-readiness passed\n- Release readiness claimed: false\n"
    (evidence / "evidence_index.md").write_text(index, encoding="utf-8")
    (evidence / "evidence_index.sha256").write_text(f"{_sha(evidence / 'evidence_index.md')}  evidence_index.md\n", encoding="utf-8")
    return evidence


def test_phase09_evidence_verifier_accepts_matching_hosted_ci_success(tmp_path: Path) -> None:
    module = _load_verifier()
    evidence = _make_bundle(tmp_path)
    result = module.verify_evidence_dir(evidence)
    assert result["valid"] is True, result


def test_phase09_evidence_verifier_rejects_unclaimed_remote_ci(tmp_path: Path) -> None:
    module = _load_verifier()
    evidence = _make_bundle(tmp_path, claimed=False, conclusion="not_claimed", ci_head=None)  # type: ignore[arg-type]
    result = module.verify_evidence_dir(evidence)
    assert result["valid"] is False
    assert any("remote_ci_run_claimed" in err for err in result["errors"])


def test_phase09_evidence_verifier_rejects_head_mismatch(tmp_path: Path) -> None:
    module = _load_verifier()
    evidence = _make_bundle(tmp_path, ci_head="different")
    result = module.verify_evidence_dir(evidence)
    assert result["valid"] is False
    assert any("head_sha" in err for err in result["errors"])


def test_phase09_authority_assets_are_present() -> None:
    required = [
        "scripts/audit_remediation/verify_hosted_ci_merge_readiness_authority.py",
        "scripts/audit_remediation/collect_hosted_ci_merge_readiness_evidence.sh",
        "scripts/audit_remediation/verify_hosted_ci_merge_readiness_evidence.py",
        "docs/roadmap/execution/technical_audit_remediation/09_hosted_ci_merge_readiness_authority.md",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel
