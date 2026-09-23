#!/usr/bin/env python3
"""Check documentation review intervals against last_reviewed front matter."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path
import sys

from doc_utils import iter_markdown, load_source_of_truth_paths, parse_front_matter, relpath

def parse_date(value: object) -> date | None:
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip().strip("'\"")
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(cleaned[:10], fmt).date()
        except ValueError:
            pass
    return None

def main() -> int:
    parser = argparse.ArgumentParser(description="Check documentation review intervals.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--canonical-only", action="store_true", help="Only fail on canonical source-of-truth documents")
    parser.add_argument("--max-overdue-days", type=int, default=0, help="Tolerance for days overdue")
    parser.add_argument("--reference-date", type=str, default=None, help="Reference date YYYY-MM-DD (defaults to today)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    canonical_paths = set(load_source_of_truth_paths(root))

    ref_date: date = date.today()
    if args.reference_date:
        parsed_ref = parse_date(args.reference_date)
        if parsed_ref is not None:
            ref_date = parsed_ref

    overdue_canonical: list[tuple[str, int, date, date]] = []
    overdue_other: list[tuple[str, int, date, date]] = []
    total_checked = 0

    paths_to_check = canonical_paths if args.canonical_only else list(iter_markdown(root))

    for path in sorted(paths_to_check):
        if not path.is_file():
            continue
        rel = relpath(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_front_matter(text)
        if not meta:
            continue

        lr_date = parse_date(meta.get("last_reviewed"))
        interval_val = meta.get("review_interval_days")
        try:
            interval = int(interval_val) if interval_val is not None else None
        except (ValueError, TypeError):
            interval = None

        if lr_date and interval:
            total_checked += 1
            due_date = lr_date + timedelta(days=interval)
            if ref_date > due_date:
                days_overdue = (ref_date - due_date).days
                if days_overdue > args.max_overdue_days:
                    entry = (rel, days_overdue, lr_date, due_date)
                    if path in canonical_paths:
                        overdue_canonical.append(entry)
                    else:
                        overdue_other.append(entry)

    print(f"Checked review intervals for {total_checked} document(s) as of {ref_date}.")

    if overdue_canonical:
        print(f"\n[FAIL] {len(overdue_canonical)} CANONICAL document(s) have EXPIRED review dates:")
        for rel, days, lr, due in overdue_canonical:
            print(f"  - {rel}: reviewed {lr}, due {due} ({days} days overdue)")

    if overdue_other:
        print(f"\n[INFO] {len(overdue_other)} non-canonical document(s) have expired review dates (tracked in stale_documentation_review_register.md).")

    if overdue_canonical:
        return 1

    print("\nCanonical documentation review date check passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
