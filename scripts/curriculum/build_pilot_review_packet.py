#!/usr/bin/env python3
"""Build a pilot educator-review packet and file-import plan for one scope."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.content_file_artifact_import import ContentFileArtifactImportService
from app.services.content_file_review_workflow import ContentFileReviewWorkflowService


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", default="grade5_mathematics_en")
    parser.add_argument("--reviewer-id", default="pending")
    parser.add_argument("--decision", default="pending")
    parser.add_argument("--evidence-url", default="pending")
    parser.add_argument("--legal-decision", default="pending")
    parser.add_argument("--legal-evidence-url", default="pending")
    parser.add_argument("--notes", default="Pilot packet for educator review; approval evidence is pending.")
    parser.add_argument("--max-records-per-layer", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--import-dry-run", action="store_true", help="Report the DB import plan without mutating the database.")
    args = parser.parse_args()

    review_service = ContentFileReviewWorkflowService(project_root=ROOT)
    review_service.build_review_packet(
        args.scope_id,
        reviewer_id=args.reviewer_id,
        decision=args.decision,
        evidence_url=args.evidence_url,
        legal_decision=args.legal_decision,
        legal_evidence_url=args.legal_evidence_url,
        notes=args.notes,
    )
    importer = ContentFileArtifactImportService(project_root=ROOT, review_service=review_service)
    import_plan = importer.plan_scope_import(
        args.scope_id,
        max_records_per_layer=args.max_records_per_layer,
    )
    output = {
        "scope_id": args.scope_id,
        "review_packet_status": review_service.review_status(args.scope_id).status,
        "review_packet_approved": review_service.review_status(args.scope_id).approved,
        "stage_unlocked": review_service.review_status(args.scope_id).stage_unlocked,
        "production_unlocked": review_service.review_status(args.scope_id).production_unlocked,
        "import_plan": {
            "db_status": import_plan.db_status,
            "record_count": len(import_plan.records),
            "errors": import_plan.errors,
            "dry_run_only": True,
        },
        "packet_path": f"data/generated/review_manifests/{args.scope_id}_educator_review.json",
    }
    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("Pilot educator review packet")
        print(f"  scope_id: {output['scope_id']}")
        print(f"  review_status: {output['review_packet_status']}")
        print(f"  approved: {output['review_packet_approved']}")
        print(f"  stage_unlocked: {output['stage_unlocked']}")
        print(f"  production_unlocked: {output['production_unlocked']}")
        print(f"  import_db_status: {output['import_plan']['db_status']}")
        print(f"  import_record_count: {output['import_plan']['record_count']}")
        print(f"  import_dry_run_only: {output['import_plan']['dry_run_only']}")
        print(f"  packet_path: {output['packet_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
