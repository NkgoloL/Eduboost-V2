#!/usr/bin/env python3
"""Create unreviewed topic-map draft envelopes for outstanding CAPS scopes."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.curriculum.build_topic_map_worklist import build_worklist

DRAFT_DIR = ROOT / "data" / "content_factory" / "topic_map_drafts"


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def draft_path(scope_id: str, *, draft_dir: Path = DRAFT_DIR) -> Path:
    return draft_dir / f"{scope_id}.json"


def build_draft(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "_meta": {
            "schema_version": "1.0.0-draft",
            "status": "draft_unreviewed",
            "generated_at": now_utc(),
            "scope_id": item["scope_id"],
            "scope": f"Grade {item['grade']} {item['subject']}",
            "suggested_runtime_topic_map_path": item["suggested_topic_map_path"],
            "source_document_ids": item["source_document_ids"],
            "source_paths": item["source_paths"],
            "source_sha256": item["source_sha256"],
            "canonical_source_urls": item["canonical_source_urls"],
            "object_store_uris": item["object_store_uris"],
            "text_extract_paths": item.get("text_extract_paths", []),
            "text_sha256": item.get("text_sha256", []),
            "outstanding_tasks": item["outstanding_tasks"],
            "review_required": True,
            "notes": "Draft envelope only. Do not move to data/caps/topic_maps or mark topic_map_approved until terms/topics/subtopics are extracted from the cited source and reviewed.",
        },
        "grade": item["grade"],
        "subject": item["subject"],
        "subject_code": item["subject_code"],
        "terms": [],
    }


def scaffold_drafts(*, commit: bool) -> dict[str, Any]:
    worklist = build_worklist()
    created: list[str] = []
    skipped: list[str] = []
    for item in worklist["items"]:
        if "extract_topic_map" not in item["outstanding_tasks"]:
            skipped.append(item["scope_id"])
            continue
        target = draft_path(item["scope_id"])
        draft = build_draft(item)
        created.append(str(target.relative_to(ROOT)))
        if commit:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "schema_version": "1.0",
        "commit": commit,
        "drafts_created": len(created),
        "draft_paths": created,
        "scopes_skipped": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="Write draft JSON files.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    payload = scaffold_drafts(commit=args.commit)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Topic-map drafts: {payload['drafts_created']} {'written' if args.commit else 'planned'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
