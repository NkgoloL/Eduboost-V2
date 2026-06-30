#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS_ROUTER = ROOT / "app/api_v2_routers/diagnostics.py"
JOBS_MODULE = ROOT / "app/modules/jobs.py"
CORE_JOBS = ROOT / "app/core/jobs.py"
OUT_JSON = ROOT / "docs/release/diagnostics_jobs_integrity_introspection.json"
OUT_MD = ROOT / "docs/release/diagnostics_jobs_integrity_introspection.md"


def function_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))


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
    diagnostics_text = DIAGNOSTICS_ROUTER.read_text(encoding="utf-8") if DIAGNOSTICS_ROUTER.exists() else ""
    jobs_text = JOBS_MODULE.read_text(encoding="utf-8") if JOBS_MODULE.exists() else ""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "diagnostics_router_exists": DIAGNOSTICS_ROUTER.exists(),
        "jobs_module_exists": JOBS_MODULE.exists(),
        "core_jobs_exists": CORE_JOBS.exists(),
        "diagnostics_functions": function_names(DIAGNOSTICS_ROUTER),
        "diagnostics_imports": imports(DIAGNOSTICS_ROUTER),
        "diagnostic_integrity_imported": "app.services.diagnostic_data_integrity" in diagnostics_text,
        "diagnostic_submission_validation_calls": diagnostics_text.count("validate_diagnostic_submission_payload"),
        "mastery_validation_calls": diagnostics_text.count("validate_mastery_update_payload"),
        "jobs_functions": function_names(JOBS_MODULE),
        "consent_service_empty_constructor_count": jobs_text.count("ConsentService()"),
        "async_session_local_in_jobs": "AsyncSessionLocal" in jobs_text,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Diagnostics and Jobs Integrity Introspection",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Check | Value |",
        "|---|---|",
        f"| Diagnostics router exists | {payload['diagnostics_router_exists']} |",
        f"| Jobs module exists | {payload['jobs_module_exists']} |",
        f"| Diagnostic integrity imported | {payload['diagnostic_integrity_imported']} |",
        f"| Diagnostic submission validation calls | {payload['diagnostic_submission_validation_calls']} |",
        f"| Mastery validation calls | {payload['mastery_validation_calls']} |",
        f"| ConsentService() empty constructor count in jobs | {payload['consent_service_empty_constructor_count']} |",
        f"| AsyncSessionLocal in jobs | {payload['async_session_local_in_jobs']} |",
        "",
        "## Diagnostics functions",
        "",
        *(f"- `{name}`" for name in payload["diagnostics_functions"]),
        "",
        "## Job functions",
        "",
        *(f"- `{name}`" for name in payload["jobs_functions"]),
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
