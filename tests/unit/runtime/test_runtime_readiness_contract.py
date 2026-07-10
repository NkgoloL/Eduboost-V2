from pathlib import Path

from app.core.runtime_readiness import (
    classify_database_lineage,
    load_alembic_revision_graph,
    validate_runtime_schema_contract,
)
from scripts.runtime.verify_runtime_stack_readiness import verify_contract


def _write_revision(path: Path, revision: str, down_revision: str | None) -> None:
    down = repr(down_revision) if down_revision is not None else "None"
    path.write_text(f"revision = {revision!r}\ndown_revision = {down}\n")


def test_alembic_graph_discovers_single_head(tmp_path: Path) -> None:
    _write_revision(tmp_path / "001_base.py", "001", None)
    _write_revision(tmp_path / "002_next.py", "002", "001")
    graph = load_alembic_revision_graph(tmp_path)
    assert graph.valid is True
    assert graph.single_head == "002"


def test_database_lineage_rejects_unknown_revision(tmp_path: Path) -> None:
    _write_revision(tmp_path / "001_base.py", "001", None)
    graph = load_alembic_revision_graph(tmp_path)
    result = classify_database_lineage(["20260531_1600"], graph)
    assert result["status"] == "error"
    assert "live_database_revision_unknown_to_repository" in result["reason_codes"]


def test_database_lineage_requires_exact_repository_head(tmp_path: Path) -> None:
    _write_revision(tmp_path / "001_base.py", "001", None)
    _write_revision(tmp_path / "002_next.py", "002", "001")
    graph = load_alembic_revision_graph(tmp_path)
    assert classify_database_lineage(["002"], graph)["status"] == "ok"
    assert classify_database_lineage(["001"], graph)["status"] == "error"


def test_schema_contract_requires_irt_columns_and_runtime_kg_tables() -> None:
    result = validate_runtime_schema_contract(
        present_tables={"diagnostic_items"},
        present_columns={"diagnostic_items": {"id"}},
        required_tables=("diagnostic_items", "runtime_kg_nodes"),
        required_columns={"diagnostic_items": ("irt_difficulty",)},
    )
    assert result["status"] == "error"
    assert result["missing_tables"] == ["runtime_kg_nodes"]
    assert result["missing_columns"] == {"diagnostic_items": ["irt_difficulty"]}


def test_runtime_stack_readiness_contract_is_installed() -> None:
    result = verify_contract(require_live_green=False)
    assert result["contract_valid"] is True
    assert result["valid"] is True
    assert result["runtime_baseline_green"] is False
    assert "database_lineage_and_schema" in result["checks"]["baseline_collector_contract"]["hard_gate_names"]
