"""Fail-closed runtime readiness helpers for PRD-11.0R restore work.

The helpers in this module are intentionally stricter than the historical
``/ready`` migration probe. A database is considered ready only when its live
``alembic_version`` value exactly matches the single repository Alembic head and
when critical runtime tables/columns exist. Unknown revisions, split heads,
missing tables, and missing IRT/runtime-KG columns are release blockers.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from sqlalchemy import text

REQUIRED_RUNTIME_TABLES: tuple[str, ...] = (
    "guardians",
    "learner_profiles",
    "assessments",
    "assessment_attempts",
    "diagnostic_items",
    "diagnostic_sessions",
    "study_plans",
    "lessons",
    "runtime_kg_graph_loads",
    "runtime_kg_nodes",
    "runtime_kg_edges",
    "runtime_kg_events",
    "ai_usage_events",
    "tutor_sessions",
    "audit_events",
)

REQUIRED_RUNTIME_COLUMNS: dict[str, tuple[str, ...]] = {
    "diagnostic_items": (
        "irt_quality_state",
        "irt_discrimination",
        "irt_difficulty",
        "irt_guessing",
    ),
    "runtime_kg_nodes": (
        "stable_code",
        "node_type",
        "label",
        "mastery_weight",
    ),
    "runtime_kg_edges": (
        "source_node_id",
        "target_node_id",
        "edge_type",
        "weight",
    ),
}

DEFAULT_ALEMBIC_VERSIONS_DIR = Path(__file__).resolve().parents[2] / "alembic" / "versions"


@dataclass(frozen=True)
class AlembicRevisionGraph:
    """Repository Alembic graph summary used by readiness checks."""

    revisions: frozenset[str]
    referenced_down_revisions: frozenset[str]
    heads: tuple[str, ...]
    version_files: tuple[str, ...]

    @property
    def single_head(self) -> str | None:
        return self.heads[0] if len(self.heads) == 1 else None

    @property
    def valid(self) -> bool:
        return bool(self.revisions) and len(self.heads) == 1


def _extract_assignment(module: ast.Module, name: str) -> Any:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
    raise ValueError(f"{name} assignment not found")


def _normalise_down_revision(value: Any) -> tuple[str, ...]:
    if value in (None, ""):
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (tuple, list, set)):
        return tuple(str(item) for item in value if item not in (None, ""))
    return (str(value),)


def load_alembic_revision_graph(versions_dir: Path = DEFAULT_ALEMBIC_VERSIONS_DIR) -> AlembicRevisionGraph:
    """Load repository Alembic revisions without mutating a database."""

    revisions: set[str] = set()
    referenced: set[str] = set()
    version_files: list[str] = []
    if not versions_dir.exists():
        return AlembicRevisionGraph(frozenset(), frozenset(), tuple(), tuple())
    for path in sorted(versions_dir.glob("*.py")):
        if path.name.startswith("__"):
            continue
        try:
            module = ast.parse(path.read_text())
            revision = str(_extract_assignment(module, "revision"))
            down_revision = _normalise_down_revision(_extract_assignment(module, "down_revision"))
        except Exception:
            continue
        revisions.add(revision)
        referenced.update(down_revision)
        version_files.append(path.name)
    heads = tuple(sorted(revisions - referenced))
    return AlembicRevisionGraph(
        revisions=frozenset(revisions),
        referenced_down_revisions=frozenset(referenced),
        heads=heads,
        version_files=tuple(version_files),
    )


def classify_database_lineage(live_revisions: Sequence[str], graph: AlembicRevisionGraph | None = None) -> dict[str, Any]:
    """Classify live Alembic revision state against the repository graph."""

    graph = graph or load_alembic_revision_graph()
    revisions = [revision for revision in live_revisions if revision and revision != "base"]
    unknown = [revision for revision in revisions if revision not in graph.revisions]
    exact_head = graph.valid and len(revisions) == 1 and revisions[0] == graph.single_head
    status = "ok" if exact_head and not unknown else "error"
    reasons: list[str] = []
    if not graph.valid:
        reasons.append("repository_alembic_graph_must_have_exactly_one_head")
    if not revisions:
        reasons.append("live_alembic_version_missing_or_base_only")
    if len(revisions) > 1:
        reasons.append("live_database_has_multiple_alembic_revisions")
    if unknown:
        reasons.append("live_database_revision_unknown_to_repository")
    if graph.valid and revisions and revisions != [graph.single_head]:
        reasons.append("live_database_revision_does_not_match_repository_head")
    return {
        "status": status,
        "expected_repository_heads": list(graph.heads),
        "expected_single_head": graph.single_head,
        "live_revisions": list(revisions),
        "unknown_revisions": unknown,
        "exact_repository_head": exact_head,
        "repository_revision_count": len(graph.revisions),
        "reason_codes": reasons,
    }


def validate_runtime_schema_contract(
    present_tables: Iterable[str],
    present_columns: Mapping[str, Iterable[str]],
    *,
    required_tables: Sequence[str] = REQUIRED_RUNTIME_TABLES,
    required_columns: Mapping[str, Sequence[str]] = REQUIRED_RUNTIME_COLUMNS,
) -> dict[str, Any]:
    """Validate required runtime tables/columns for beta/release paths."""

    table_set = set(present_tables)
    column_sets = {table: set(columns) for table, columns in present_columns.items()}
    missing_tables = [table for table in required_tables if table not in table_set]
    missing_columns: dict[str, list[str]] = {}
    for table, columns in required_columns.items():
        if table not in table_set:
            missing_columns[table] = list(columns)
            continue
        missing = [column for column in columns if column not in column_sets.get(table, set())]
        if missing:
            missing_columns[table] = missing
    return {
        "status": "ok" if not missing_tables and not missing_columns else "error",
        "required_tables": list(required_tables),
        "required_columns": {table: list(columns) for table, columns in required_columns.items()},
        "missing_tables": missing_tables,
        "missing_columns": missing_columns,
        "schema_contract_satisfied": not missing_tables and not missing_columns,
    }


async def fetch_live_alembic_revisions(session: Any) -> list[str]:
    result = await session.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num"))
    return [str(row[0]) for row in result.fetchall()]


async def fetch_public_schema_snapshot(session: Any) -> tuple[set[str], dict[str, set[str]]]:
    tables_result = await session.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
        )
    )
    tables = {str(row[0]) for row in tables_result.fetchall()}
    columns_result = await session.execute(
        text(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = 'public'"
        )
    )
    columns: dict[str, set[str]] = {}
    for table, column in columns_result.fetchall():
        columns.setdefault(str(table), set()).add(str(column))
    return tables, columns


async def check_database_lineage_exact(session_factory: Any) -> dict[str, Any]:
    """Async readiness check requiring live DB revision to equal repository head."""

    try:
        async with session_factory() as session:
            revisions = await fetch_live_alembic_revisions(session)
        result = classify_database_lineage(revisions)
        return {**result, "status": "ok" if result["status"] == "ok" else "error"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": exc.__class__.__name__, "reason_codes": ["alembic_lineage_query_failed"]}


async def check_runtime_schema_contract(session_factory: Any) -> dict[str, Any]:
    """Async readiness check requiring critical runtime schema objects."""

    try:
        async with session_factory() as session:
            tables, columns = await fetch_public_schema_snapshot(session)
        return validate_runtime_schema_contract(tables, columns)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": exc.__class__.__name__, "reason_codes": ["runtime_schema_contract_query_failed"]}
