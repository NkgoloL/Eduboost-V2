from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid
import json
from pathlib import Path

from scripts.roadmap_reconciliation.verify_prd002_historical_report_stale_source_quarantine import evaluate

ROOT = Path(__file__).resolve().parents[3]

def test_prd002_authority_is_valid() -> None:
    result = evaluate(ROOT)
    assert_archival_or_current_valid(result)
    assert result["prd_id"] == "PRD-0.2"
    assert result["prd001_canonical_current_state_documentation_refresh_valid"] is True

def test_prd002_boundaries_are_preserved() -> None:
    result = evaluate(ROOT)
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["new_kg_slice_authorised"] is False
    assert result["prd1_implementation_authorised"] is False

def test_historical_report_is_marked_superseded() -> None:
    report = (ROOT / "docs/reports/EduBoost_V2_True_Status_Report_2026-07-03.md").read_text(encoding="utf-8")
    assert "Historical report — superseded" in report
    assert "status: historical-superseded" in report
    assert "quarantined_by: PRD-0.2" in report
    assert "live roadmap" in report
    assert not (ROOT / "docs/reports/EduBoost_V2_True_Status_Report_2026-07-03.md:Zone.Identifier").exists()

def test_stale_source_quarantine_register_lists_current_authority() -> None:
    qreg = json.loads((ROOT / "docs/reports/stale_source_quarantine_register.json").read_text(encoding="utf-8"))
    assert qreg["register_id"] == "STALE-SOURCE-QUARANTINE-REGISTER"
    assert qreg["quarantined_sources"][0]["source_of_truth"] is False
    assert qreg["quarantined_sources"][0]["status"] == "historical_superseded"
    assert "docs/current_state.md" in qreg["current_authority_sources"]
    assert qreg["windows_zone_identifier_policy"]["tracked_zone_identifier_files_allowed"] is False
