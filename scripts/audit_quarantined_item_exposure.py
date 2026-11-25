#!/usr/bin/env python3
"""Aggregate lower-bound exposure history for the quarantined Grade 4 launch bank.

Run separately with the authorized DATABASE_URL for each environment. Never emits
learner identifiers or response text. ItemExposure is created on answer submission,
so zero rows do not prove that an item was never served.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import AsyncSessionLocal
from app.models.item_exposure import ItemExposure

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/quarantine/generated_content_2026-11-23/originals/data/generated/items/grade4_maths_launch_item_bank.json"


async def collect(environment: str) -> dict[str, Any]:
    item_ids = [row["item_id"] for row in json.loads(SOURCE.read_text())["items"]]
    try:
        async with AsyncSessionLocal() as session:
            query = select(
                func.count(ItemExposure.id),
                func.count(func.distinct(ItemExposure.learner_id)),
                func.count(ItemExposure.answered_at),
                func.sum(case((ItemExposure.is_correct.is_(True), 1), else_=0)),
                func.sum(case((ItemExposure.is_correct.is_(False), 1), else_=0)),
                func.min(ItemExposure.served_at),
                func.max(ItemExposure.served_at),
            ).where(ItemExposure.item_id.in_(item_ids))
            row = (await session.execute(query)).one()
            item_rows = (
                await session.execute(
                    select(ItemExposure.item_id, func.count(ItemExposure.id))
                    .where(ItemExposure.item_id.in_(item_ids))
                    .group_by(ItemExposure.item_id)
                )
            ).all()
            return {
                "environment": environment,
                "assessment": "lower_bound_observed",
                "launch_item_count": len(item_ids),
                "exposure_rows": int(row[0] or 0),
                "distinct_learners_with_submissions": int(row[1] or 0),
                "answered_exposure_rows": int(row[2] or 0),
                "correct_responses_by_recorded_key": int(row[3] or 0),
                "incorrect_responses_by_recorded_key": int(row[4] or 0),
                "items_with_submissions": len(item_rows),
                "first_submission_at": row[5].isoformat() if row[5] else None,
                "last_submission_at": row[6].isoformat() if row[6] else None,
                "warning": "Exposure rows are recorded on response, not on every item serve; this is a lower bound. Cross-check application/session logs before concluding no exposure.",
            }
    except (SQLAlchemyError, OSError, RuntimeError) as exc:
        return {
            "environment": environment,
            "assessment": "unverified",
            "launch_item_count": len(item_ids),
            "error_type": type(exc).__name__,
            "warning": "No exposure conclusion can be drawn until this query and serving-log review run against the target environment.",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", required=True, help="local, Compose, Render, or ACA target label")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = asyncio.run(collect(args.environment))
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["assessment"] == "lower_bound_observed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
