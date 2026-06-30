#!/usr/bin/env python3
"""
scripts/deduplicate_makefile_targets.py
=======================================
Detect and optionally remove duplicate target definitions from the Makefile.

Background (Recommendation 4)
------------------------------
Five targets are defined twice in Makefile, causing the second definition
to silently override the first.  This is a real maintenance hazard because
the effective recipe depends on declaration order, and future additions may
accidentally restore the wrong copy.

Duplicates confirmed by the 2026-05-12 technical assessment:
  - observability-ops-check          (two definitions)
  - post-deploy-staging-smoke-checklist-check (two definitions)
  - release-candidate-tag-manifest-check      (two definitions)
  - release-state-snapshot-check              (two definitions)
  - staging-smoke-evidence-manifest-check     (two definitions)

Usage
-----
  # Detect only (exit 1 if duplicates found):
  python3 scripts/deduplicate_makefile_targets.py

  # Auto-deduplicate (keep last definition, write Makefile in place):
  python3 scripts/deduplicate_makefile_targets.py --fix

  # Preview the fixed Makefile without writing:
  python3 scripts/deduplicate_makefile_targets.py --fix --dry-run

  # Keep first definition instead of last:
  python3 scripts/deduplicate_makefile_targets.py --fix --keep first

Add to CI:
  make deduplicate-check   →  python3 scripts/deduplicate_makefile_targets.py
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = REPO_ROOT / "Makefile"

# A target line looks like:  target-name:  or  target-name: dep1 dep2
TARGET_RE = re.compile(r"^([A-Za-z0-9_\-\.]+)\s*:((?!=).*)?$")


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_targets(lines: list[str]) -> dict[str, list[int]]:
    """Return {target_name: [line_indices_of_definition_header]}."""
    occurrences: dict[str, list[int]] = defaultdict(list)
    for i, line in enumerate(lines):
        m = TARGET_RE.match(line)
        if m:
            occurrences[m.group(1)].append(i)
    return occurrences


def find_duplicates(
    occurrences: dict[str, list[int]]
) -> dict[str, list[int]]:
    return {k: v for k, v in occurrences.items() if k != ".PHONY" and len(v) > 1}


# ---------------------------------------------------------------------------
# Recipe extraction
# ---------------------------------------------------------------------------

def extract_recipe_block(lines: list[str], header_line: int) -> list[int]:
    """Return the indices of the recipe lines following *header_line*.

    A recipe block ends at the next non-indented, non-empty line that
    looks like another target or a blank line followed by a new target.
    """
    block = [header_line]
    i = header_line + 1
    while i < len(lines):
        line = lines[i]
        if line.startswith("\t") or (line.strip() == ""):
            block.append(i)
            i += 1
        else:
            break
    return block


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(
    lines: list[str],
    duplicates: dict[str, list[int]],
    keep: str = "last",
) -> list[str]:
    """Return a new lines list with duplicate targets removed.

    *keep* controls which occurrence is preserved:
      'last'  – keep the final definition (matches Make's own semantics)
      'first' – keep the first definition
    """
    lines_to_remove: set[int] = set()

    for target, occurrences in duplicates.items():
        # Decide which occurrence to keep
        if keep == "last":
            occurrences[-1]
            remove_occurrences = occurrences[:-1]
        else:
            occurrences[0]
            remove_occurrences = occurrences[1:]

        for header_line in remove_occurrences:
            block = extract_recipe_block(lines, header_line)
            lines_to_remove.update(block)

    return [line for i, line in enumerate(lines) if i not in lines_to_remove]


# ---------------------------------------------------------------------------
# .PHONY sync
# ---------------------------------------------------------------------------

def sync_phony(lines: list[str]) -> list[str]:
    """Re-emit .PHONY with deduplicated, sorted target names."""
    all_targets = [
        m.group(1)
        for line in lines
        if (m := TARGET_RE.match(line))
        and not line.startswith(".PHONY")
        and not line.startswith("help")
    ]
    unique_sorted = sorted(set(all_targets))
    phony_line = f".PHONY: {' '.join(unique_sorted)}\n"

    new_lines = []
    replaced = False
    for line in lines:
        if line.startswith(".PHONY:") and not replaced:
            new_lines.append(phony_line)
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        new_lines.insert(0, phony_line)

    return new_lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Remove duplicate definitions (default: detect only).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --fix, print the result instead of writing it.",
    )
    parser.add_argument(
        "--keep",
        choices=["first", "last"],
        default="last",
        help="Which duplicate occurrence to keep (default: last, matching Make semantics).",
    )
    parser.add_argument(
        "--makefile",
        default=str(MAKEFILE),
        help=f"Path to Makefile (default: {MAKEFILE}).",
    )
    args = parser.parse_args(argv)

    makefile_path = Path(args.makefile)
    if not makefile_path.exists():
        print(f"[ERROR] Makefile not found: {makefile_path}", file=sys.stderr)
        return 1

    lines = makefile_path.read_text(encoding="utf-8").splitlines(keepends=True)
    occurrences = parse_targets(lines)
    duplicates = find_duplicates(occurrences)

    if not duplicates:
        print("[PASS] No duplicate Makefile targets found.")
        return 0

    # Report
    print(f"[{'WARN' if args.fix else 'FAIL'}] Duplicate Makefile targets detected:\n")
    for target, positions in sorted(duplicates.items()):
        line_numbers = [p + 1 for p in positions]  # 1-indexed for humans
        print(f"  {target!r:55s} → lines {line_numbers}")

    if not args.fix:
        print(
            f"\nRun with --fix to remove duplicates (keeping the {args.keep!r} "
            "definition of each)."
        )
        return 1

    # Fix
    fixed_lines = deduplicate(lines, duplicates, keep=args.keep)
    fixed_lines = sync_phony(fixed_lines)
    fixed_content = "".join(fixed_lines)

    if args.dry_run:
        print("\n--- Fixed Makefile preview (first 80 lines) ---")
        for line in fixed_content.splitlines()[:80]:
            print(line)
        print("--- (dry run – nothing written) ---")
    else:
        makefile_path.write_text(fixed_content, encoding="utf-8")
        print(
            f"\n[FIXED] Removed {sum(len(v) - 1 for v in duplicates.values())} "
            f"duplicate definition(s) from {makefile_path}."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
