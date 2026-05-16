#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "release" / "backend_consolidation_evidence_manifest.md"

EVIDENCE_PATHS = [
    "docs/adr/ADR-021-backend-consolidation-evidence-first.md",
    "docs/release/backend_consolidation_dragons.md",
    "docs/release/backend_consolidation_decision_record.md",
    "docs/release/audit_repository_compatibility_contract.md",
    "docs/release/audit_callsite_inventory.md",
    "docs/release/consent_service_compatibility_contract.md",
    "docs/release/consent_callsite_inventory.md",
    "docs/release/health_readiness_diagnostic_contract.md",
    "docs/release/schema_drift_evidence_contract.md",
    "docs/release/backend_runtime_compatibility_contract.md",
    "docs/release/backend_runtime_compatibility_report.md",
    "docs/release/backend_runtime_probe_contract.md",
    "docs/release/backend_runtime_probe_report.md",
    "docs/release/backend_consolidation_readiness_matrix.md",
    "docs/release/backend_data_retention_decision_checklist.md",
    "docs/release/backend_deletion_candidate_inventory.md",
    "docs/release/backend_consolidation_readiness_report.md",
    "docs/release/backend_consolidation_execution_packet.md",
    "docs/release/audit_canonicalization_implementation_checklist.md",
    "docs/release/consent_runtime_repair_checklist.md",
    "docs/release/schema_drift_db_execution_checklist.md",
    "docs/release/deep_readiness_implementation_checklist.md",
    "docs/release/backend_consolidation_execution_report.md",
    "docs/release/backend_consolidation_terminal_packet.md",
]


@dataclass(frozen=True)
class ManifestRow:
    path: str
    exists: bool
    bytes: int
    sha256: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_rows() -> list[ManifestRow]:
    rows: list[ManifestRow] = []
    for relative in EVIDENCE_PATHS:
        path = REPO_ROOT / relative
        if path.exists():
            rows.append(ManifestRow(relative, True, path.stat().st_size, _sha256(path)))
        else:
            rows.append(ManifestRow(relative, False, 0, ""))
    return rows


def render(rows: list[ManifestRow]) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Backend Consolidation Evidence Manifest",
        "",
        f"Generated at: `{generated}`",
        "",
        "| Path | Exists | Bytes | SHA-256 |",
        "|---|---|---:|---|",
    ]

    for row in rows:
        lines.append(
            f"| `{row.path}` | {'yes' if row.exists else 'no'} | {row.bytes} | `{row.sha256}` |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This manifest proves evidence artefact presence and checksums. It does not approve deletion or schema consolidation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    rows = collect_rows()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(rows), encoding="utf-8")
    missing = [row.path for row in rows if not row.exists]
    print(f"Wrote {OUTPUT} ({len(rows)} row(s), {len(missing)} missing)")
    if missing:
        print("Missing evidence artefacts:")
        for path in missing:
            print(f"- {path}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
