#!/usr/bin/env python3
"""Score a diagnostic item bank without creating human-review approvals."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.diagnostics.quality_scorer import QualityScorer

DEFAULT_INPUT = ROOT / "data" / "caps" / "grade4_maths_item_bank.json"
DEFAULT_TOPIC_MAP = ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json"
DEFAULT_MANIFEST_DIR = ROOT / "data" / "generated" / "run_manifests"


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
    stats = {"ai_generated": 0, "requires_review": 0, "failed": 0, "total": 0}

    for item in seed.get("items", []):
        stats["total"] += 1
        scored = scorer.score(item)
        errors = validator.validate_all(scored)
        score = float(scored.get("quality_score") or 0.0)
        item.update(scored)
        if errors:
            stats["failed"] += 1
            item.setdefault("validation_errors", [{"rule": e.rule, "detail": e.detail} for e in errors])
        # Automated checks never constitute human approval, including candidates
        # that fail validation and items previously carrying a synthetic label.
        item["review_status"] = "ai_generated"
        item["reviewer_id"] = None
        item["reviewed_at"] = None
        if errors:
            continue
        # Automated quality/safety checks are not educator review. Never let
        # this script create an approval claim or synthetic reviewer identity.
        item["reviewer_id"] = None
        item["reviewed_at"] = None
        if not errors and item.get("safety_passed") is True and score >= args.threshold:
            item["review_status"] = "ai_generated"
            stats["ai_generated"] += 1
        elif not errors and score >= args.review_threshold:
            item["review_status"] = "ai_generated"
            stats["requires_review"] += 1
        else:
            item["review_status"] = "ai_generated"
            stats["failed"] += 1

    manifest = {
        "operation": "score_item_bank_no_approval",
        "input": str(args.input),
        "threshold": args.threshold,
        "review_threshold": args.review_threshold,
        "dry_run": args.dry_run,
        "stats": stats,
    }
    if not args.dry_run:
        from datetime import datetime, timezone
        seed["generated_at"] = datetime.now(timezone.utc).isoformat()
        args.input.write_text(json.dumps(seed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        args.manifest_dir.mkdir(parents=True, exist_ok=True)
        (args.manifest_dir / "auto_approve_item_bank.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
