#!/usr/bin/env python3
"""Static and behavioral verifier for Phase 2R Gates 2R.2-2R.8.

This verifier intentionally avoids importing the SQLAlchemy Base because local
static environments may not have the async PostgreSQL driver installed. Live ORM
and trigger behavior is proven by scripts/verify_phase02r_postgres.sh.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SUPPORTED_GATES = {"2R.2", "2R.3", "2R.4", "2R.5", "2R.6", "2R.7", "2R.8"}


def _run(command: list[str]) -> dict[str, object]:
    proc = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"command": command, "exit_code": proc.returncode, "output": proc.stdout[-8000:]}


def _behavioral_contracts() -> list[str]:
    errors: list[str] = []
    try:
        import hashlib

        from app.services.curriculum.acquisition import ControlledAcquisitionService, assert_no_learner_pii_in_source_metadata
        from app.services.curriculum.answer_verification import DeterministicMathAnswerVerifier
        from app.services.curriculum.claim_validation import Claim, ClaimValidator
        from app.services.curriculum.corpus import CorpusBuilder, CorpusChunkCandidate, versioned_cache_key
        from app.services.curriculum.evaluation import RetrievalEvaluationCase, RetrievalEvaluationScorer
        from app.services.curriculum.extraction import StructuredTextExtractor
        from app.services.curriculum.graph import MappingDraft, build_grade4_mathematics_skeleton
        from app.services.curriculum.grounding import GroundingPolicyEngine, RetrievedChunk
        from app.services.curriculum.legacy import LegacyArtifactView, LegacyMigrationClassifier
        from app.services.curriculum.tutor_grounding import TutorGroundingPolicy, TutorGroundingTrace

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.txt"
            path.write_text("PAGE ONE\n\nWhole numbers\fPAGE TWO\n\nFractions", encoding="utf-8")
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            acquired = ControlledAcquisitionService().acquire_local_file(path, expected_sha256=sha)
            if acquired.sha256 != sha:
                errors.append("acquisition checksum contract failed")
            try:
                assert_no_learner_pii_in_source_metadata({"learner_id": "L1"})
                errors.append("PII metadata was not rejected")
            except Exception:
                pass
            extracted = StructuredTextExtractor(max_chunk_chars=80).extract_text_fixture(path, language="en")
            if len(extracted.pages) != 2 or not extracted.chunks:
                errors.append("structured extraction did not preserve pages/chunks")

        for node in build_grade4_mathematics_skeleton():
            node.validate()
        try:
            MappingDraft("chunk", "node", "DEFINED_IN", "machine_proposed", "review_required").validate_for_retrieval()
            errors.append("unapproved mapping was not rejected")
        except Exception:
            pass

        candidate = CorpusChunkCandidate(
            chunk_version_id="chunk-1",
            source_version_id="source-1",
            mapping_version_id="map-1",
            authority_tier="tier_1",
            rights_status="approved",
            chunk_review_status="approved",
            mapping_review_status="approved",
            quality_score=0.95,
            language="en",
        )
        manifest = CorpusBuilder().build_manifest(
            corpus_code="g4-maths-en",
            version_number=1,
            scope={"grade": 4, "subject": "Mathematics"},
            language="en",
            embedding_model="test-embedding",
            embedding_version="v1",
            candidates=[candidate],
        )
        if len(manifest.manifest_sha256) != 64:
            errors.append("corpus manifest hash contract failed")
        if "epoch:1" not in versioned_cache_key(activation_key="g4-maths:en", corpus_version_id="corpus-1", binding_epoch=1):
            errors.append("versioned cache key contract failed")

        chunk = RetrievedChunk(
            chunk_version_id="chunk-1",
            source_version_id="source-1",
            mapping_version_ids=["map-1"],
            objective_ids=["obj-1"],
            authority_tier="tier_1",
            rights_status="approved",
            review_status="approved",
            corpus_version_id="corpus-1",
            score=0.9,
            language="en",
            text="Learners compare and order whole numbers.",
        )
        decision = GroundingPolicyEngine().validate_generation_grounding(
            corpus_version_id="corpus-1",
            requested_objective_ids=["obj-1"],
            retrieved_chunks=[chunk],
        )
        if not decision.passed or not decision.source_snapshot_hash:
            errors.append("generation grounding contract failed")
        if ClaimValidator().validate([Claim("curriculum_requirement", "Learners compare whole numbers", ["chunk-1"])]).status != "passed":
            errors.append("claim validation contract failed")
        if DeterministicMathAnswerVerifier().verify_arithmetic_expression(question_expression="2 + 3 * 4", proposed_answer="14").status != "passed":
            errors.append("deterministic answer verifier contract failed")
        TutorGroundingPolicy().validate(TutorGroundingTrace("what is CAPS?", [], [], [], None, "fallback", "No approved corpus available"))
        if LegacyMigrationClassifier().classify(LegacyArtifactView("a1", "lesson", True, None, [])).disposition != "published_requires_review":
            errors.append("legacy classifier contract failed")
        positives = [RetrievalEvaluationCase(f"p{i}", "en", "Numbers", 1, "query", [f"c{i}"], [f"c{i}"]) for i in range(18)]
        negatives = [RetrievalEvaluationCase(f"n{i}", "en", "Numbers", 1, "bad query", [], [], True) for i in range(10)]
        metrics = RetrievalEvaluationScorer().score(positives + negatives)
        if metrics.positive_case_count != 18 or metrics.negative_case_count != 10:
            errors.append("retrieval evaluation threshold contract failed")
    except Exception as exc:
        errors.append(f"behavioral contract execution failed: {exc}")
    return errors


def verify(gate: str, mode: str) -> dict[str, object]:
    errors: list[str] = []
    checks: list[dict[str, object]] = []
    if gate not in SUPPORTED_GATES:
        return {"valid": False, "errors": [f"unsupported gate: {gate}"], "checks": []}

    from app.services.curriculum.phase02r_verification import validate_required_paths

    errors.extend(validate_required_paths(gate))
    compile_targets = ["app/models/curriculum_grounding.py", "scripts/verify_phase02r_gate2r2_to_2r8.py"]
    compile_targets.extend(validate_required_paths.__globals__["REQUIRED_PATHS_BY_GATE"].get(gate, ()))
    compile_check = _run([sys.executable, "-m", "compileall", "-q", *sorted(set(compile_targets))])
    checks.append(compile_check)
    if compile_check["exit_code"] != 0:
        errors.append("compileall failed for Phase 2R grounding modules")

    errors.extend(_behavioral_contracts())

    graph_check = _run([sys.executable, "scripts/verify_migration_graph.py"])
    checks.append(graph_check)
    if graph_check["exit_code"] != 0:
        errors.append("migration graph check failed")

    if mode == "closure":
        errors.append(
            f"{gate} closure requires real source data, reviewer approvals, live PostgreSQL proof, and gate-specific evidence; static implementation verifier cannot close it."
        )
    return {"valid": not errors, "errors": errors, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True)
    parser.add_argument("--mode", choices=["implementation", "closure"], default="implementation")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.gate, args.mode)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print(f"Phase 2R Gate {args.gate} implementation verification passed")
    else:
        print(f"Phase 2R Gate {args.gate} verification failed", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
