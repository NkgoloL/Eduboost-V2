#!/usr/bin/env python3
"""Stamp Phase 2R evidence handoff metadata without changing gate status."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs/release-evidence/atlas/phase-02r"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _extract_index_field(text: str, label: str) -> str | None:
    match = re.search(rf"\*\*{re.escape(label)}:\*\*\s+`?([0-9a-f]{{40}})`?", text)
    return match.group(1) if match else None


def _require_sha(label: str, value: str) -> str:
    if not SHA_RE.fullmatch(value):
        raise ValueError(f"{label} must be a 40-character lowercase Git SHA")
    return value


def build_metadata(args: argparse.Namespace) -> dict[str, Any]:
    gate_dir = EVIDENCE_ROOT / f"gate-{args.gate.lower().replace('.', 'r')}"
    if args.gate == "2R.1":
        gate_dir = EVIDENCE_ROOT / "gate-2r1"
    evidence_index = gate_dir / "evidence_index.md"
    index_text = evidence_index.read_text(encoding="utf-8")

    current_branch = _run_git("branch", "--show-current")
    current_tip = args.current_branch_tip_sha or _run_git("rev-parse", "HEAD")
    remote_tip = args.remote_branch_sha_at_handoff
    if remote_tip is None:
        remote_ref = _run_git("ls-remote", "origin", current_branch)
        remote_tip = remote_ref.split()[0] if remote_ref else current_tip

    source_commit = args.source_commit_sha or _extract_index_field(index_text, "Source commit")
    evidence_commit = args.evidence_commit_sha or _extract_index_field(index_text, "Evidence commit")
    if source_commit is None:
        raise ValueError("source_commit_sha was not provided and could not be read from evidence_index.md")
    if evidence_commit is None:
        raise ValueError("evidence_commit_sha was not provided and could not be read from evidence_index.md")

    return {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "phase": "02R",
        "gate": args.gate,
        "status": "candidate_handoff_metadata_only",
        "gate_closure_established": False,
        "next_gate_authorised": False,
        "source_commit_sha": _require_sha("source_commit_sha", source_commit),
        "evidence_commit_sha": _require_sha("evidence_commit_sha", evidence_commit),
        "current_branch": current_branch,
        "current_branch_tip_sha": _require_sha("current_branch_tip_sha", current_tip),
        "remote_branch_sha_at_handoff": _require_sha("remote_branch_sha_at_handoff", remote_tip),
        "evidence_index_path": str(evidence_index.relative_to(ROOT)),
        "evidence_index_sha256": _sha256(evidence_index),
        "raw_artifact_checksum_index": str((gate_dir / "raw/SHA256SUMS.txt").relative_to(ROOT)),
        "approval_state": "pending_independent_gate_2r1_approvals",
        "gate_2r2_state": "blocked",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", default="2R.1")
    parser.add_argument("--source-commit-sha")
    parser.add_argument("--evidence-commit-sha")
    parser.add_argument("--current-branch-tip-sha")
    parser.add_argument("--remote-branch-sha-at-handoff")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    metadata = build_metadata(args)
    output = args.output or (
        EVIDENCE_ROOT
        / f"gate-{args.gate.lower().replace('.', 'r')}"
        / "evidence_handoff_metadata.json"
    )
    if args.gate == "2R.1" and args.output is None:
        output = EVIDENCE_ROOT / "gate-2r1/evidence_handoff_metadata.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps({"valid": True, "output": str(output.relative_to(ROOT)), "metadata": metadata}, indent=2, sort_keys=True))
    else:
        print(f"wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
