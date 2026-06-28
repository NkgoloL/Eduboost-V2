from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAPTURE_PATH = ROOT / "scripts/technical_audit/capture_branch_protection_evidence.py"
VERIFY_PATH = ROOT / "scripts/technical_audit/verify_merge_readiness_authority.py"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_branch_protection_evaluator_accepts_classic_protection() -> None:
    module = _load(CAPTURE_PATH)
    result = module.evaluate_branch_protection(
        target_branch="master",
        branch_payload={"name": "master"},
        classic_payload={"url": "https://api.github.test/protection"},
        rulesets_payload=[],
    )
    assert result["branch_protection_claimed"] is True
    assert result["mechanism"] == "classic_branch_protection"


def test_branch_protection_evaluator_accepts_active_ruleset() -> None:
    module = _load(CAPTURE_PATH)
    result = module.evaluate_branch_protection(
        target_branch="master",
        branch_payload={"name": "master"},
        classic_payload={"available": False},
        rulesets_payload=[
            {
                "id": 123,
                "name": "protect master",
                "target": "branch",
                "enforcement": "active",
                "conditions": {"ref_name": {"include": ["refs/heads/master"], "exclude": []}},
                "rules": [{"type": "required_status_checks"}],
            }
        ],
    )
    assert result["branch_protection_claimed"] is True
    assert result["mechanism"] == "active_branch_rulesets"
    assert result["active_matching_rulesets"][0]["signals"]["requires_status_checks"] is True


def test_branch_protection_evaluator_rejects_unprotected_branch() -> None:
    module = _load(CAPTURE_PATH)
    result = module.evaluate_branch_protection(
        target_branch="master",
        branch_payload={"name": "master"},
        classic_payload={"available": False},
        rulesets_payload=[{"id": 1, "target": "branch", "enforcement": "evaluate"}],
    )
    assert result["branch_protection_claimed"] is False
    assert result["mechanism"] == "none"


def test_merge_readiness_verifier_accepts_claimed_record(tmp_path: Path, monkeypatch) -> None:
    module = _load(VERIFY_PATH)
    monkeypatch.chdir(tmp_path)
    raw = tmp_path / "docs/release-evidence/technical-audit/phase-09-hosted-ci/raw"
    result_path = raw / "branch_protection_result_master.json"
    _write_json(
        result_path,
        {
            "schema_version": 1,
            "target_branch": "master",
            "branch_protection_claimed": True,
            "mechanism": "classic_branch_protection",
            "release_readiness_claimed": False,
            "runtime_kg_implementation_claimed": False,
        },
    )
    sums = tmp_path / "docs/release-evidence/technical-audit/phase-09-hosted-ci/SHA256SUMS.txt"
    sums.parent.mkdir(parents=True, exist_ok=True)
    sums.write_text(f"{_sha(result_path)}  {result_path.as_posix()}\n", encoding="utf-8")
    record = tmp_path / "docs/roadmap/execution/technical_audit_remediation/hosted_ci_authority_record.json"
    _write_json(
        record,
        {
            "schema_version": 1,
            "slice": "TA-PHASE-09-HOSTED-CI-RUN-EVIDENCE",
            "head_sha": "a" * 40,
            "target_branch": "master",
            "hosted_ci_run_claimed": True,
            "hosted_ci_status": "completed",
            "hosted_ci_conclusion": "success",
            "branch_protection_claimed": True,
            "branch_protection_evidence": result_path.as_posix(),
            "branch_protection_mechanism": "classic_branch_protection",
            "merge_readiness_authorised": True,
            "sha256sums": sums.as_posix(),
            "release_readiness_claimed": False,
            "runtime_kg_implementation_claimed": False,
        },
    )
    outcome = module.verify_record(record)
    assert outcome["valid"] is True, outcome


def test_merge_readiness_verifier_rejects_missing_branch_protection(tmp_path: Path) -> None:
    module = _load(VERIFY_PATH)
    record = tmp_path / "record.json"
    _write_json(
        record,
        {
            "schema_version": 1,
            "slice": "TA-PHASE-09-HOSTED-CI-RUN-EVIDENCE",
            "head_sha": "a" * 40,
            "hosted_ci_run_claimed": True,
            "hosted_ci_status": "completed",
            "hosted_ci_conclusion": "success",
            "branch_protection_claimed": False,
            "merge_readiness_authorised": False,
            "sha256sums": str(tmp_path / "missing.txt"),
        },
    )
    outcome = module.verify_record(record)
    assert outcome["valid"] is False
    assert any("branch_protection_claimed" in error for error in outcome["errors"])
