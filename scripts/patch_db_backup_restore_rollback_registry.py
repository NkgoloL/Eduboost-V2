#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.db_backup_restore_rollback_evidence import ACCEPTED, write_status  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def replace_or_append(text: str, item_id: str, block: str) -> str:
    if "findings:" not in text:
        text = "findings:\n"
    marker = f"  - id: {item_id}"
    start = text.find(marker)
    if start < 0:
        return text.rstrip() + "\n" + block
    end = text.find("\n  - id:", start + 1)
    if end < 0:
        return text[:start] + block
    return text[:start] + block + text[end + 1:]


def main() -> int:
    run_drill = os.getenv("DB_ROLLBACK_RUN_DRILL") == "1" or os.getenv("DB_ROLLBACK_ACCEPT") == "1"
    status = write_status(run_drill=run_drill)
    accepted = status["status"] == ACCEPTED

    proof = "runtime-passing" if accepted else "not-proven"
    blocker = "none" if accepted else "backup restore rollback drill proof required"
    ready = "true" if accepted else "false"
    blocks = "false" if accepted else "true"
    run_url = status["github_run"]["run_url"] if accepted else "null"
    run_id = status["github_run"]["run_id"] if accepted else "null"
    dump_hash = status["dump_sha256"] if accepted else "null"
    commit = status["current_commit"] if accepted else "null"
    verified_by = status["verified_by"] if accepted else "null"
    date_verified = status["date_verified"] if accepted else "null"

    block = f"""  - id: DB-ROLLBACK-001
    title: Backup restore rollback runtime evidence
    severity: P0
    gate: 6
    owner: backend
    implementation_batch: code_3311_3350
    proof_status: {proof}
    proof_command: make db-backup-restore-rollback-release-check
    evidence_file: docs/release/db_backup_restore_rollback_evidence_status.md
    evidence_url: {run_url}
    run_id: {run_id}
    source_table_count: {status["source_table_count"]}
    restore_table_count: {status["restore_table_count"]}
    dump_sha256: {dump_hash}
    dump_size_bytes: {status["dump_size_bytes"]}
    last_verified_commit: {commit}
    verified_by: {verified_by}
    date_verified: {date_verified}
    closure_blocker: {blocker}
    release_ready: {ready}
    blocks_beta: {blocks}
    external_dependency: true
"""

    repair = f"""  - id: DB-ROLLBACK-001R
    title: Backup restore rollback evidence repair
    severity: P0
    gate: 6
    owner: backend
    implementation_batch: code_3311_3350
    proof_status: {proof}
    proof_command: make db-backup-restore-rollback-release-check
    evidence_file: docs/release/db_backup_restore_rollback_evidence_status.md
    evidence_url: {run_url}
    run_id: {run_id}
    source_table_count: {status["source_table_count"]}
    restore_table_count: {status["restore_table_count"]}
    dump_sha256: {dump_hash}
    last_verified_commit: {commit}
    closure_blocker: {blocker}
    release_ready: {ready}
    blocks_beta: {blocks}
    external_dependency: true
"""

    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    text = replace_or_append(text, "DB-ROLLBACK-001", block)
    text = replace_or_append(text, "DB-ROLLBACK-001R", repair)
    REGISTRY.write_text(text, encoding="utf-8")
    print("Updated DB-ROLLBACK-001 and DB-ROLLBACK-001R registry entries")

    if os.getenv("DB_ROLLBACK_ACCEPT") == "1" and not accepted:
        print("DB backup/restore/rollback evidence is not accepted; blockers:")
        for item in status["blockers"]:
            print(f"- {item}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
