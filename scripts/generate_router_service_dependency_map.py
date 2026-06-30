#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER_DIR = ROOT / "app/api_v2_routers"
OUT_JSON = ROOT / "docs/architecture/router_service_dependency_map.json"
OUT_MD = ROOT / "docs/architecture/router_service_dependency_map.md"


def imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            modules.append(node.module or "")
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
    return sorted(set(modules))


def main() -> int:
    rows = []
    if ROUTER_DIR.exists():
        for path in sorted(ROUTER_DIR.glob("*.py")):
            modules = imports(path)
            rows.append({
                "router": str(path.relative_to(ROOT)),
                "service_imports": [m for m in modules if m.startswith("app.services") or m.startswith("app.modules")],
                "dependency_imports": [m for m in modules if m.startswith("app.api_v2_deps")],
                "repository_imports": [m for m in modules if m.startswith("app.repositories")],
                "database_imports": [m for m in modules if m in {"app.core.database", "sqlalchemy.ext.asyncio"}],
            })

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Router Service Dependency Map",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Router | Dependencies | Services/modules | Repositories | Database imports |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['router']}` | "
            f"{', '.join(f'`{x}`' for x in row['dependency_imports']) or '-'} | "
            f"{', '.join(f'`{x}`' for x in row['service_imports']) or '-'} | "
            f"{', '.join(f'`{x}`' for x in row['repository_imports']) or '-'} | "
            f"{', '.join(f'`{x}`' for x in row['database_imports']) or '-'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
