#!/usr/bin/env python3
"""Verify the Grade 4 Mathematics launch item-bank count."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ITEM_BANK = REPO_ROOT / "data" / "generated" / "items" / "grade4_maths_launch_item_bank.json"


def _load_items(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError(f"{path} does not contain an items array")
    return [item for item in items if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grade", type=int, default=4)
    parser.add_argument("--subject", default="mathematics")
    parser.add_argument("--minimum", type=int, default=50)
    parser.add_argument("--path", type=Path, default=DEFAULT_ITEM_BANK)
    args = parser.parse_args()

    path = args.path if args.path.is_absolute() else REPO_ROOT / args.path
    items = _load_items(path)
    matching = [
        item
        for item in items
        if int(item.get("grade", -1)) == args.grade
        and str(item.get("subject", "")).lower() == args.subject.lower()
    ]
    approved = [item for item in matching if item.get("review_status") == "approved"]

    by_topic: dict[str, int] = {}
    for item in approved:
        topic = str(item.get("topic") or item.get("caps_ref") or "unknown")
        by_topic[topic] = by_topic.get(topic, 0) + 1

    print(f"Grade {args.grade} {args.subject.title()} Item Bank")
    print(f"Source: {path.relative_to(REPO_ROOT)}")
    print(f"Total matching items: {len(matching)}")
    print(f"Approved items: {len(approved)}")
    print("By topic:")
    for topic, count in sorted(by_topic.items()):
        print(f"  - {topic}: {count}")

    if len(approved) < args.minimum:
        print(f"FAIL: approved item count {len(approved)} is below minimum {args.minimum}")
        return 1

    print(f"PASS: approved item count meets minimum {args.minimum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
