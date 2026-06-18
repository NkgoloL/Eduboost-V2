#!/usr/bin/env python3
"""Verify the Gate 2R.1 approvals manifest."""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVALS = ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r1_approvals.json"
EVIDENCE_INDEX = ROOT / "docs/release-evidence/atlas/phase-02r/gate-2r1/evidence_index.md"

app = json.loads(APPROVALS.read_text(encoding="utf-8"))
evidence_ts = "2026-06-18T13:35:28+02:00"  # from git log evidence commit
evidence_index_sha256 = hashlib.sha256(EVIDENCE_INDEX.read_bytes()).hexdigest()

print(f"Decision:              {app['decision']}")
print(f"Evidence source SHA:   {app['evidence_source_sha']}")
print(f"Evidence commit SHA:   {app['evidence_commit_sha']}")
print(f"Evidence index SHA256: {app['evidence_index_sha256']}")
print(f"Computed index SHA256: {evidence_index_sha256}")
print(f"Index hash match:      {app['evidence_index_sha256'] == evidence_index_sha256}")
print(f"Decided at:            {app['decided_at']}")
print(f"Authorised next gate:  {app['authorised_next_gate']}")
print()

errors = 0
for d in app["decisions"]:
    role = d["role"]
    if d["decided_at"] < evidence_ts:
        print(f"ERROR: {role} decision ({d['decided_at']}) predates evidence ({evidence_ts})")
        errors += 1
    print(f"  {role:30s} {d['decision']:12s} {d['decided_at']}  ref={d['immutable_reference'][:12]}")

print()
if errors:
    print(f"FAILED: {errors} error(s)")
else:
    print("All decisions after evidence: OK")
    print("Approvals manifest valid.")
