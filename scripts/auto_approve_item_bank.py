#!/usr/bin/env python3
"""Apply launch auto-approval policy to a diagnostic item-bank JSON file."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.diagnostics.quality_scorer import QualityScorer

DEFAULT_INPUT = ROOT / "data" / "caps" / "grade4_maths_item_bank.json"
DEFAULT_TOPIC_MAP = ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json"
DEFAULT_MANIFEST_DIR = ROOT / "data" / "generated" / "run_manifests"
AUTO_REVIEWER_ID = "00000000-0000-0000-0000-000000000002"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--topic-map", type=Path, default=DEFAULT_TOPIC_MAP)
    parser.add_argument("--threshold", type=float, default=0.85)
    parser.add_argument("--review-threshold", type=float, default=0.70)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest-dir", type=Path, default=DEFAULT_MANIFEST_DIR)
    args = parser.parse_args()

    seed = load_json(args.input)
    topic_map = load_json(args.topic_map)
    validator = ItemValidator(topic_map=topic_map)
    scorer = QualityScorer(topic_map=topic_map)
    now = datetime.now(timezone.utc).isoformat()
    stats = {"approved": 0, "review": 0, "unchanged_approved": 0, "failed": 0, "total": 0}

    for item in seed.get("items", []):
        stats["total"] += 1
        scored = scorer.score(item)
        errors = validator.validate_all(scored)
        score = float(scored.get("quality_score") or 0.0)
        item.update(scored)
        if errors:
            stats["failed"] += 1
            item.setdefault("validation_errors", [{"rule": e.rule, "detail": e.detail} for e in errors])
            continue
        if item.get("review_status") == "approved" and score < args.threshold:
            stats["unchanged_approved"] += 1
            continue
        if item.get("safety_passed") is True and score >= args.threshold:
            item["review_status"] = "approved"
            item["reviewer_id"] = item.get("reviewer_id") or AUTO_REVIEWER_ID
            item["reviewed_at"] = item.get("reviewed_at") or now
            stats["approved"] += 1
        elif score >= args.review_threshold:
            item["review_status"] = "ai_generated"
            stats["review"] += 1
        else:
            stats["failed"] += 1

    manifest = {
        "operation": "auto_approve_item_bank",
        "generated_at": now,
        "input": str(args.input),
        "threshold": args.threshold,
        "review_threshold": args.review_threshold,
        "dry_run": args.dry_run,
        "stats": stats,
    }
    if not args.dry_run:
        seed["generated_at"] = now
        args.input.write_text(json.dumps(seed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        args.manifest_dir.mkdir(parents=True, exist_ok=True)
        (args.manifest_dir / "auto_approve_item_bank.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
