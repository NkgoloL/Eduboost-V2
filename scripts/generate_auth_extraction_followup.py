#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "app/api_v2_routers/auth.py"
OUT_JSON = ROOT / "docs/architecture/auth_service_extraction_followup.json"
OUT_MD = ROOT / "docs/architecture/auth_service_extraction_followup.md"


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
    repo_imports = [module for module in imports(AUTH) if module.startswith("app.repositories")]
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "auth_router_repository_imports": repo_imports,
        "next_steps": [
            "Move remaining auth repository interactions into canonical AuthService",
            "Remove auth router repository imports",
            "Remove auth import-linter ignore_imports entries",
            "Add integration tests for register/login/refresh against canonical AuthService",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join([
            "# Auth Service Extraction Follow-up",
            "",
            f"Generated at: `{payload['generated_at']}`",
            "",
            "## Remaining repository imports",
            "",
            *(f"- `{item}`" for item in repo_imports),
            "",
            "## Next steps",
            "",
            *(f"- {item}" for item in payload["next_steps"]),
            "",
        ]),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
