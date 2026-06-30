#!/usr/bin/env python3
"""Fail if new learner-related functions lack a consent-gate marker."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_consent_gate_inventory import ConsentGateRow, collect_rows


ALLOWLIST_PATH = REPO_ROOT / "docs" / "security" / "popia_consent_gate_allowlist.txt"


def row_key(row: ConsentGateRow) -> str:
    return f"{row.path}::{row.function}"


def load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.exists():
        return set()
    return {
        line.strip()
        for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def missing_rows() -> list[ConsentGateRow]:
    return [row for row in collect_rows() if row.status == "missing"]


def write_current_allowlist() -> None:
    ALLOWLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(missing_rows(), key=row_key)
    lines = [
        "# POPIA consent-gate baseline allowlist.",
        "# Entries are current learner-related functions without a local consent marker.",
        "# Remove entries as explicit consent gates are added.",
        "",
    ]
    lines.extend(row_key(row) for row in rows)
    ALLOWLIST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if "--write-baseline" in argv:
        write_current_allowlist()
        print(f"Wrote {ALLOWLIST_PATH.relative_to(REPO_ROOT)}")
        return 0

    allowed = load_allowlist()
    missing = missing_rows()
    new_missing = [row for row in missing if row_key(row) not in allowed]
    stale_allowed = sorted(allowed - {row_key(row) for row in missing})

    print("POPIA consent-gate inventory check")
    print(f"- Missing consent markers: {len(missing)}")
    print(f"- Baseline allowlist entries: {len(allowed)}")
    print(f"- New unallowlisted missing markers: {len(new_missing)}")
    print(f"- Stale allowlist entries: {len(stale_allowed)}")

    if new_missing:
        print("\nNew learner-related functions without consent-gate marker:")
        for row in new_missing:
            print(f"- {row_key(row)}")
        return 1

    if stale_allowed:
        print("\nStale allowlist entries; regenerate baseline or remove them:")
        for key in stale_allowed:
            print(f"- {key}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
