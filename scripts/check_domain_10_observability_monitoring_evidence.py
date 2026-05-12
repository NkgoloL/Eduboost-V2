#!/usr/bin/env python3
"""Verify repo-side evidence for Observability & Monitoring roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['prometheus.yml', 'prometheus', 'grafana', 'grafana/dashboards', 'alertmanager', 'alertmanager/rules', 'app/api_v2.py', 'app/middleware', 'docs/operations', 'docs/operations/staging_operations_evidence_2026-05-11.md', 'scripts/check_observability_ops_evidence.py', '.github/workflows/cluster-d-ci.yml', 'Makefile']
TRACKED_GAPS = []
EXTERNAL_GATES = ['Green GitHub Actions status must be verified on GitHub after push.', 'Production/staging/cloud evidence cannot be produced from repository files alone.', 'Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.', 'Grafana/Prometheus/Loki/Alertmanager must be validated in staging or production monitoring systems.']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 10: Observability & Monitoring")
    print(f"Repo evidence checked: {len(REQUIRED_EVIDENCE)} item(s)")
    if missing:
        print("Missing required repo evidence:")
        for item in missing:
            print(f"- {item}")
        return 1
    print("Repo-side evidence files are present.")
    if TRACKED_GAPS:
        print("Tracked repo gaps from roadmap scope:")
        for item in TRACKED_GAPS:
            print(f"- {item}")
    if EXTERNAL_GATES:
        print("External/human gates remain outside repository verification:")
        for item in EXTERNAL_GATES:
            print(f"- {item}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
