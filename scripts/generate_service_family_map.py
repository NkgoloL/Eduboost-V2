#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/architecture/service_family_map.json"
OUT_MD = ROOT / "docs/architecture/service_family_map.md"

DOMAIN_TOKENS = (
    "auth",
    "audit",
    "consent",
    "diagnostic",
    "lesson",
    "learner",
    "popia",
    "assessment",
    "gamification",
    "billing",
    "notification",
)


def classify_path(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    name = path.name.lower()
    rel = str(path.relative_to(ROOT)).lower()

    if "deprecated" in text:
        return "deprecated_legacy_service"
    if "authorization" in name or "authz" in name:
        return "authorization_helper"
    if "runtime" in name or "facade" in name:
        return "active_runtime_facade"
    if "compat" in name or "migration" in name or "consolidation" in name:
        return "migration_or_compat_helper"
    if "/app/modules/" in "/" + rel and "service" in name:
        return "canonical_domain_service"
    if "/app/services/" in "/" + rel and "service" in name:
        return "duplicate_domain_service"
    return "unclassified"


def domain_for(path: Path) -> str:
    rel = str(path.relative_to(ROOT)).lower()
    for token in DOMAIN_TOKENS:
        if token in rel:
            return token
    return "other"


def class_names(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef))


def main() -> int:
    rows = []
    for base in [ROOT / "app/services", ROOT / "app/modules"]:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if path.name == "__init__.py":
                continue
            rows.append({
                "path": str(path.relative_to(ROOT)),
                "domain": domain_for(path),
                "classification": classify_path(path),
                "classes": class_names(path),
            })

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["domain"]].append(row)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "domains": grouped,
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Service Family Map",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Domain | Path | Classification | Classes |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['domain']} | `{row['path']}` | {row['classification']} | "
            f"{', '.join(f'`{item}`' for item in row['classes']) or '-'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
