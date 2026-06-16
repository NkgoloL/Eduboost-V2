#!/usr/bin/env python
"""Evaluate the Phase 2 retrieval service against an approved JSON dataset."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.services.semantic_retrieval import SemanticRetrievalService, build_embedding_provider
from app.services.semantic_retrieval.evaluation import evaluate_retrieval
from app.services.semantic_retrieval.types import EvaluationCase
from scripts.validate_phase2_evaluation_dataset import validate_dataset_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default="data/retrieval/phase2_evaluation_set.json",
        help="Approved retrieval evaluation JSON file.",
    )
    parser.add_argument("--output", default="", help="Optional JSON output path.")
    parser.add_argument("--allow-smoke", action="store_true", help="Allow a non-closure smoke dataset.")
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    payload = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    if not args.allow_smoke:
        if payload.get("status") != "approved" or payload.get("closure_eligible") is not True:
            raise SystemExit("Dataset is not approved for retrieval closure; use --allow-smoke only for diagnostics.")
        validation_errors = validate_dataset_payload(payload)
        if validation_errors:
            details = "; ".join(validation_errors)
            raise SystemExit(f"Dataset failed canonical retrieval closure validation: {details}")
    cases = [EvaluationCase.model_validate(case) for case in payload["cases"]]
    thresholds = payload.get("thresholds") or {}
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            metrics = await evaluate_retrieval(
                session,
                service=SemanticRetrievalService(
                    embedding_provider=build_embedding_provider()
                ),
                cases=cases,
                recall_threshold=float(thresholds.get("recall_at_k", 0.8)),
                mrr_threshold=float(thresholds.get("mean_reciprocal_rank", 0.6)),
                unsafe_hit_threshold=int(thresholds.get("unsafe_hit_count", 0)),
            )
    finally:
        await engine.dispose()

    result = {
        "dataset_id": payload.get("dataset_id"),
        "case_count": metrics.case_count,
        "recall_at_k": metrics.recall_at_k,
        "mean_reciprocal_rank": metrics.mean_reciprocal_rank,
        "precision_at_k": metrics.precision_at_k,
        "unsafe_hit_count": metrics.unsafe_hit_count,
        "thresholds": metrics.thresholds,
        "passed": metrics.passed,
        "case_results": metrics.case_results,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    return 0 if metrics.passed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
