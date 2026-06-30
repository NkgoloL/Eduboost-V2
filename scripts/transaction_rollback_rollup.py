from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"
OUT_JSON = ROOT / "docs/release/transaction_rollback_rollup_report.json"
OUT_MD = ROOT / "docs/release/transaction_rollback_rollup_report.md"

REQUIRED_PROOFS = {
    "TX-POPIA-001": "POPIA consent lifecycle + audit rollback proof",
    "TX-AUTH-001": "Auth user + guardian + learner rollback proof",
    "TX-DIAG-001": "Diagnostic response + mastery + audit rollback proof",
    "TX-LESSON-001": "Lesson completion + gamification XP + audit rollback proof",
}

EXPECTED_EVIDENCE = {
    "TX-POPIA-001": "docs/release/no_false_closure_status_after_1431_1470.md",
    "TX-AUTH-001": "docs/release/no_false_closure_status_after_1471_1510.md",
    "TX-DIAG-001": "docs/release/no_false_closure_status_after_1511_1550.md",
    "TX-LESSON-001": "docs/release/no_false_closure_status_after_1551_1590.md",
}


@dataclass(frozen=True)
class RollupProof:
    id: str
    title: str
    present_in_registry: bool
    integration_passing: bool
    evidence_file: str
    evidence_exists: bool


@dataclass(frozen=True)
class TransactionRollbackRollup:
    generated_at: str
    status: str
    proofs: list[RollupProof]
    remaining_boundaries: list[str]


def _registry_text() -> str:
    return REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""


def _proof_status_for(registry: str, proof_id: str) -> str | None:
    marker = f"id: {proof_id}"
    index = registry.find(marker)
    if index < 0:
        return None
    block = registry[index : registry.find("\n  - id:", index + 1)]
    if not block:
        block = registry[index:]
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("proof_status:"):
            return stripped.split(":", 1)[1].strip()
    return None


def build_rollup() -> TransactionRollbackRollup:
    registry = _registry_text()
    proofs: list[RollupProof] = []

    for proof_id, title in REQUIRED_PROOFS.items():
        status = _proof_status_for(registry, proof_id)
        evidence_file = EXPECTED_EVIDENCE[proof_id]
        proofs.append(
            RollupProof(
                id=proof_id,
                title=title,
                present_in_registry=status is not None,
                integration_passing=status == "integration-passing",
                evidence_file=evidence_file,
                evidence_exists=(ROOT / evidence_file).exists(),
            )
        )

    complete = all(proof.present_in_registry and proof.integration_passing and proof.evidence_exists for proof in proofs)

    return TransactionRollbackRollup(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        status="isolated_rollback_coverage_complete" if complete else "rollback_coverage_incomplete",
        proofs=proofs,
        remaining_boundaries=[
            "production route wiring through transactional services not proven",
            "live Postgres rollback proof not proven",
            "migration-level rollback behavior not proven",
            "staging evidence not attached",
        ],
    )


def write_rollup() -> TransactionRollbackRollup:
    rollup = build_rollup()
    OUT_JSON.write_text(json.dumps(asdict(rollup), indent=2), encoding="utf-8")

    lines = [
        "# Transaction Rollback Proof Rollup",
        "",
        f"Generated at: `{rollup.generated_at}`",
        "",
        f"**Status:** `{rollup.status}`",
        "",
        "## Required proof coverage",
        "",
        "| ID | Title | Registry | Integration passing | Evidence file | Evidence exists |",
        "|---|---|---:|---:|---|---:|",
    ]
    for proof in rollup.proofs:
        lines.append(
            f"| `{proof.id}` | {proof.title} | {proof.present_in_registry} | "
            f"{proof.integration_passing} | `{proof.evidence_file}` | {proof.evidence_exists} |"
        )

    lines.extend(["", "## Remaining boundaries", ""])
    lines.extend(f"- {item}" for item in rollup.remaining_boundaries)
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "TX-001 can be treated as complete only at isolated rollback-proof coverage level. "
            "It is not production-ready until route wiring, live database, and staging evidence are attached.",
            "",
        ]
    )

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return rollup


__all__ = ["REQUIRED_PROOFS", "TransactionRollbackRollup", "build_rollup", "write_rollup"]
