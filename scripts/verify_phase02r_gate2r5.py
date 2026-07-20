#!/usr/bin/env python3
"""Gate 2R.5 implementation verifier."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import run
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run(command: list[str]) -> dict[str, Any]:
    proc = run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"command": command, "exit_code": proc.returncode, "output": proc.stdout[-8000:]}


def _control_errors() -> list[str]:
    control = json.loads((ROOT / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    if control.get("start_approved") is not True:
        errors.append("Phase 02R start_approved must remain true")
    if control.get("approved_gate") != "2R.4":
        errors.append(f"Gate 2R.5 implementation requires approved_gate=2R.4, found {control.get('approved_gate')!r}")
    if control.get("authorised_next_gate") != "2R.5":
        errors.append(f"Gate 2R.5 implementation requires authorised_next_gate=2R.5, found {control.get('authorised_next_gate')!r}")
    if control.get("authorised_next_gate") in {"2R.6", "2R.7", "2R.8"}:
        errors.append("Gate 2R.6+ is authorised; Gate 2R.5 verifier must not run against downstream state")
    return errors


def _behavioral_errors() -> list[str]:
    errors: list[str] = []
    try:
        from dataclasses import replace

        from app.services.curriculum.corpus import (
            ActiveCorpusBinding,
            ActiveCorpusRetriever,
            CorpusBuilder,
            CorpusRejectedError,
            RetrievalProjectionBuilder,
            RetrievalQuery,
            build_activation_key,
            build_gate2r5_fixture_package,
            canonical_gate2r5_candidates,
            versioned_cache_key,
        )

        activation_key = build_activation_key(delivery_language="en")
        if activation_key != "CAPS:g4:MATH:en:global":
            errors.append("activation key contract changed unexpectedly")
        manifest, projection, binding, result = build_gate2r5_fixture_package()
        if len(manifest.manifest_sha256) != 64 or len(projection.projection_sha256) != 64:
            errors.append("manifest/projection hash contract failed")
        if not result.hits:
            errors.append("real-source retrieval dry-run produced no hits")
        if "epoch:1" not in versioned_cache_key(activation_key=activation_key, corpus_version_id="corpus-g4math-en-v1", binding_epoch=1):
            errors.append("versioned cache key must include binding epoch")

        candidates = list(canonical_gate2r5_candidates())
        rejected_cases = [
            replace(candidates[0], mapping_review_status="proposed"),
            replace(candidates[0], rights_status="rejected"),
            replace(candidates[0], authority_tier="tier_2"),
            replace(candidates[0], language_status="machine_translation_draft"),
            replace(candidates[0], source_status="withdrawn"),
            replace(candidates[0], synthetic_fixture=True),
        ]
        builder = CorpusBuilder()
        for bad in rejected_cases[:2] + rejected_cases[3:]:
            try:
                builder.build_manifest(
                    corpus_code="CAPS-G4-MATH-EN",
                    version_number=1,
                    scope={"curriculum_code": "CAPS", "grade": 4, "subject_code": "MATH"},
                    language="en",
                    embedding_model="test",
                    embedding_version="v1",
                    activation_key=activation_key,
                    candidates=[bad],
                )
                errors.append(f"ineligible candidate was accepted: {bad}")
            except CorpusRejectedError:
                pass
        try:
            builder.build_manifest(
                corpus_code="CAPS-G4-MATH-EN",
                version_number=1,
                scope={"curriculum_code": "CAPS", "grade": 4, "subject_code": "MATH"},
                language="en",
                embedding_model="test",
                embedding_version="v1",
                activation_key=activation_key,
                candidates=[rejected_cases[2]],
            )
            errors.append("corpus without Tier 1 authority was accepted")
        except CorpusRejectedError:
            pass
        try:
            ActiveCorpusRetriever(projection, ActiveCorpusBinding(
                activation_key=binding.activation_key,
                corpus_version_id="other-corpus",
                binding_epoch=binding.binding_epoch,
                manifest_sha256=binding.manifest_sha256,
            ))
            errors.append("mixed active binding/projection corpus was accepted")
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
            errors.append("stale query binding epoch was accepted")
        except CorpusRejectedError:
            pass
        projection2 = RetrievalProjectionBuilder().build_projection(
            corpus_version_id=projection.corpus_version_id,
            activation_key=projection.activation_key,
            binding_epoch=projection.binding_epoch,
            manifest=manifest,
            candidates=tuple(reversed(candidates)),
        )
        if projection.projection_sha256 != projection2.projection_sha256:
            errors.append("retrieval projection is not deterministic under candidate ordering")
    except Exception as exc:
        errors.append(f"Gate 2R.5 behavioral checks failed to execute: {exc}")
    return errors


def verify(mode: str) -> dict[str, Any]:
    from app.services.curriculum.phase02r_verification import validate_required_paths

    errors: list[str] = []
    checks: list[dict[str, Any]] = []
    errors.extend(_control_errors())
    errors.extend(validate_required_paths("2R.5"))

    compile_targets = [
        "app/services/curriculum/corpus.py",
        "app/services/curriculum/retrieval.py",
        "app/services/curriculum/phase02r_verification.py",
        "scripts/verify_phase02r_gate2r5.py",
        "scripts/curriculum/build_phase02r_gate2r5_semantic_corpus.py",
        "scripts/curriculum/export_phase02r_gate2r5_retrieval_projection.py",
        "scripts/curriculum/validate_phase02r_gate2r5_retrieval.py",
        "tests/unit/phase02r/test_gate2r5_semantic_corpus.py",
    ]
    checks.append(_run([sys.executable, "-m", "compileall", "-q", *compile_targets]))
    if checks[-1]["exit_code"] != 0:
        errors.append("compileall failed for Gate 2R.5 files")

    for command, message in [
        ([sys.executable, "scripts/curriculum/build_phase02r_gate2r5_semantic_corpus.py", "--json"], "semantic corpus manifest dry-run failed"),
        ([sys.executable, "scripts/curriculum/export_phase02r_gate2r5_retrieval_projection.py", "--json"], "retrieval projection export failed"),
        ([sys.executable, "scripts/curriculum/validate_phase02r_gate2r5_retrieval.py", "--json"], "retrieval validation failed"),
        ([sys.executable, "scripts/verify_migration_graph.py"], "migration graph check failed"),
    ]:
        checks.append(_run(command))
        if checks[-1]["exit_code"] != 0:
            errors.append(message)

    errors.extend(_behavioral_errors())
    if mode == "closure":
        errors.append("Gate 2R.5 closure requires committed candidate evidence, approvals, and a separate transition; implementation verifier cannot close the gate")
    return {"valid": not errors, "errors": errors, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["implementation", "closure"], default="implementation")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.mode)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print(f"Phase 2R Gate 2R.5 {args.mode} verification passed")
    else:
        print(f"Phase 2R Gate 2R.5 {args.mode} verification failed", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
