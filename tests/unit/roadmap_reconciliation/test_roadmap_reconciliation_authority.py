from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_outstanding_register_contains_required_ids() -> None:
    text = Path("docs/roadmap/reconciliation/outstanding_work_register.md").read_text(encoding="utf-8")
    for i in range(1, 19):
        assert f"RR-{i:03d}" in text
    assert "The next implementation slice must cite" in text
    assert "Security posture deepening" in text
    assert "Privacy / POPIA completion" in text


def test_canonical_sources_inventory_points_to_existing_files() -> None:
    payload = json.loads(Path("docs/roadmap/reconciliation/canonical_roadmap_sources.json").read_text(encoding="utf-8"))
    sources = payload["canonical_sources"]
    assert len(sources) >= 7
    for source in sources:
        assert Path(source["path"]).exists(), source["path"]
    assert "Outstanding Work Register" in payload["new_work_rule"]


def test_phase_18_to_21_are_classified_as_auxiliary_governance() -> None:
    text = Path("docs/roadmap/reconciliation/phase_18_to_21_governance_classification.md").read_text(encoding="utf-8")
    assert "auxiliary beta-operations governance" in text
    assert "not canonical roadmap phases" in text
    assert "automatic Phase 22+ creation" in text


def test_placeholder_record_is_fail_closed() -> None:
    payload = json.loads(Path("docs/roadmap/reconciliation/roadmap_reconciliation_record.json").read_text(encoding="utf-8"))
    assert payload["status"] == "roadmap_reconciliation_pending"
    assert payload["roadmap_reconciliation_recorded"] is False
    assert payload["production_release_authorised"] is False
    assert payload["public_beta_authorised"] is False
    assert payload["runtime_kg_implementation_claimed"] is False


def test_verify_module_rejects_placeholder_record() -> None:
    module = _load_module(Path("scripts/roadmap_reconciliation/verify_roadmap_reconciliation.py"))
    result = module.verify_record(Path("docs/roadmap/reconciliation/roadmap_reconciliation_record.json"))
    assert result["valid"] is False
    assert result["errors"]
