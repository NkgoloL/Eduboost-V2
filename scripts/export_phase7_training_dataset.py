#!/usr/bin/env python3
"""Export an approved Phase 7 training dataset manifest to deterministic JSONL."""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.services.curriculum_expansion import TrainingDatasetGovernanceService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-id", required=True)
    parser.add_argument("--output-name", required=True)
    parser.add_argument("--artifact-root", default="artifacts/training")
    return parser


async def _run(args: argparse.Namespace) -> None:
    async with AsyncSessionLocal() as db:
        service = TrainingDatasetGovernanceService(db, Path(args.artifact_root))
        manifest, output = await service.export_manifest(UUID(args.manifest_id), args.output_name)
        await db.commit()
        print(f"manifest_id={manifest.manifest_id}")
        print(f"dataset_version={manifest.dataset_version}")
        print(f"dataset_sha256={manifest.dataset_sha256}")
        print(f"output={output}")


def main() -> int:
    args = build_parser().parse_args()
    asyncio.run(_run(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
