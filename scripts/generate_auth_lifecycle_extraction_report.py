#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "app/api_v2_routers/auth.py"
OUT_JSON = ROOT / "docs/architecture/auth_lifecycle_extraction_report.json"
OUT_MD = ROOT / "docs/architecture/auth_lifecycle_extraction_report.md"


def functions(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))


def main() -> int:
    source = AUTH.read_text(encoding="utf-8")
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "delegates": {
            "register": "auth_service.register(" in source,
            "login": "auth_service.login(" in source,
            "refresh": "auth_service.refresh(" in source,
            "create_dev_session": "auth_service.create_dev_session(" in source,
        },
        "legacy_helpers": [name for name in functions(AUTH) if name.startswith("_auth_lifecycle_legacy_")],
        "repo_import_present": "from app.repositories" in source,
        "future_annotations_present": "from __future__ import annotations" in source,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Auth Lifecycle Extraction Report",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Method | Delegated through AuthApplicationService |",
        "|---|---:|",
    ]
    for method, delegated in payload["delegates"].items():
        lines.append(f"| `{method}` | {delegated} |")
    lines.extend(
        [
            "",
            "## Preserved legacy helpers",
            "",
            *(f"- `{name}`" for name in payload["legacy_helpers"]),
            "",
            "## Remaining debt",
            "",
            "- Move preserved private helpers into `AuthApplicationService` proper.",
            "- Add HTTP request/response tests using dependency overrides and realistic payloads.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
