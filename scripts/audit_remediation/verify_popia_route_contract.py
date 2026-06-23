#!/usr/bin/env python3
"""Static POPIA route-contract verifier for frontend/backend alignment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_FRONTEND_ROUTES = [
    "/popia/data-export/",
    "/popia/deletion-request/",
    "/popia/deletion-cancel/",
    "/popia/restriction-request/",
    "/popia/deletion-status/",
]

REQUIRED_FRONTEND_SNIPPETS = [
    'fetchApi<DataExportBundle>("/popia/exports"',
    'fetchApi<DataRightsStatus>("/popia/erasure"',
    'fetchApi<DataRightsStatus>(`/popia/erasure/${learnerId}/cancel`',
    'fetchApi<DataRightsStatus>("/popia/restriction"',
    'fetchApi<DataRightsStatus>(`/popia/erasure/${learnerId}/status`',
]

REQUIRED_BACKEND_SNIPPETS = [
    '@router.post("/exports")',
    '@router.post("/erasure", status_code=status.HTTP_201_CREATED)',
    '@router.post("/erasure/{learner_id}/cancel")',
    '@router.get("/erasure/{learner_id}/status")',
    '@router.post("/restriction")',
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    services = text("app/frontend/src/lib/api/services.ts")
    parents = text("app/api_v2_routers/parents.py")
    popia_router = text("app/api_v2_routers/popia.py")
    popia_service = text("app/services/popia_service.py")

    for forbidden in FORBIDDEN_FRONTEND_ROUTES:
        if forbidden in services:
            errors.append(f"frontend still references stale POPIA route {forbidden}")

    if "/api/v2/popia/data-export/" in parents:
        errors.append("parent router still emits stale /api/v2/popia/data-export URLs")
    if 'export_url=f"/api/v2/popia/exports?learner_id={learner.id}"' not in parents and '"export_url": f"/api/v2/popia/exports?learner_id={learner.id}"' not in parents:
        errors.append("parent router must emit canonical /api/v2/popia/exports export references")

    for snippet in REQUIRED_FRONTEND_SNIPPETS:
        if snippet not in services:
            errors.append(f"frontend missing canonical POPIA snippet: {snippet}")
    for snippet in REQUIRED_BACKEND_SNIPPETS:
        if snippet not in popia_router:
            errors.append(f"backend missing canonical POPIA route snippet: {snippet}")
    if "async def erasure_status(" not in popia_service:
        errors.append("POPIADataRightsService missing erasure_status method")

    result = {
        "valid": not errors,
        "errors": errors,
        "canonical_frontend_routes": [
            "/popia/exports",
            "/popia/erasure",
            "/popia/erasure/{learner_id}/cancel",
            "/popia/erasure/{learner_id}/status",
            "/popia/restriction",
        ],
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("POPIA ROUTE CONTRACT PASSED" if not errors else "POPIA ROUTE CONTRACT FAILED")
        for error in errors:
            print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
