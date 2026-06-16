#!/usr/bin/env python3
"""Validate Atlas phase-control paths and prevent unsupported completion claims."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs/roadmap/PHASE_STATUS_REGISTER.md"


def main() -> int:
    errors: list[str] = []
    text = REGISTER.read_text(encoding="utf-8")
    if "Canonical control root:** `atlas`" not in text:
        errors.append("status register does not declare Atlas as canonical")
    for phase in range(1, 8):
        plan = ROOT / f"docs/roadmap/execution/atlas/phase_{phase:02d}_execution_plan.md"
        report = ROOT / f"docs/roadmap/execution/atlas/phase_{phase:02d}_implementation_report.md"
        evidence = ROOT / f"docs/release-evidence/atlas/phase-{phase:02d}/phase_{phase:02d}_evidence_index.md"
        audit = ROOT / f"docs/release-evidence/atlas/phase-{phase:02d}/phase_{phase:02d}_audit_report.md"
        for path in (plan, report, evidence, audit):
            if not path.exists():
                errors.append(f"missing canonical control artifact: {path.relative_to(ROOT)}")
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
