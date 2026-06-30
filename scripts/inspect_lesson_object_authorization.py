#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app/api_v2_routers/lessons.py"
OUT_JSON = ROOT / "docs/release/lesson_object_authorization_introspection.json"
OUT_MD = ROOT / "docs/release/lesson_object_authorization_introspection.md"


def functions() -> list[dict]:
    if not ROUTER.exists():
        return []
    tree = ast.parse(ROUTER.read_text(encoding="utf-8"))
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [arg.arg for arg in node.args.args + node.args.kwonlyargs]
            rows.append({"name": node.name, "args": args, "lineno": node.lineno})
    return sorted(rows, key=lambda item: item["lineno"])


def main() -> int:
    src = ROUTER.read_text(encoding="utf-8") if ROUTER.exists() else ""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "router_exists": ROUTER.exists(),
        "helper_import_present": "app.services.lesson_authorization" in src,
        "read_helper_calls": src.count("require_lesson_read_access_for_current_user"),
        "write_helper_calls": src.count("require_lesson_write_access_for_current_user"),
        "sync_extractor_calls": src.count("iter_sync_lesson_ids"),
        "functions": functions(),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join([
            "# Lesson Object Authorization Introspection",
            "",
            f"Generated at: `{payload['generated_at']}`",
            "",
            "| Check | Value |",
            "|---|---|",
            f"| Router exists | {payload['router_exists']} |",
            f"| Helper import present | {payload['helper_import_present']} |",
            f"| Read helper calls | {payload['read_helper_calls']} |",
            f"| Write helper calls | {payload['write_helper_calls']} |",
            f"| Sync extractor calls | {payload['sync_extractor_calls']} |",
            "",
            "## Router functions",
            "",
            *(f"- `{item['name']}` args={item['args']}" for item in payload["functions"]),
            "",
        ]),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
