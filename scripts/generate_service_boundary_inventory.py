#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/architecture/service_boundary_inventory.json"
OUT_MD = ROOT / "docs/architecture/service_boundary_inventory.md"


def classify(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    name = path.name.lower()
    if "runtime" in name or "facade" in name:
        return "active_runtime_facade"
    if "migration" in name or "consolidation" in name or "compat" in name:
        return "migration_or_compat_helper"
    if "deprecated" in text:
        return "deprecated_pending_callsite_removal"
    if "service" in name:
        return "domain_or_cross_cutting_service"
    return "unclassified"


def main() -> int:
    rows = []
    for base in [ROOT / "app/services", ROOT / "app/modules"]:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if path.name == "__init__.py":
                continue
            rows.append({"path": str(path.relative_to(ROOT)), "classification": classify(path)})

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = ["# Service Boundary Inventory", "", f"Generated at: `{payload['generated_at']}`", "", "| Path | Classification |", "|---|---|"]
    for row in rows:
        lines.append(f"| `{row['path']}` | {row['classification']} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
