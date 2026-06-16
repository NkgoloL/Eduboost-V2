#!/usr/bin/env python3
"""Validate Atlas phase-control paths and prevent unsupported completion claims."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs/roadmap/PHASE_STATUS_REGISTER.md"

PHASES = [
    {
        "label": "01",
        "plan": "docs/roadmap/execution/atlas/phase_01_execution_plan.md",
        "report": "docs/roadmap/execution/atlas/phase_01_implementation_report.md",
        "evidence": "docs/release-evidence/atlas/phase-01/phase_01_evidence_index.md",
        "audit": "docs/release-evidence/atlas/phase-01/phase_01_audit_report.md",
    },
    {
        "label": "02",
        "plan": "docs/roadmap/execution/atlas/phase_02_execution_plan.md",
        "report": "docs/roadmap/execution/atlas/phase_02_implementation_report.md",
        "evidence": "docs/release-evidence/atlas/phase-02/phase_02_evidence_index.md",
        "audit": "docs/release-evidence/atlas/phase-02/phase_02_audit_report.md",
    },
    {
        "label": "02R",
        "plan": "docs/roadmap/execution/atlas/phase_02r_execution_plan.md",
        "report": "docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md",
        "evidence": "docs/release-evidence/atlas/phase-02r/gate-2r0/evidence_index.md",
        "audit": "docs/release-evidence/atlas/phase-02r/gate-2r0/audit_report.md",
    },
    *[
        {
            "label": f"{phase:02d}",
            "plan": f"docs/roadmap/execution/atlas/phase_{phase:02d}_execution_plan.md",
            "report": f"docs/roadmap/execution/atlas/phase_{phase:02d}_implementation_report.md",
            "evidence": f"docs/release-evidence/atlas/phase-{phase:02d}/phase_{phase:02d}_evidence_index.md",
            "audit": f"docs/release-evidence/atlas/phase-{phase:02d}/phase_{phase:02d}_audit_report.md",
        }
        for phase in range(3, 8)
    ],
]


def main() -> int:
    errors: list[str] = []
    text = REGISTER.read_text(encoding="utf-8")
    if "Canonical control root:** `atlas`" not in text:
        errors.append("status register does not declare Atlas as canonical")
    for phase in PHASES:
        for key in ("plan", "report", "evidence", "audit"):
            path = ROOT / phase[key]
            if not path.exists():
                errors.append(f"missing canonical control artifact: {path.relative_to(ROOT)}")
    control_path = ROOT / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json"
    if control_path.exists():
        control = json.loads(control_path.read_text(encoding="utf-8"))
        if control.get("phase") != "02R":
            errors.append("Phase 02R start-gate control has incorrect phase")
        if not isinstance(control.get("start_approved"), bool):
            errors.append("Phase 02R start-gate control must expose boolean start_approved")
    else:
        errors.append(f"missing canonical control artifact: {control_path.relative_to(ROOT)}")
    for backup in ROOT.glob(".phase*-backup-*"):
        errors.append(f"backup directory remains inside repository: {backup.name}")
    for manifest in (ROOT / "docs/release-evidence/atlas").glob("phase-*/raw/SHA256SUMS*"):
        for raw in manifest.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                errors.append(f"invalid checksum line in {manifest.relative_to(ROOT)}: {line}")
                continue
            expected, name = parts
            name = name.lstrip("* ")
            candidate = manifest.parent / name
            if not candidate.exists():
                # tolerate historic paths by checking basename in the raw directory
                candidate = manifest.parent / Path(name).name
            if not candidate.exists():
                errors.append(f"checksum target missing: {name}")
                continue
            actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual != expected:
                errors.append(f"checksum mismatch: {candidate.relative_to(ROOT)}")
    if errors:
        print("Phase-control validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Atlas phase-control validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
