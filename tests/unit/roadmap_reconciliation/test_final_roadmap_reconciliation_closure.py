from __future__ import annotations

import json
from pathlib import Path

from scripts.roadmap_reconciliation.verify_final_roadmap_reconciliation_closure import evaluate


def test_final_closure_authority_is_valid_before_capture() -> None:
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["all_reconciled_rr_items_addressed"] is True


def test_final_closure_record_is_pending_before_capture() -> None:
    record = json.loads(Path("docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_record.json").read_text())
    assert record["final_roadmap_reconciliation_closure_recorded"] is True
    assert record["new_rr_items_introduced"] is False
    assert record["production_release_authorised"] is False


def test_final_closure_matrix_has_all_rr_items() -> None:
    matrix = json.loads(Path("docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_matrix.json").read_text())
    ids = [item["rr_id"] for item in matrix["items"]]
    assert ids == [f"RR-{i:03d}" for i in range(1, 19)]


def test_final_closure_report_preserves_boundaries() -> None:
    text = Path("docs/roadmap/reconciliation/final_roadmap_reconciliation_closure.md").read_text()
    assert "not be treated as `RR-019`" in text
    assert "Production release authorised: false" in text
    assert "Runtime KG implementation claimed: false" in text


def test_rr018_final_flag_is_present() -> None:
    record = json.loads(Path("docs/roadmap/reconciliation/rr_018_trustworthy_beta_product_quality_record.json").read_text())
    assert record["all_reconciled_rr_items_addressed_through_rr018"] is True
