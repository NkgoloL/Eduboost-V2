from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFY_PATH = ROOT / "scripts" / "roadmap_reconciliation" / "verify_rr001_atlas_phase_status_reconciliation.py"


def _load_verify_module():
    spec = importlib.util.spec_from_file_location("verify_rr001", VERIFY_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase_status_register_is_superseded_not_blocking():
    text = (ROOT / "docs" / "roadmap" / "PHASE_STATUS_REGISTER.md").read_text(encoding="utf-8")
    assert "RR-001 Atlas phase status reconciliation" in text
    assert "Supersession notice" in text
    assert "not the current implementation queue" in text
    assert "| Overall programme | **Reconciliation in progress** |" not in text
    assert "| Controlled beta | Blocked |" not in text


def test_rr001_matrix_classifies_all_atlas_phases_as_historical_or_superseded():
    matrix = json.loads(
        (ROOT / "docs" / "roadmap" / "reconciliation" / "rr_001_atlas_phase_status_matrix.json").read_text(
            encoding="utf-8"
        )
    )
    phases = matrix["atlas_phases"]
    assert {str(item["phase"]) for item in phases} == {str(i) for i in range(9)}
    assert all(item["release_authority"] is False for item in phases)
    assert all(
        item["current_classification"] in {"historical_atlas_record", "superseded_by_rr_register"}
        for item in phases
    )
    assert matrix["next_work_source"] == "docs/roadmap/reconciliation/outstanding_work_register.md"


def test_rr001_record_preserves_safety_boundaries():
    record = json.loads(
        (ROOT / "docs" / "roadmap" / "reconciliation" / "rr_001_atlas_phase_status_record.json").read_text(
            encoding="utf-8"
        )
    )
    assert record["rr_id"] == "RR-001"
    assert record["atlas_phase_register_reconciled"] is True
    assert record["next_work_must_cite_rr_id"] is True
    assert record["production_release_authorised"] is False
    assert record["deployment_authorised"] is False
    assert record["public_beta_authorised"] is False
    assert record["runtime_kg_implementation_claimed"] is False


def test_verify_rr001_passes():
    module = _load_verify_module()
    result = module.verify()
    assert result["valid"] is True, result["errors"]
    assert result["next_work_must_cite_rr_id"] is True
