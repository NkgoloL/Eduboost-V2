"""Static verification registry for Phase 2R Gates 2R.2-2R.8."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

REQUIRED_PATHS_BY_GATE: dict[str, tuple[str, ...]] = {
    "2R.2": (
        "app/models/curriculum_grounding.py",
        "app/services/curriculum/acquisition.py",
        "alembic/versions/20260618_1200_phase02r_grounding_controls.py",
    ),
    "2R.3": (
        "app/services/curriculum/extraction.py",
        "app/models/curriculum_grounding.py",
    ),
    "2R.4": (
        "app/services/curriculum/graph.py",
        "app/models/curriculum_graph.py",
        "scripts/curriculum/validate_phase02r_gate2r4_graph.py",
        "scripts/curriculum/export_phase02r_curriculum_graph.py",
        "scripts/verify_phase02r_gate2r4.py",
        "scripts/verify_phase02r_gate2r4_postgres.sh",
        "scripts/collect_phase02r_gate2r4_evidence.sh",
    ),
    "2R.5": (
        "app/services/curriculum/corpus.py",
        "app/services/curriculum/retrieval.py",
        "app/models/curriculum_grounding.py",
        "scripts/curriculum/build_phase02r_gate2r5_semantic_corpus.py",
        "scripts/curriculum/export_phase02r_gate2r5_retrieval_projection.py",
        "scripts/curriculum/validate_phase02r_gate2r5_retrieval.py",
        "scripts/verify_phase02r_gate2r5.py",
        "scripts/verify_phase02r_gate2r5_postgres.sh",
        "scripts/collect_phase02r_gate2r5_evidence.sh",
    ),
    "2R.6": (
        "app/services/curriculum/grounding.py",
        "app/services/curriculum/claim_validation.py",
        "app/services/curriculum/answer_verification.py",
        "app/services/curriculum/generation.py",
        "scripts/curriculum/build_phase02r_gate2r6_grounded_generation.py",
        "scripts/curriculum/export_phase02r_gate2r6_generation_packet.py",
        "scripts/curriculum/validate_phase02r_gate2r6_generation.py",
        "scripts/verify_phase02r_gate2r6.py",
        "scripts/verify_phase02r_gate2r6_postgres.sh",
        "scripts/collect_phase02r_gate2r6_evidence.sh",
    ),
    "2R.7": (
        "app/services/curriculum/tutor_grounding.py",
        "scripts/curriculum/build_phase02r_gate2r7_grounded_tutor.py",
        "scripts/curriculum/export_phase02r_gate2r7_tutor_packet.py",
        "scripts/curriculum/validate_phase02r_gate2r7_tutor.py",
        "scripts/verify_phase02r_gate2r7.py",
        "scripts/verify_phase02r_gate2r7_postgres.sh",
        "scripts/collect_phase02r_gate2r7_evidence.sh",
    ),
    "2R.8": (
        "app/services/curriculum/legacy_migration.py",
        "app/services/curriculum/evaluation.py",
        "app/services/curriculum/phase02r_closure.py",
        "scripts/curriculum/build_phase02r_gate2r8_legacy_migration.py",
        "scripts/curriculum/export_phase02r_gate2r8_evaluation_report.py",
        "scripts/curriculum/export_phase02r_gate2r8_audit_bundle.py",
        "scripts/curriculum/validate_phase02r_gate2r8_closure.py",
        "scripts/verify_phase02r_gate2r8.py",
        "scripts/verify_phase02r_gate2r8_postgres.sh",
        "scripts/collect_phase02r_gate2r8_evidence.sh",
    ),
}


def validate_required_paths(gate: str) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_PATHS_BY_GATE.get(gate, ()):
        if not (ROOT / relative).is_file():
            errors.append(f"missing required {gate} implementation path: {relative}")
    return errors
