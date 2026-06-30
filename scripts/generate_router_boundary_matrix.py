#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER_DIR = ROOT / "app/api_v2_routers"
OUT_JSON = ROOT / "docs/architecture/router_repository_boundary_matrix.json"
OUT_MD = ROOT / "docs/architecture/router_repository_boundary_matrix.md"

P0_ROUTER_FILES = {"popia.py", "lessons.py", "auth.py"}
AUTH_TRANSITION_ALLOWLIST = {
    "app.repositories.learner_repository",
    "app.repositories.repositories",
}


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
            repo_imports = [module for module in modules if module.startswith("app.repositories")]
            allowed = []
            violations = []
            for module in repo_imports:
                if path.name == "auth.py" and module in AUTH_TRANSITION_ALLOWLIST:
                    allowed.append(module)
                else:
                    violations.append(module)
            rows.append({
                "router": str(path.relative_to(ROOT)),
                "p0_router": path.name in P0_ROUTER_FILES,
                "repository_imports": repo_imports,
                "transition_allowed": allowed,
                "violations": violations,
            })

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Router Repository Boundary Matrix",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Router | P0 | Repository imports | Transition allowed | Violations |",
        "|---|---:|---|---|---|",
    ]
    for row in rows:
        repo = ", ".join(f"`{item}`" for item in row["repository_imports"]) or "-"
        allowed = ", ".join(f"`{item}`" for item in row["transition_allowed"]) or "-"
        violations = ", ".join(f"`{item}`" for item in row["violations"]) or "-"
        lines.append(f"| `{row['router']}` | {row['p0_router']} | {repo} | {allowed} | {violations} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
