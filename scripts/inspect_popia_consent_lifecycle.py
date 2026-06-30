#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "docs/release/popia_consent_lifecycle_introspection.json"
REPORT_MD = ROOT / "docs/release/popia_consent_lifecycle_introspection.md"

TARGETS = {
    "router": ROOT / "app/api_v2_routers/popia.py",
    "canonical_service": ROOT / "app/modules/consent/service.py",
    "deprecated_service": ROOT / "app/services/consent_service.py",
    "standalone_consent_repo": ROOT / "app/repositories/consent_repository.py",
    "aggregate_repositories": ROOT / "app/repositories/repositories.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _imports_from(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    return sorted(set(imports))


def _function_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sorted(
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )


def _class_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef))


def main() -> int:
    router_text = _read(TARGETS["router"])
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": {name: str(path.relative_to(ROOT)) for name, path in TARGETS.items()},
        "exists": {name: path.exists() for name, path in TARGETS.items()},
        "router_imports": _imports_from(TARGETS["router"]),
        "router_functions": _function_names(TARGETS["router"]),
        "canonical_service_classes": _class_names(TARGETS["canonical_service"]),
        "canonical_service_functions": _function_names(TARGETS["canonical_service"]),
        "deprecated_service_classes": _class_names(TARGETS["deprecated_service"]),
        "generated_uuid_dependency_count": router_text.count("Depends(lambda: uuid.uuid4())"),
        "deprecated_service_imported_by_router": "app.services.consent_service" in router_text,
        "canonical_service_imported_by_router": "app.modules.consent.service" in router_text,
    }

    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# POPIA Consent Lifecycle Introspection",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "| Check | Value |",
        "|---|---|",
        f"| Router exists | {payload['exists']['router']} |",
        f"| Canonical service exists | {payload['exists']['canonical_service']} |",
        f"| Deprecated service exists | {payload['exists']['deprecated_service']} |",
        f"| Generated UUID dependency count | {payload['generated_uuid_dependency_count']} |",
        f"| Deprecated service imported by router | {payload['deprecated_service_imported_by_router']} |",
        f"| Canonical service imported by router | {payload['canonical_service_imported_by_router']} |",
        "",
        "## Router functions",
        "",
        *(f"- `{name}`" for name in payload["router_functions"]),
        "",
        "## Canonical service classes",
        "",
        *(f"- `{name}`" for name in payload["canonical_service_classes"]),
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_JSON.relative_to(ROOT)}")
    print(f"Wrote {REPORT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
