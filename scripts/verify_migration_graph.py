#!/usr/bin/env python3
"""Verify Alembic revision graph hygiene without requiring a database.

The script intentionally parses revision metadata statically so CI can catch
broken `down_revision` links even when Alembic/database dependencies are not
available in a lightweight docs or policy job.
"""
from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS_DIR = ROOT / "alembic" / "versions"
TIMESTAMPED_NAME = re.compile(r"^\d{8}_\d{4}_[a-z0-9_]+\.py$")
LEGACY_EXEMPTIONS = {
    "0001_v2_consolidated_schema.py",
    "0002_add_missing_tables.py",
    "0003_add_items_correct.py",
    "0004_add_rlhf_pipeline.py",
    "0005_seed_irt_items.py",
    "0006_v2_audit_events.py",
    "0007_caps_irt_item_bank.py",
    "0008_lesson_completion_tracking.py",
    "0009_add_subject_mastery.py",
    "3f8a2c1d9e04_add_auth_extensions.py",
    "94b628483fa7_merge_remaining_heads_0004_and_0005.py",
    "f2faf5aa12fd_merge_migration_branches.py",
    "merge_2026_05_01_merge_branches.py",
}


@dataclass(frozen=True)
class Migration:
    file: Path
    revision: str
    down_revisions: tuple[str, ...]


def _literal_assignment(tree: ast.Module, name: str):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and target.id == name:
                return ast.literal_eval(node.value)
    raise ValueError(f"missing assignment: {name}")


def load_migrations() -> list[Migration]:
    migrations: list[Migration] = []
    for file in sorted(VERSIONS_DIR.glob("*.py")):
        if file.name.startswith("_"):
            continue
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        revision = _literal_assignment(tree, "revision")
        down = _literal_assignment(tree, "down_revision")
        if down is None:
            down_revisions: tuple[str, ...] = ()
        elif isinstance(down, str):
            down_revisions = (down,)
        elif isinstance(down, tuple):
            down_revisions = tuple(str(item) for item in down)
        else:
            raise TypeError(f"{file}: unsupported down_revision value {down!r}")
        migrations.append(Migration(file=file, revision=str(revision), down_revisions=down_revisions))
    return migrations


def main() -> int:
    migrations = load_migrations()
    revisions = {migration.revision: migration for migration in migrations}
    errors: list[str] = []

    if len(revisions) != len(migrations):
        seen: set[str] = set()
        for migration in migrations:
            if migration.revision in seen:
                errors.append(f"duplicate revision id: {migration.revision}")
            seen.add(migration.revision)

    for migration in migrations:
        for down_revision in migration.down_revisions:
            if down_revision not in revisions:
                errors.append(
                    f"{migration.file.name}: down_revision {down_revision!r} does not exist"
                )
        if migration.file.name not in LEGACY_EXEMPTIONS and not TIMESTAMPED_NAME.match(migration.file.name):
            errors.append(
                f"{migration.file.name}: new migration names must match YYYYMMDD_HHMM_<short_description>.py"
            )

    children: dict[str, list[str]] = {revision: [] for revision in revisions}
    bases = []
    for migration in migrations:
        if not migration.down_revisions:
            bases.append(migration.revision)
        for down_revision in migration.down_revisions:
            children.setdefault(down_revision, []).append(migration.revision)
    heads = sorted(revision for revision, child_revisions in children.items() if not child_revisions)

    if len(bases) != 1:
        errors.append(f"expected exactly one base revision, found {bases}")
    if len(heads) != 1:
        errors.append(f"expected exactly one head revision, found {heads}")

    if errors:
        print("Migration graph validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Migration graph OK: {len(migrations)} revisions, head={heads[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
