#!/usr/bin/env python3
"""Validate Gate 2R.5 active-corpus retrieval policy controls."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.corpus import (
    ActiveCorpusBinding,
    ActiveCorpusRetriever,
    CorpusRejectedError,
    RetrievalQuery,
    build_gate2r5_fixture_package,
)


def validate() -> dict[str, object]:
    manifest, projection, binding, result = build_gate2r5_fixture_package()
    errors: list[str] = []
    if not result.hits:
        errors.append("expected at least one real-source retrieval hit")
    if any(hit.record.authority_tier != "tier_1" for hit in result.hits):
        errors.append("fixture retrieval should resolve Tier 1 CAPS authority")
    try:
        ActiveCorpusRetriever(projection, ActiveCorpusBinding(
            activation_key=binding.activation_key,
            corpus_version_id=binding.corpus_version_id,
            binding_epoch=binding.binding_epoch + 1,
            manifest_sha256=binding.manifest_sha256,
        ))
        errors.append("stale/wrong projection binding epoch was not rejected")
    except CorpusRejectedError:
        pass
    retriever = ActiveCorpusRetriever(projection, binding)
    try:
        retriever.search(RetrievalQuery(
            activation_key=binding.activation_key,
            corpus_version_id=binding.corpus_version_id,
            binding_epoch=binding.binding_epoch + 1,
            language="en",
            query_text="whole numbers",
        ))
        errors.append("stale query binding epoch was not rejected")
    except CorpusRejectedError:
        pass
    return {
        "status": "passed" if not errors else "failed",
        "gate": "2R.5",
        "errors": errors,
        "activation_key": binding.activation_key,
        "corpus_version_id": binding.corpus_version_id,
        "binding_epoch": binding.binding_epoch,
        "manifest_sha256": manifest.manifest_sha256,
        "projection_sha256": projection.projection_sha256,
        "retrieval": result.export(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = validate()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Phase 2R Gate 2R.5 retrieval validation " + payload["status"])
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
