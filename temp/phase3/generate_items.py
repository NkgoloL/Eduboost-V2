#!/usr/bin/env python3
"""
scripts/generate_items.py
─────────────────────────────────────────────────────────────────────────────
Phase 3: Item Generation CLI (P3-01, P3-02, P3-03)

Generates diagnostic item candidates for a given CAPS reference using the
LLM gateway, runs each candidate through item_validator, and writes passing
items to the seed JSON file.

Usage:
    python scripts/generate_items.py \
        --caps-ref 4.M.1.1 \
        --n-items 60 \
        --difficulty-band moderate \
        --dry-run

    python scripts/generate_items.py \
        --caps-ref 4.M.1.2 \
        --n-items 60 \
        --output data/caps/grade4_maths_item_bank.json

Difficulty bands:
    easy        b < -1.0   (10 items target)
    moderate    -1.0 ≤ b < 0.0  (12 items target)
    on_level    0.0 ≤ b < +1.0  (12 items target)
    challenging b ≥ +1.0   (6 items target)
    mixed       Distribute across all bands (default — generates 60 candidates)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

# ---------------------------------------------------------------------------
# Path setup — allow running from repo root
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.modules.diagnostics.item_generator import ItemGenerator, ItemGenerationError
from app.modules.diagnostics.item_validator import ItemValidator, ValidationError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("generate_items")

# ---------------------------------------------------------------------------
# Difficulty band → b-parameter target ranges
# ---------------------------------------------------------------------------
DIFFICULTY_BANDS = {
    "easy":        (-3.0, -1.0, 10),   # (b_min, b_max, target_items)
    "moderate":    (-1.0,  0.0, 12),
    "on_level":    ( 0.0,  1.0, 12),
    "challenging": ( 1.0,  3.0,  6),
    "mixed":       (-3.0,  3.0, 40),   # Full range, 40 approved target
}

SEED_SCHEMA_HEADER = {
    "schema_version": "1.0",
    "generated_at": None,          # filled at write time
    "caps_ref_metadata": {},       # filled from topic map
    "items": [],
}

TOPIC_MAP_PATH = REPO_ROOT / "data" / "caps" / "caps_topic_map_grade4_maths.json"
DEFAULT_OUTPUT  = REPO_ROOT / "data" / "caps" / "grade4_maths_item_bank.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_topic_map() -> dict:
    if not TOPIC_MAP_PATH.exists():
        logger.error("Topic map not found at %s", TOPIC_MAP_PATH)
        sys.exit(1)
    with open(TOPIC_MAP_PATH) as f:
        return json.load(f)


def load_or_init_seed(output_path: Path) -> dict:
    if output_path.exists():
        with open(output_path) as f:
            data = json.load(f)
        logger.info("Loaded existing seed file: %d items", len(data.get("items", [])))
        return data
    seed = dict(SEED_SCHEMA_HEADER)
    seed["items"] = []
    return seed


def save_seed(seed: dict, output_path: Path) -> None:
    seed["generated_at"] = datetime.now(timezone.utc).isoformat()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(seed, f, indent=2, default=str)
    logger.info("Saved seed file → %s (%d items)", output_path, len(seed["items"]))


def item_exists(seed: dict, item_id: str) -> bool:
    return any(i.get("item_id") == item_id for i in seed["items"])


def count_approved(seed: dict, caps_ref: str) -> int:
    return sum(
        1 for i in seed["items"]
        if i.get("caps_ref") == caps_ref and i.get("review_status") == "approved"
    )


def count_generated(seed: dict, caps_ref: str) -> int:
    return sum(1 for i in seed["items"] if i.get("caps_ref") == caps_ref)


def build_difficulty_schedule(band: str, n_items: int) -> list[tuple[str, float, float]]:
    """
    Returns a list of (band_name, b_min, b_max) tuples, one per item to generate.
    For 'mixed', distributes across bands according to target ratios.
    """
    if band != "mixed":
        b_min, b_max, _ = DIFFICULTY_BANDS[band]
        return [(band, b_min, b_max)] * n_items

    # Mixed: follow the 10/12/12/6 distribution scaled to n_items
    schedule = []
    targets = [
        ("easy",       -3.0, -1.0, 10),
        ("moderate",   -1.0,  0.0, 12),
        ("on_level",    0.0,  1.0, 12),
        ("challenging", 1.0,  3.0,  6),
    ]
    total_target = sum(t[3] for t in targets)
    for band_name, b_min, b_max, t_count in targets:
        count = max(1, round(n_items * t_count / total_target))
        schedule.extend([(band_name, b_min, b_max)] * count)

    return schedule[:n_items]


# ---------------------------------------------------------------------------
# Main generation loop
# ---------------------------------------------------------------------------

async def run_generation(
    caps_ref: str,
    n_items: int,
    difficulty_band: str,
    output_path: Path,
    dry_run: bool,
    max_retries: int,
    retry_delay: float,
) -> None:
    topic_map = load_topic_map()
    if caps_ref not in topic_map.get("topics", {}):
        logger.error(
            "CAPS ref '%s' not found in topic map. Available: %s",
            caps_ref,
            list(topic_map["topics"].keys()),
        )
        sys.exit(1)

    topic_data = topic_map["topics"][caps_ref]
    seed = load_or_init_seed(output_path)

    # Update metadata
    seed.setdefault("caps_ref_metadata", {})[caps_ref] = {
        "topic":    topic_data["topic"],
        "subtopic": topic_data["subtopic"],
        "skill":    topic_data["skill"],
        "term":     topic_data["term"],
        "grade":    topic_data["grade"],
    }

    generator = ItemGenerator()
    validator  = ItemValidator(topic_map=topic_map)

    difficulty_schedule = build_difficulty_schedule(difficulty_band, n_items)

    stats = {
        "attempted": 0,
        "passed_validator": 0,
        "failed_validator": 0,
        "failed_generation": 0,
        "skipped_duplicate": 0,
        "written": 0,
    }

    logger.info(
        "Starting generation: caps_ref=%s  n=%d  band=%s  dry_run=%s",
        caps_ref, n_items, difficulty_band, dry_run,
    )

    for idx, (band_name, b_min, b_max) in enumerate(difficulty_schedule, start=1):
        stats["attempted"] += 1
        attempt = 0

        while attempt < max_retries:
            attempt += 1
            try:
                item = await generator.generate(
                    caps_ref=caps_ref,
                    topic_data=topic_data,
                    difficulty_band=band_name,
                    b_min=b_min,
                    b_max=b_max,
                )

                # Validate
                validator.validate(item)

                # Duplicate guard
                if item_exists(seed, item["item_id"]):
                    logger.debug("Duplicate item_id %s — regenerating", item["item_id"])
                    stats["skipped_duplicate"] += 1
                    item["item_id"] = str(uuid4())   # assign fresh UUID

                stats["passed_validator"] += 1

                if not dry_run:
                    seed["items"].append(item)
                    stats["written"] += 1

                logger.info(
                    "[%d/%d] ✅  %s  band=%-11s  b=%.2f  id=%s",
                    idx, n_items, caps_ref, band_name,
                    item.get("difficulty_b", 0.0), item["item_id"][:8],
                )
                break   # success — move to next item

            except ValidationError as exc:
                stats["failed_validator"] += 1
                logger.warning(
                    "[%d/%d] ❌  Validation failed (attempt %d/%d): %s",
                    idx, n_items, attempt, max_retries, exc,
                )
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)

            except ItemGenerationError as exc:
                stats["failed_generation"] += 1
                logger.warning(
                    "[%d/%d] ⚠️  Generation error (attempt %d/%d): %s",
                    idx, n_items, attempt, max_retries, exc,
                )
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * 2)

        else:
            logger.error(
                "[%d/%d] Gave up after %d attempts for band=%s",
                idx, n_items, max_retries, band_name,
            )

    # Final save
    if not dry_run:
        save_seed(seed, output_path)

    # Report
    approved = count_approved(seed, caps_ref)
    generated_total = count_generated(seed, caps_ref)

    print("\n" + "=" * 60)
    print(f"  Generation Report — {caps_ref}")
    print("=" * 60)
    print(f"  Attempted:          {stats['attempted']}")
    print(f"  Passed validator:   {stats['passed_validator']}")
    print(f"  Failed validator:   {stats['failed_validator']}")
    print(f"  Failed generation:  {stats['failed_generation']}")
    print(f"  Written to seed:    {stats['written']}")
    print(f"  Total in seed:      {generated_total}  (approved: {approved})")
    print(f"  Target (approved):  {topic_data.get('launch_target', 40)}")
    pass_rate = (
        stats["passed_validator"] / stats["attempted"] * 100
        if stats["attempted"] else 0
    )
    print(f"  Pass rate:          {pass_rate:.1f}%")
    status = "✅ TARGET MET" if approved >= topic_data.get("launch_target", 40) else "⚠️  BELOW TARGET"
    print(f"  Status:             {status}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate CAPS diagnostic items via LLM and validate them."
    )
    parser.add_argument(
        "--caps-ref", required=True,
        help="CAPS reference code, e.g. 4.M.1.1",
    )
    parser.add_argument(
        "--n-items", type=int, default=60,
        help="Number of item candidates to generate (default: 60)",
    )
    parser.add_argument(
        "--difficulty-band",
        choices=list(DIFFICULTY_BANDS.keys()),
        default="mixed",
        help="Difficulty band or 'mixed' to distribute across all bands (default: mixed)",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="Path to the item bank seed JSON file",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Generate and validate items but do not write to seed file",
    )
    parser.add_argument(
        "--max-retries", type=int, default=3,
        help="Max LLM retries per item on failure (default: 3)",
    )
    parser.add_argument(
        "--retry-delay", type=float, default=1.5,
        help="Seconds to wait between retries (default: 1.5)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(
        run_generation(
            caps_ref=args.caps_ref,
            n_items=args.n_items,
            difficulty_band=args.difficulty_band,
            output_path=args.output,
            dry_run=args.dry_run,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay,
        )
    )


if __name__ == "__main__":
    main()
