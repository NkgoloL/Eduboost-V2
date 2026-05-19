#!/usr/bin/env python3
"""
scripts/rename_metaphor_layers.py
-----------------------------------
Inventories (and optionally renames) old metaphor-layer terminology in active
source code.  Metaphor names belong only in product/storytelling docs.

Metaphor → domain name mapping
--------------------------------
    executive      → auth
    judiciary      → popia
    fourth_estate  → observability
    ether          → core  (or modules depending on context)

Usage
-----
    # Inventory only (dry run):
    python scripts/rename_metaphor_layers.py

    # Update checked-in inventory baseline:
    python scripts/rename_metaphor_layers.py --update-baseline

    # Apply renames in place:
    python scripts/rename_metaphor_layers.py --apply

    # Inventory a specific directory:
    python scripts/rename_metaphor_layers.py --root app/

Exit codes
----------
    0  No active-code references found (or all renamed)
    1  References found in --dry-run mode
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Directories that contain active engineering code
ACTIVE_DIRS = ["app", "tests", "scripts", "alembic"]
BASELINE_PATH = Path("docs/architecture/metaphor_layer_inventory_baseline.json")

# Directories where metaphor language is acceptable (product / storytelling docs)
ALLOWED_DIRS = ["docs/product", "docs/storytelling", "phases"]

# Metaphor → canonical domain name mapping
RENAME_MAP: dict[str, str] = {
    "executive": "auth",
    "judiciary": "popia",
    "fourth_estate": "observability",
    "ether": "core",
}

# File extensions to scan
EXTENSIONS = {".py", ".md", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh"}

# Build a single pattern that matches any metaphor name as a word boundary
_pattern = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in RENAME_MAP) + r")\b",
    re.IGNORECASE,
)


def is_in_allowed_dir(path: Path) -> bool:
    parts = path.parts
    return any(allowed in parts for allowed in [p.split("/")[-1] for p in ALLOWED_DIRS])


def scan(root: Path) -> list[tuple[Path, int, str, str]]:
    """Return list of (file, lineno, matched_term, line_text)."""
    hits: list[tuple[Path, int, str, str]] = []
    for active_dir in ACTIVE_DIRS:
        search_root = root / active_dir
        if not search_root.exists():
            continue
        for path in search_root.rglob("*"):
            if path.suffix not in EXTENSIONS or not path.is_file():
                continue
            if is_in_allowed_dir(path):
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for lineno, line in enumerate(lines, start=1):
                for match in _pattern.finditer(line):
                    hits.append((path, lineno, match.group(0).lower(), line.rstrip()))
    return hits


def _hit_key(hit: tuple[Path, int, str, str]) -> str:
    path, lineno, term, line_text = hit
    return f"{path}:{lineno}:{term}:{line_text}"


def _load_baseline() -> set[str]:
    if not BASELINE_PATH.exists():
        return set()
    try:
        payload = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    keys: set[str] = set()
    for item in payload.get("references", []):
        hit = (
            Path(str(item["file"])),
            int(item["line"]),
            str(item["term"]),
            str(item["text"]),
        )
        keys.add(_hit_key(hit))
    return keys


def _write_baseline(hits: list[tuple[Path, int, str, str]]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "description": (
            "Known active-code metaphor terminology references. The CI gate "
            "fails only for references not listed here, so this baseline must "
            "shrink as naming is moved to canonical domain language."
        ),
        "references": [
            {
                "file": str(path),
                "line": lineno,
                "term": term,
                "text": line_text,
            }
            for path, lineno, term, line_text in sorted(hits, key=_hit_key)
        ],
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def apply_renames(root: Path) -> int:
    """Replace metaphor names in-place. Returns count of files modified."""
    modified = 0
    for active_dir in ACTIVE_DIRS:
        search_root = root / active_dir
        if not search_root.exists():
            continue
        for path in search_root.rglob("*"):
            if path.suffix not in EXTENSIONS or not path.is_file():
                continue
            if is_in_allowed_dir(path):
                continue
            try:
                original = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            def _replace(m: re.Match) -> str:
                term = m.group(0).lower()
                replacement = RENAME_MAP.get(term, term)
                # Preserve original casing style (all-caps, title, lower)
                if m.group(0).isupper():
                    return replacement.upper()
                if m.group(0).istitle():
                    return replacement.title()
                return replacement

            updated = _pattern.sub(_replace, original)
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                print(f"  Renamed: {path}")
                modified += 1
    return modified


def main() -> int:
    apply = "--apply" in sys.argv
    update_baseline = "--update-baseline" in sys.argv
    root_arg = next((a for a in sys.argv[1:] if a.startswith("--root=")), None)
    root = Path(root_arg.split("=", 1)[1]) if root_arg else Path(".")

    if apply:
        print("Applying metaphor → domain renames...\n")
        count = apply_renames(root)
        print(f"\nDone. {count} file(s) modified.")
        return 0

    # Dry-run inventory
    hits = scan(root)
    if update_baseline:
        _write_baseline(hits)
        print(f"Wrote {BASELINE_PATH} with {len(hits)} reference(s)")
        return 0

    if not hits:
        print("✓ No metaphor-layer references found in active code.")
        return 0

    baseline = _load_baseline()
    new_hits = [hit for hit in hits if _hit_key(hit) not in baseline]
    baseline_count = len(hits) - len(new_hits)
    if baseline_count and not new_hits:
        print(
            "Metaphor layer inventory passed "
            f"({baseline_count} known reference(s) accounted for by baseline)."
        )
        return 0

    print(f"\n{'='*60}")
    print(f"  Metaphor Layer Inventory — {len(new_hits)} new reference(s) found")
    if baseline_count:
        print(f"  Baseline accounted for {baseline_count} known reference(s)")
    print(f"  Run with --apply to rename in-place.")
    print(f"{'='*60}\n")
    print(f"  {'Metaphor term':<20} {'Canonical name':<20}")
    print(f"  {'-'*18}   {'-'*18}")
    for k, v in RENAME_MAP.items():
        print(f"  {k:<20} → {v:<20}")
    print()

    prev_file = None
    for path, lineno, term, line_text in new_hits:
        if path != prev_file:
            print(f"  {path}")
            prev_file = path
        canonical = RENAME_MAP.get(term, term)
        print(f"    line {lineno:>4}: [{term} → {canonical}]  {line_text[:80]}")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
