#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
OUT_JSON = ROOT / "docs/release/auth_router_boundary_introspection.json"
OUT_MD = ROOT / "docs/release/auth_router_boundary_introspection.md"


def imports(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            modules.append(node.module or "")
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
    return sorted(set(modules))


def functions(path: Path) -> list[dict]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rows.append({
                "name": node.name,
                "lineno": node.lineno,
                "args": [arg.arg for arg in node.args.args + node.args.kwonlyargs],
            })
    return sorted(rows, key=lambda row: row["lineno"])


def main() -> int:
    source = AUTH_ROUTER.read_text(encoding="utf-8") if AUTH_ROUTER.exists() else ""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "auth_router_exists": AUTH_ROUTER.exists(),
        "imports": imports(AUTH_ROUTER),
        "functions": functions(AUTH_ROUTER),
        "auth_runtime_dependency_imported": "app.api_v2_deps.auth_runtime" in source,
        "learner_repository_symbol_count": source.count("LearnerRepository"),
        "learner_repository_constructor_count": source.count("LearnerRepository("),
        "direct_get_by_guardian_count": source.count(".get_by_guardian("),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Auth Router Boundary Introspection",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Check | Value |",
        "|---|---|",
        f"| Auth router exists | {payload['auth_router_exists']} |",
        f"| Auth runtime dependency imported | {payload['auth_runtime_dependency_imported']} |",
        f"| LearnerRepository symbol count | {payload['learner_repository_symbol_count']} |",
        f"| LearnerRepository constructor count | {payload['learner_repository_constructor_count']} |",
        f"| Direct `.get_by_guardian(` count | {payload['direct_get_by_guardian_count']} |",
        "",
        "## Functions",
        "",
        *(f"- `{row['name']}` args={row['args']}" for row in payload["functions"]),
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
