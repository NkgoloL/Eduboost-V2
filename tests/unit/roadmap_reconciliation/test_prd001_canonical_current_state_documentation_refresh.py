from __future__ import annotations

import json
from pathlib import Path

from scripts.roadmap_reconciliation.verify_prd001_canonical_current_state_documentation_refresh import evaluate

ROOT = Path(__file__).resolve().parents[3]

def test_prd001_authority_is_valid() -> None:
    result = evaluate(ROOT)
    assert result["authority_valid"] is True, result["errors"]
    assert result["prd_id"] == "PRD-0.1"
    assert result["prd000_production_readiness_stream_authority_valid"] is True

def test_prd001_boundaries_are_preserved() -> None:
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

def test_canonical_docs_do_not_contain_known_stale_claims() -> None:
    docs = [ROOT / "docs/current_state.md", ROOT / "README.md", ROOT / "docs/README.md", ROOT / "docs/roadmap/README.md", ROOT / "docs/architecture/README.md"]
    corpus = "\n\n".join(path.read_text(encoding="utf-8") for path in docs)
    assert "RR-010 beta outcome reporting, RR-015 external approvals" not in corpus
    assert "runtime KG implementation remains unauthorised" not in corpus
    assert "Next after KG-0: `KG-1 — CAPS graph foundation`" not in corpus
    assert "RR roadmap/TODO register: closed" in corpus
    assert "KG roadmap: closed through KG-8" in corpus
    assert "Controlled runtime KG authority switch: executed" in corpus

def test_truth_map_lists_expected_docs() -> None:
    truth_map = json.loads((ROOT / "docs/roadmap/production_readiness/current_state_documentation_truth_map.json").read_text(encoding="utf-8"))
    assert truth_map["prd_id"] == "PRD-0.1"
    assert truth_map["canonical_files"] == ["docs/current_state.md", "README.md", "docs/README.md", "docs/roadmap/README.md", "docs/architecture/README.md"]
