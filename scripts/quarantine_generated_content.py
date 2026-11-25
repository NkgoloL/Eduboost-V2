#!/usr/bin/env python3
"""Quarantine generated learner content while retaining byte-exact source snapshots."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = (
    ROOT / "data/generated/items",
    ROOT / "data/generated/lessons",
    ROOT / "data/generated/assessment_blueprints",
    ROOT / "data/generated/study_plans",
)
LEGACY_ITEM_BANK = ROOT / "data/caps/grade4_maths_item_bank.json"
SNAPSHOT_ROOT = ROOT / "data/quarantine/generated_content_2026-11-23/originals"
MANIFEST = ROOT / "data/quarantine/generated_content_2026-11-23/manifest.json"
ROW_KEYS = {"items", "lessons", "blueprints", "weekly_template", "topic_sequence", "remediation_mappings", "extension_mappings"}
SYNTHETIC_REVIEWERS = {"00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000002"}
REASON = (
    "Quarantined pending root-cause review and independent educator approval. "
    "Existing approval labels are not evidence of human review."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unsupported_approval(row: dict[str, Any], *, legacy_bank: bool) -> bool:
    status = row.get("review_status")
    reviewer = str(row.get("reviewer_id") or "")
    if status == "approved":
        # All artifacts under data/generated are quarantined regardless of any
        # prior label. The legacy authored bank is narrowed to unsupported claims.
        return True if not legacy_bank else (
            reviewer in SYNTHETIC_REVIEWERS or not reviewer or row.get("source") == "llm_generated"
        )
    return status == "human_reviewed" and (not reviewer or reviewer in SYNTHETIC_REVIEWERS)


def downgrade(value: Any, *, legacy_bank: bool = False) -> int:
    changed = 0
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if key in ROW_KEYS and isinstance(child, list):
                for row in child:
                    if not isinstance(row, dict):
                        continue
                    if _unsupported_approval(row, legacy_bank=legacy_bank):
                        row["review_status"] = "ai_generated"
                        row["reviewer_id"] = None
                        row["reviewed_at"] = None
                        changed += 1
                    row["quarantine_status"] = "quarantined"
                    row["quarantine_reason"] = REASON
                continue
            if isinstance(child, (dict, list)):
                changed += downgrade(child, legacy_bank=legacy_bank)
        if _unsupported_approval(value, legacy_bank=legacy_bank):
            value["review_status"] = "ai_generated"
            value["reviewer_id"] = None
            value["reviewed_at"] = None
            changed += 1
        if any(key in value for key in ("weekly_template", "topic_sequence", "remediation_mappings")):
            value["quarantine_status"] = "quarantined"
            value["quarantine_reason"] = REASON
    elif isinstance(value, list):
        for child in value:
            changed += downgrade(child, legacy_bank=legacy_bank)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="preserve originals and rewrite artifacts")
    args = parser.parse_args()
    paths = sorted(
        {path for directory in TARGET_DIRS if directory.exists() for path in directory.rglob("*.json")}
        | ({LEGACY_ITEM_BANK} if LEGACY_ITEM_BANK.exists() else set())
    )
    prior = {}
    if MANIFEST.exists():
        prior = {
            entry["path"]: entry
            for entry in json.loads(MANIFEST.read_text(encoding="utf-8")).get("artifacts", [])
        }
    entries = []
    for path in paths:
        rel = str(path.relative_to(ROOT))
        current_raw = path.read_bytes()
        transformed = json.loads(current_raw)
        changed = downgrade(transformed, legacy_bank=(path == LEGACY_ITEM_BANK))
        if changed == 0 and "study_plans" not in path.parts and path != LEGACY_ITEM_BANK and rel not in prior:
            continue
        rewritten = (json.dumps(transformed, ensure_ascii=False, indent=2) + "\n").encode()
        backup = SNAPSHOT_ROOT / path.relative_to(ROOT)
        existing = prior.get(rel)
        if backup.exists():
            original_hash = sha256(backup.read_bytes())
            if existing and existing.get("original_sha256") != original_hash:
                raise RuntimeError(f"Manifest/snapshot hash mismatch for {path}")
            original_bytes = len(backup.read_bytes())
        else:
            original_hash = sha256(current_raw)
            original_bytes = len(current_raw)
        entries.append({
            "path": rel,
            "original_sha256": original_hash,
            "quarantined_sha256": sha256(rewritten),
            "original_bytes": original_bytes,
            "records_downgraded": changed if changed else (existing or {}).get("records_downgraded", 0),
        })
        if args.apply:
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                shutil.copy2(path, backup)
            if sha256(backup.read_bytes()) != original_hash:
                raise RuntimeError(f"Snapshot hash mismatch for {path}")
            if current_raw != rewritten:
                path.write_bytes(rewritten)
    manifest = {
        "schema_version": "1.0",
        "created_at": (
            json.loads(MANIFEST.read_text(encoding="utf-8")).get("created_at")
            if MANIFEST.exists() else datetime.now(timezone.utc).isoformat()
        ),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "applied" if args.apply else "preview",
        "reason": REASON,
        "source_files": len(entries),
        "records_downgraded": sum(entry["records_downgraded"] for entry in entries),
        "artifacts": entries,
    }
    if args.apply:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in ("status", "source_files", "records_downgraded")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
