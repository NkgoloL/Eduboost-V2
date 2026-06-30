#!/usr/bin/env python3
"""
scripts/assign_irt_params.py
─────────────────────────────────────────────────────────────────────────────
Phase 3: IRT Parameter Assignment + Quality Scoring (P3-09, P3-10, P3-11)

After human review (P3-05 – P3-07), this script:
  1. Reads all approved items from the seed JSON
  2. Assigns initial IRT parameters based on difficulty_band calibration
  3. Computes per-item quality_score
  4. Writes updated items back to the seed file

Initial IRT defaults (refined after first 100 diagnostic sessions):
  - a (discrimination) = 1.0 for all items
  - c (guessing)       = 0.25 for MCQ (4 options → 1/4 baseline)
  - b (difficulty)     = midpoint of band range (from difficulty_b field or band mapping)

Usage:
    python scripts/assign_irt_params.py
    python scripts/assign_irt_params.py --caps-ref 4.M.1.1 --dry-run
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.modules.diagnostics.quality_scorer import QualityScorer
from app.modules.diagnostics.irt_params import assign_irt_params

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("assign_irt_params")

TOPIC_MAP_PATH = REPO_ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json"
DEFAULT_INPUT  = REPO_ROOT / "data" / "caps" / "grade4_maths_item_bank.json"

def load_json(path: Path) -> dict:
    if not path.exists():
        logger.error("File not found: %s", path)
        sys.exit(2)
    with open(path) as f:
        return json.load(f)


def save_json(data: dict, path: Path) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info("Saved → %s", path)



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assign IRT parameters and quality scores to approved items."
    )
    parser.add_argument("--input",    type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--caps-ref", help="Only process a specific CAPS ref")
    parser.add_argument("--status",   default="approved", help="Filter by review_status")
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    seed     = load_json(args.input)
    topic_map = load_json(TOPIC_MAP_PATH) if TOPIC_MAP_PATH.exists() else {}
    scorer    = QualityScorer(topic_map=topic_map)

    items       = seed.get("items", [])
    updated_ids = set()
    counts      = {"irt_assigned": 0, "scored": 0, "skipped": 0}

    for idx, item in enumerate(items):
        # Apply filters
        if args.caps_ref and item.get("caps_ref") != args.caps_ref:
            counts["skipped"] += 1
            continue
        if args.status and item.get("review_status") != args.status:
            counts["skipped"] += 1
            continue

        # Assign IRT
        updated_item = assign_irt_params(item)
        counts["irt_assigned"] += 1

        # Score
        scored_item = scorer.score(updated_item)
        counts["scored"] += 1

        items[idx] = scored_item
        updated_ids.add(scored_item.get("item_id"))

        logger.debug(
            "  %s  b=%.2f  a=%.2f  c=%.2f  quality=%.3f",
            str(scored_item.get("item_id", "?"))[:8],
            scored_item.get("difficulty_b", 0),
            scored_item.get("discrimination_a", 0),
            scored_item.get("guessing_c", 0),
            scored_item.get("quality_score", 0),
        )

    # Report
    processed = [i for i in items if i.get("item_id") in updated_ids]
    scorer.report(processed)

    print(f"{'='*55}")
    print(f"  IRT Assignment {'[DRY RUN] ' if args.dry_run else ''}Summary")
    print(f"{'='*55}")
    print(f"  Items processed:   {counts['irt_assigned']}")
    print(f"  Scores computed:   {counts['scored']}")
    print(f"  Items skipped:     {counts['skipped']}")

    if not args.dry_run:
        seed["items"] = items
        save_json(seed, args.input)
        print(f"  Saved to:          {args.input}")
    else:
        print("  [DRY RUN] No file changes written.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
