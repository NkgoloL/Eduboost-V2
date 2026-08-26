from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.roadmap_reconciliation.verify_prd000_production_readiness_stream_authority import evaluate


def _copy_repo(tmp_path: Path) -> Path:
    root = Path.cwd()
    work = tmp_path / "repo"
    for rel in [
        "docs/roadmap/reconciliation",
        "docs/roadmap/knowledge_graph",
        "docs/roadmap/production_readiness",
    ]:
        src = root / rel
        dst = work / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
    return work


def test_prd000_authority_valid_before_capture(tmp_path: Path) -> None:
    work = _copy_repo(tmp_path)
    record_path = work / "docs/roadmap/production_readiness/prd_000_production_readiness_stream_authority_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "production_readiness_stream_authority_recorded": False,
            "evidence_owner": None,
            "evidence_captured_at": None,
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = evaluate(work)
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["production_readiness_stream_authority_recorded"] is False
    assert result["prd0_sequence_registered"] is True
    assert result["production_readiness_sequence_registered"] is True
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["new_kg_slice_authorised"] is False


def test_prd000_captured_record_required_for_valid(tmp_path: Path) -> None:
    work = _copy_repo(tmp_path)
    record_path = work / "docs/roadmap/production_readiness/prd_000_production_readiness_stream_authority_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update({
        "production_readiness_stream_authority_recorded": True,
        "rr_closure_valid": True,
        "kg_closure_valid": True,
        "known_caveats_carried_forward": True,
        "evidence_owner": "Nkgolo Lebelo",
        "evidence_captured_at": "2026-07-06T00:00:00+00:00",
    })
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = evaluate(work)
    assert result["authority_valid"] is True
    assert result["production_readiness_stream_authority_recorded"] is True


def test_prd000_rejects_release_boundary_authorisation(tmp_path: Path) -> None:
    work = _copy_repo(tmp_path)
    register_path = work / "docs/roadmap/production_readiness/production_readiness_register.json"
    register = json.loads(register_path.read_text(encoding="utf-8"))
    register["authority_boundaries"]["production_release_authorised"] = True
    register_path.write_text(json.dumps(register, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = evaluate(work)
    assert result["authority_valid"] is False
    assert any("production_release_authorised" in error for error in result["errors"])


def test_prd000_rejects_missing_kg_runtime_truth(tmp_path: Path) -> None:
    work = _copy_repo(tmp_path)
    register_path = work / "docs/roadmap/production_readiness/production_readiness_register.json"
    register = json.loads(register_path.read_text(encoding="utf-8"))
    register["authority_boundaries"]["authority_switch_executed"] = False
    register_path.write_text(json.dumps(register, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = evaluate(work)
    assert result["authority_valid"] is False
    assert any("authority_switch_executed" in error for error in result["errors"])
