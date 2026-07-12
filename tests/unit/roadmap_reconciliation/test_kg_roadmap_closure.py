import json
import shutil
from pathlib import Path

from scripts.knowledge_graph.audit_kg_roadmap_closure import audit
from scripts.roadmap_reconciliation.verify_kg_roadmap_closure import evaluate


def test_kg_roadmap_closure_authority_is_valid_before_capture():
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["kg_roadmap_closure_recorded"] is True


def test_kg_roadmap_closure_audit_sees_all_kg_items():
    result = audit(Path("."))
    assert result["authority_valid"] is True
    assert result["kg_item_count"] == 10
    assert result["missing_records"] == []
    assert result["incomplete_records"] == []
    assert result["kg008_non_required_check_pytest_path_caveat_visible"] is True


def test_closure_matrix_preserves_kgact001_before_kg8():
    matrix = json.loads(Path("docs/roadmap/knowledge_graph/kg_roadmap_closure_matrix.json").read_text())
    ids = [row["kg_id"] for row in matrix["kg_items"]]
    assert ids == ["KG-0", "KG-1", "KG-2", "KG-3", "KG-4", "KG-5", "KG-6", "KG-7", "KG-ACT-001", "KG-8"]


def test_missing_kg8_record_breaks_authority(tmp_path):
    src = Path(".")
    dst = tmp_path / "repo"
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", ".venv", "node_modules", "__pycache__"))
    (dst / "docs/roadmap/knowledge_graph/kg_008_post_switch_optimisation_scale_review_record.json").unlink()
    result = evaluate(dst)
    assert result["authority_valid"] is False
    assert any("KG-8" in error for error in result["errors"])
