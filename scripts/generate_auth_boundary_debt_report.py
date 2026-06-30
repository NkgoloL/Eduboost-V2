#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
OUT_JSON = ROOT / "docs/architecture/auth_boundary_debt_report.json"
OUT_MD = ROOT / "docs/architecture/auth_boundary_debt_report.md"


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


def main() -> int:
    source = AUTH_ROUTER.read_text(encoding="utf-8") if AUTH_ROUTER.exists() else ""
    repo_imports = [m for m in imports(AUTH_ROUTER) if m.startswith("app.repositories")]
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "auth_router": str(AUTH_ROUTER.relative_to(ROOT)),
        "repository_imports": repo_imports,
        "learner_repository_symbol_present": "LearnerRepository" in source,
        "direct_get_by_guardian_present": ".get_by_guardian(" in source,
        "remaining_debt": [
            "Extract remaining auth repository interactions into canonical AuthService",
            "Remove auth router repository imports after AuthService extraction",
            "Remove auth transition ignore_imports from .importlinter",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Auth Boundary Debt Report",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Repository imports | {', '.join(f'`{item}`' for item in repo_imports) or '-'} |",
        f"| LearnerRepository symbol present | {payload['learner_repository_symbol_present']} |",
        f"| Direct get_by_guardian present | {payload['direct_get_by_guardian_present']} |",
        "",
        "## Remaining debt",
        "",
        *(f"- {item}" for item in payload["remaining_debt"]),
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
