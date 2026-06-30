#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "app/api_v2_routers/auth.py"
SERVICE = ROOT / "app/services/auth_application_service.py"
IMPL = ROOT / "app/services/auth_lifecycle_impl.py"
OUT_JSON = ROOT / "docs/architecture/auth_service_ownership_report.json"
OUT_MD = ROOT / "docs/architecture/auth_service_ownership_report.md"


def function_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))


def main() -> int:
    auth_text = AUTH.read_text(encoding="utf-8") if AUTH.exists() else ""
    service_text = SERVICE.read_text(encoding="utf-8") if SERVICE.exists() else ""

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "auth_router_has_legacy_helpers": "_auth_lifecycle_legacy_" in auth_text,
        "auth_router_imports_repositories": "from app.repositories" in auth_text,
        "auth_router_has_future_annotations": "from __future__ import annotations" in auth_text,
        "auth_application_service_methods": {
            method: f"AuthApplicationService.{method}" in service_text
            for method in ("register", "login", "refresh", "create_dev_session")
        },
        "implementation_functions": function_names(IMPL),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Auth Service Ownership Report",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Check | Value |",
        "|---|---|",
        f"| Auth router has legacy helpers | {payload['auth_router_has_legacy_helpers']} |",
        f"| Auth router imports repositories | {payload['auth_router_imports_repositories']} |",
        f"| Auth router has future annotations | {payload['auth_router_has_future_annotations']} |",
        "",
        "## AuthApplicationService lifecycle ownership",
        "",
    ]
    lines.extend(f"- `{method}`: {present}" for method, present in payload["auth_application_service_methods"].items())
    lines.extend(["", "## Implementation functions", ""])
    lines.extend(f"- `{name}`" for name in payload["implementation_functions"])
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
