#!/usr/bin/env python3
"""
scripts/inventory_services.py
------------------------------
Inventories all files in app/services/ and app/modules/, identifies duplicate
bounded-context concepts, and (optionally) injects deprecation header comments
into files that should be retired per ADR 0010.

Usage
-----
    # Print inventory report:
    python scripts/inventory_services.py

    # Inject deprecation notices into flagged files:
    python scripts/inventory_services.py --mark-deprecated

Exit codes
----------
    0  Inventory complete (with or without duplicates found)
    1  Internal error
"""

from __future__ import annotations

import sys
from pathlib import Path

SERVICES_DIR = Path("app/services")
MODULES_DIR = Path("app/modules")

# Per ADR 0010: app/services/ is canonical.
# These module-level service files are flagged as duplicates to be collapsed.
KNOWN_DUPLICATES: dict[str, str] = {
    # module file path (relative)  →  canonical service file (relative)
    "app/modules/auth/service.py":          "app/services/auth_service.py",
    "app/modules/consent/service.py":       "app/services/consent_service.py",
    "app/modules/diagnostics/service.py":   "app/services/diagnostics_service.py",
    "app/modules/lessons/service.py":       "app/services/lesson_service.py",
    "app/modules/study_plans/service.py":   "app/services/study_plan_service.py",
    "app/modules/parents/service.py":       "app/services/parent_service.py",
    "app/modules/billing/service.py":       "app/services/billing_service.py",
}

DEPRECATION_HEADER = """\
# DEPRECATED — per ADR 0010 (docs/adr/0010-business-logic-location.md)
# This file is scheduled for removal. All callers must migrate to:
#   {canonical}
# Do NOT add new logic here. Open a PR to migrate any remaining callers.
#
"""


def inventory_dir(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.rglob("*.py") if not p.name.startswith("_"))


def inject_deprecation(path: Path, canonical: str) -> bool:
    """Prepend deprecation header if not already present. Returns True if modified."""
    content = path.read_text(encoding="utf-8")
    if "DEPRECATED — per ADR 0010" in content:
        return False
    header = DEPRECATION_HEADER.format(canonical=canonical)
    path.write_text(header + content, encoding="utf-8")
    return True


def main() -> int:
    mark = "--mark-deprecated" in sys.argv

    service_files = inventory_dir(SERVICES_DIR)
    module_files = inventory_dir(MODULES_DIR)

    print(f"\n{'='*60}")
    print("  EduBoost V2 — Service & Module Inventory")
    print(f"{'='*60}\n")

    print(f"  app/services/  ({len(service_files)} files)\n")
    for f in service_files:
        print(f"    {f}")

    print(f"\n  app/modules/  ({len(module_files)} files)\n")
    for f in module_files:
        print(f"    {f}")

    # Identify actual duplicates (files that exist on disk)
    found_duplicates: list[tuple[Path, str]] = []
    for dup_rel, canonical_rel in KNOWN_DUPLICATES.items():
        dup_path = Path(dup_rel)
        if dup_path.exists():
            found_duplicates.append((dup_path, canonical_rel))

    if found_duplicates:
        print(f"\n  Duplicate service concepts found ({len(found_duplicates)})\n")
        for dup_path, canonical in found_duplicates:
            action = ""
            if mark:
                modified = inject_deprecation(dup_path, canonical)
                action = "  [DEPRECATED header injected]" if modified else "  [already marked]"
            print(f"    DUPLICATE : {dup_path}")
            print(f"    CANONICAL : {canonical}{action}\n")
        if not mark:
            print("  Run with --mark-deprecated to inject deprecation headers.\n")
    else:
        print("\n  ✓ No known duplicate service concepts found on disk.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
