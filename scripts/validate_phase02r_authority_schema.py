#!/usr/bin/env python3
"""Statically validate Gate 2R.1 models, migration, and append-only controls."""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "app/models/curriculum_authority.py"
MIGRATION = ROOT / "alembic/versions/20260616_1200_phase02r_authority_controls.py"

REQUIRED_COLUMNS = {
    "curriculum_sources": {
        "source_id", "publisher", "authority_tier", "official_source_url", "document_title",
        "document_type", "country", "curriculum", "phase", "grade", "subject", "language",
        "created_by", "created_at",
    },
    "curriculum_source_versions": {
        "source_version_id", "source_id", "version_label", "publication_date", "effective_from",
        "effective_to", "supersedes_source_version_id", "copyright_owner", "original_sha256",
        "original_object_uri", "media_type", "file_size_bytes", "retrieved_at", "retrieval_metadata",
        "created_by", "created_at",
    },
    "curriculum_rights_decisions": {
        "rights_decision_id", "source_version_id", "decision_status", "may_store_original",
        "may_extract", "may_embed", "may_use_for_retrieval", "may_include_in_model_prompt",
        "may_generate_derivatives", "may_translate", "may_publish_translation",
        "may_show_excerpt_to_educator", "may_show_excerpt_to_learner", "may_redistribute",
        "may_use_commercially", "may_use_for_model_training", "requires_attribution", "conditions",
        "decision_basis", "evidence_uri", "reviewed_by", "reviewed_at", "expires_at",
        "supersedes_decision_id", "idempotency_key", "created_at",
    },
    "curriculum_inventory_versions": {
        "inventory_version_id", "inventory_code", "version_number", "curriculum", "grade", "subject",
        "delivery_languages", "terms", "strands", "status", "manifest_sha256",
        "supersedes_inventory_version_id", "frozen_by", "frozen_at", "created_by", "created_at",
    },
    "curriculum_inventory_items": {
        "inventory_item_id", "inventory_version_id", "requirement_code", "requirement_type",
        "authority_tier", "term", "strand", "language", "source_id", "source_version_id", "item_status",
        "absence_reason", "evidence", "reviewed_by", "reviewed_at", "created_at",
    },
    "curriculum_review_decisions": {
        "review_decision_id", "review_domain", "subject_type", "subject_id", "decision", "reviewer_id",
        "reviewer_role", "rationale", "evidence", "supersedes_review_decision_id", "idempotency_key",
        "created_at",
    },
}
APPEND_ONLY_TABLES = set(REQUIRED_COLUMNS)


def _literal_string(node: ast.AST) -> str | None:
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError):
        return None
    return value if isinstance(value, str) else None


def model_tables() -> dict[str, set[str]]:
    tree = ast.parse(MODEL.read_text(encoding="utf-8"), filename=str(MODEL))
    tables: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        table_name: str | None = None
        columns: set[str] = set()
        for child in node.body:
            if isinstance(child, ast.Assign):
                if any(isinstance(target, ast.Name) and target.id == "__tablename__" for target in child.targets):
                    table_name = _literal_string(child.value)
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                if isinstance(child.value, ast.Call):
                    func = child.value.func
                    name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
                    if name == "mapped_column":
                        columns.add(child.target.id)
        if table_name:
            tables[table_name] = columns
    return tables


def validate() -> list[str]:
    errors: list[str] = []
    try:
        tables = model_tables()
    except (OSError, SyntaxError) as exc:
        return [f"unable to parse authority model: {exc}"]

    for table_name, columns in REQUIRED_COLUMNS.items():
        if table_name not in tables:
            errors.append(f"missing ORM table declaration: {table_name}")
            continue
        missing = columns - tables[table_name]
        if missing:
            errors.append(f"{table_name}: missing model columns {sorted(missing)}")

    try:
        migration = MIGRATION.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing migration: {MIGRATION.relative_to(ROOT)}")
        migration = ""

    if 'revision = "20260616_1200_phase02r_authority"' not in migration:
        errors.append("Phase 2R migration revision is incorrect")
    if 'down_revision = "20260615_2100_p17_reconcile"' not in migration:
        errors.append("Phase 2R migration does not follow the recorded reconciliation head")
    if "prevent_phase02r_authority_mutation" not in migration:
        errors.append("append-only trigger function is missing")
    for table_name in sorted(APPEND_ONLY_TABLES):
        if f'"{table_name}"' not in migration:
            errors.append(f"migration does not create {table_name}")
    if "_create_append_only_trigger(table_name)" not in migration:
        errors.append("migration does not apply append-only triggers to the authority-table loop")

    return errors


def main() -> int:
    errors = validate()
    if "--json" in sys.argv:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2, sort_keys=True))
    elif errors:
        print("Phase 2R authority schema validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("Phase 2R authority schema validation passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
