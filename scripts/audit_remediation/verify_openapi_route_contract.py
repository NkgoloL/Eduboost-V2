#!/usr/bin/env python3
"""Verify OpenAPI/frontend route contract for technical-audit remediation.

This verifier is dependency-light: it reads committed source and JSON files only.
It does not import the FastAPI app. Use ``regenerate_openapi_contract.sh`` to
regenerate and check OpenAPI with the project Python environment first.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RouteRequirement:
    path: str
    method: str
    reason: str


REQUIRED_OPENAPI_ROUTES: tuple[RouteRequirement, ...] = (
    RouteRequirement("/api/v2/popia/exports", "post", "canonical POPIA data export"),
    RouteRequirement("/v2/popia/exports", "post", "canonical POPIA data export alias"),
    RouteRequirement("/api/v2/popia/erasure", "post", "canonical POPIA erasure request"),
    RouteRequirement("/v2/popia/erasure", "post", "canonical POPIA erasure request alias"),
    RouteRequirement("/api/v2/popia/erasure/{learner_id}/cancel", "post", "canonical POPIA erasure cancellation"),
    RouteRequirement("/v2/popia/erasure/{learner_id}/cancel", "post", "canonical POPIA erasure cancellation alias"),
    RouteRequirement("/api/v2/popia/erasure/{learner_id}/status", "get", "canonical POPIA erasure status"),
    RouteRequirement("/v2/popia/erasure/{learner_id}/status", "get", "canonical POPIA erasure status alias"),
    RouteRequirement("/api/v2/popia/restriction", "post", "canonical POPIA processing restriction"),
    RouteRequirement("/v2/popia/restriction", "post", "canonical POPIA processing restriction alias"),
    RouteRequirement("/api/v2/parents/{guardian_id}/export", "get", "parent export endpoint"),
    RouteRequirement("/v2/parents/{guardian_id}/export", "get", "parent export endpoint alias"),
)

FORBIDDEN_FRONTEND_ROUTES: tuple[str, ...] = (
    "/popia/data-export/",
    "/popia/deletion-request/",
    "/popia/deletion-cancel/",
    "/popia/restriction-request/",
    "/popia/deletion-status/",
)

REQUIRED_FRONTEND_PATTERNS: tuple[str, ...] = (
    r'fetchApi<[^>]+>\("/popia/exports"',
    r'fetchApi<[^>]+>\("/popia/erasure"',
    r'fetchApi<[^>]+>\(`/popia/erasure/\$\{learnerId\}/cancel`',
    r'fetchApi<[^>]+>\("/popia/restriction"',
    r'fetchApi<[^>]+>\(`/popia/erasure/\$\{learnerId\}/status`',
    r'fetchApi<[^>]+>\(`/parents/\$\{guardianId\}/export`',
)

STALE_PARENT_EXPORT_SNIPPETS: tuple[str, ...] = (
    "/api/v2/popia/data-export/",
    "/api/v2/popia/deletion-request/",
    "/api/v2/popia/deletion-status/",
)


def _read(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def _load_openapi(root: Path) -> dict[str, Any]:
    return json.loads(_read(root, "docs/openapi.json"))


def verify(root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    openapi_path = root / "docs/openapi.json"
    if not openapi_path.exists():
        errors.append("missing docs/openapi.json")
        openapi: dict[str, Any] = {"paths": {}}
    else:
        checked.append("docs/openapi.json")
        try:
            openapi = _load_openapi(root)
        except json.JSONDecodeError as exc:
            errors.append(f"docs/openapi.json is invalid JSON: {exc}")
            openapi = {"paths": {}}

    paths = openapi.get("paths") if isinstance(openapi, dict) else {}
    if not isinstance(paths, dict):
        errors.append("docs/openapi.json must contain an object-valued paths field")
        paths = {}

    for requirement in REQUIRED_OPENAPI_ROUTES:
        methods = paths.get(requirement.path)
        if not isinstance(methods, dict):
            errors.append(f"OpenAPI missing {requirement.method.upper()} {requirement.path} ({requirement.reason})")
            continue
        if requirement.method.lower() not in {str(method).lower() for method in methods.keys()}:
            errors.append(f"OpenAPI path {requirement.path} missing method {requirement.method.upper()} ({requirement.reason})")

    services_path = "app/frontend/src/lib/api/services.ts"
    parents_path = "app/api_v2_routers/parents.py"
    popia_router_path = "app/api_v2_routers/popia.py"
    for rel_path in (services_path, parents_path, popia_router_path):
        if not (root / rel_path).exists():
            errors.append(f"missing {rel_path}")

    services = _read(root, services_path) if (root / services_path).exists() else ""
    parents = _read(root, parents_path) if (root / parents_path).exists() else ""
    popia_router = _read(root, popia_router_path) if (root / popia_router_path).exists() else ""
    checked.extend(path for path in (services_path, parents_path, popia_router_path) if (root / path).exists())

    for forbidden in FORBIDDEN_FRONTEND_ROUTES:
        if forbidden in services:
            errors.append(f"frontend still references stale POPIA route fragment {forbidden}")

    for pattern in REQUIRED_FRONTEND_PATTERNS:
        if not re.search(pattern, services):
            errors.append(f"frontend missing canonical route pattern: {pattern}")

    for stale in STALE_PARENT_EXPORT_SNIPPETS:
        if stale in parents:
            errors.append(f"parent router still emits stale privacy URL fragment {stale}")

    if "/api/v2/popia/exports?learner_id=" not in parents:
        errors.append("parent router must emit canonical /api/v2/popia/exports?learner_id= export URL")

    if '@router.get("/erasure/{learner_id}/status")' not in popia_router:
        errors.append("backend POPIA router must expose GET /erasure/{learner_id}/status")

    if errors:
        warnings.append("Run PYTHON_BIN=.venv/bin/python bash scripts/audit_remediation/regenerate_openapi_contract.sh --regenerate after fixing source routes.")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "required_openapi_routes": [
            {"path": req.path, "method": req.method.upper(), "reason": req.reason}
            for req in REQUIRED_OPENAPI_ROUTES
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root, for tests or alternate checkouts")
    args = parser.parse_args()

    result = verify(args.root.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("OPENAPI ROUTE CONTRACT PASSED" if result["valid"] else "OPENAPI ROUTE CONTRACT FAILED")
        for error in result["errors"]:
            print(f"- {error}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
