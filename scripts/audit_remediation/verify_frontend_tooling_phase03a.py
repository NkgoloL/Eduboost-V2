#!/usr/bin/env python3
"""Verify Phase 03A frontend Vitest contract repair assets."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class Finding:
    valid: bool
    message: str


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def verify() -> dict[str, object]:
    findings: list[Finding] = []
    services = _read("app/frontend/__tests__/services.smoke.test.ts")
    findings.append(Finding("/api/backend/popia/erasure/L1/cancel" in services, "services smoke test asserts canonical erasure cancel proxy path"))
    findings.append(Finding("/api/backend/popia/erasure/L1/status" in services, "services smoke test asserts canonical erasure status proxy path"))
    findings.append(Finding("/popia/deletion-cancel" not in services and "/popia/deletion-status" not in services, "services smoke test no longer encodes stale POPIA alias paths"))

    tutor = _read("app/frontend/src/components/learner/AiTutorChat.tsx")
    findings.append(Finding('typeof bottomRef.current?.scrollIntoView === "function"' in tutor, "AI tutor scrollIntoView is guarded for jsdom"))

    collector = _read("scripts/audit_remediation/collect_frontend_tooling_authority_evidence.sh")
    findings.append(Finding("! -name 'frontend_tooling_evidence_check.json'" in collector, "frontend tooling collector excludes verifier output from SHA manifest"))
    findings.append(Finding("write_sha_manifest" in collector, "frontend tooling collector has stable SHA manifest helper"))

    doc = REPO_ROOT / "docs/roadmap/execution/technical_audit_remediation/03a_frontend_tooling_vitest_contracts.md"
    findings.append(Finding(doc.exists(), "Phase 03A execution note exists"))

    payload = {"valid": all(f.valid for f in findings), "findings": [asdict(f) for f in findings]}
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = verify()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for finding in payload["findings"]:
            print(f"{'PASS' if finding['valid'] else 'FAIL'} {finding['message']}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
