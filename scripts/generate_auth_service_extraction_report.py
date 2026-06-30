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
AUTH = ROOT / "app/api_v2_routers/auth.py"
OUT_JSON = ROOT / "docs/architecture/auth_service_extraction_report.json"
OUT_MD = ROOT / "docs/architecture/auth_service_extraction_report.md"


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


def function_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))


def main() -> int:
    source = AUTH.read_text(encoding="utf-8") if AUTH.exists() else ""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "auth_router_repository_imports": [item for item in imports(AUTH) if item.startswith("app.repositories")],
        "auth_router_uses_auth_service_dependency": "app.api_v2_deps.auth_service" in source,
        "auth_router_contains_future_annotations": "from __future__ import annotations" in source,
        "auth_application_service_functions": function_names(ROOT / "app/services/auth_application_service.py"),
        "remaining_business_logic_debt": [
            "Move register orchestration into AuthApplicationService.register",
            "Move login orchestration into AuthApplicationService.login",
            "Move refresh orchestration into AuthApplicationService.refresh",
            "Move dev-session bootstrap into AuthApplicationService.create_dev_session",
            "Add HTTP dependency-override integration tests for each auth lifecycle path",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Auth Service Extraction Report",
                "",
                f"Generated at: `{payload['generated_at']}`",
                "",
                f"Repository imports remaining in auth router: `{len(payload['auth_router_repository_imports'])}`",
                "",
                "## Repository imports",
                "",
                *(f"- `{item}`" for item in payload["auth_router_repository_imports"]),
                "",
                "## Remaining business-logic extraction debt",
                "",
                *(f"- {item}" for item in payload["remaining_business_logic_debt"]),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
