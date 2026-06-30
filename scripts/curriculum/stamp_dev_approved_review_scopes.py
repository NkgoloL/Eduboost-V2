#!/usr/bin/env python3
"""Stamp generated review scopes as dev_approved for non-production staging unlock."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_scope import ContentScopeStatus
from app.services.content_file_artifact_import import ContentFileArtifactImportService
from app.services.content_file_review_workflow import ContentFileReviewWorkflowService
from app.services.content_scope_registry import ContentScopeRegistry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", action="append", default=None, help="Scope to stamp. Repeatable. Defaults to all review scopes.")
    parser.add_argument("--reviewer-id", default="dev-content-review-2026-06-03")
    parser.add_argument("--evidence-url", default="dev-reviewed-generated-artifacts")
    parser.add_argument("--notes", default="Developer reviewed generated artifacts for staging/import unblock. Educator and legal production approvals remain pending.")
    parser.add_argument("--max-records-per-layer", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    registry = ContentScopeRegistry()
    scope_ids = args.scope_id or [scope.scope_id for scope in registry.list_scopes() if scope.status == ContentScopeStatus.REVIEW]
    review_service = ContentFileReviewWorkflowService(project_root=ROOT, registry=registry)
    importer = ContentFileArtifactImportService(project_root=ROOT, registry=registry, review_service=review_service)
    rows = []
    for scope_id in scope_ids:
        review_service.build_review_packet(
            scope_id,
            reviewer_id=args.reviewer_id,
            decision="dev_approved",
            evidence_url=args.evidence_url,
            legal_decision="pending",
            legal_evidence_url="pending",
            notes=args.notes,
        )
        status = review_service.review_status(scope_id)
        plan = importer.plan_scope_import(scope_id, max_records_per_layer=args.max_records_per_layer)
        rows.append({
            "scope_id": scope_id,
            "review_status": status.status,
            "stage_unlocked": status.stage_unlocked,
            "production_unlocked": status.production_unlocked,
            "db_status": plan.db_status,
            "record_count": len(plan.records),
            "stage_blockers": status.stage_blockers,
            "production_blockers": status.production_blockers,
        })
    output = {
        "schema_version": "1.0",
        "scope_count": len(rows),
        "stage_unlocked": sum(1 for row in rows if row["stage_unlocked"]),
        "production_unlocked": sum(1 for row in rows if row["production_unlocked"]),
        "scopes": rows,
    }
    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("Dev-approved review stamps")
        print(f"  scope_count: {output['scope_count']}")
        print(f"  stage_unlocked: {output['stage_unlocked']}")
        print(f"  production_unlocked: {output['production_unlocked']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
