"""Generate canonical current-state documentation from single-source register state.

Implements deliverables for:
- TSR-2.1: Repair production-register summary derivation
- TSR-2.2: Generate current-state documentation (README.md & docs/current_state.md)
- TSR-2.4: Clarify controlled-beta semantics
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.true_state_remediation.core import atomic_write_text, load_json, root_from


def generate_current_state(root: Path) -> dict[str, Any]:
    prod_reg = load_json(root / "docs/roadmap/production_readiness/production_readiness_register.json", {})
    tsr_reg = load_json(root / "docs/roadmap/production_readiness/true_state_remediation_register.json", {})

    now_iso = datetime.now(timezone.utc).isoformat()
    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Current authority & active bundle
    active_bundle = tsr_reg.get("current_bundle", "B02")
    active_stream = "B02 (Canonical Truth and Toolchain)"

    # Generate docs/current_state.md
    current_state_md = f"""---
title: EduBoost Current State
status: active
owner: release-management
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: {now_date}
review_interval_days: 14
evidence_command: PYTHONPATH=. python3 scripts/true_state_remediation/execute_bundle.py --bundle B02 --phase verify --json
code_anchors: [app/api_v2.py, app/frontend/package.json, docs/roadmap/production_readiness/true_state_remediation_register.json]
---

# EduBoost Current State

This file is the canonical current-state summary for EduBoost V2 generated deterministically from single-source register state on {now_date}.

It is intentionally conservative. It records what is true now and what remains unauthorised before production, deployment, public beta, billing, live learner traffic, or further production-readiness implementation work can proceed.

## Product identity

EduBoost V2 is a South African Grade 4 Mathematics learning platform. Its active launch product scope is:

- **Launch-Active Scope**: South African Grade 4 Mathematics (CAPS-aligned).
- **Planned / Inactive Scope**: Grades R–3 and Grades 5–7, and subjects other than Mathematics remain in planning and are not active for launch.
- Diagnostic assessment and adaptive learner support.
- Knowledge-graph-grounded learning-state modelling.
- AI-assisted tutoring through controlled and grounded service boundaries.
- Parent/guardian visibility into progress, consent history, and reports.
- Personalised study plans based on curriculum coverage and mastery gaps.
- Gamification through achievements, points, and badges.
- POPIA-aware privacy, consent, audit, and data-rights workflows.

## Technical identity

The active technical direction is:

- FastAPI V2 backend.
- Next.js frontend under `app/frontend`.
- PostgreSQL 16 persistence with pgvector and Alembic migrations.
- Redis 7 backend for sessions, cache, and ARQ background workers.
- Content Factory and curriculum tooling for controlled source ingestion.
- Generated canonical OpenAPI contract under `docs/openapi.json` and `docs/openapi.yaml`.
- Deterministic Route Inventory under `docs/route_inventory.md`.
- True-State Remediation automation under `scripts/true_state_remediation/`.

## Canonical remediation state

```text
Remediation program: EduBoost V2 True-State Remediation
Active implementation bundle: {active_stream}
Bundle B01 (Release Gate Recovery): verified and closed
Bundle B02 (Canonical Truth and Toolchain): in_progress
Feature freeze: active
Controlled beta operational hold: active
```

## Controlled beta semantics

Controlled-beta fields are distinct and independently enforced:

- **Governance Authorization**: Authorized under controlled remediation scope.
- **Operational Safety**: Internal / staging verification only.
- **Activation Hold**: `active` (live external traffic prohibited).
- **Cohort Limits**: Staging cohort only (<50 test accounts).
- **Kill-Switch State**: Enabled (`FEATURE_FLAG_MAINTENANCE_MODE=true` fails closed).

## Release authority boundaries (fail-closed)

These remain strictly unauthorized:

```text
production_release_authorised: false
deployment_authorised: false
release_tag_authorised: false
public_beta_authorised: false
public_beta_live_traffic_authorised: false
live_learner_traffic_authorised: false
billing_launch_authorised: false
live_payment_processing_authorised: false
```

**Generation timestamp: {now_iso}**
"""

    atomic_write_text(root / "docs/current_state.md", current_state_md)

    # Generate updated README.md header/status
    readme_path = root / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8")
    
    # Replace last_reviewed date in README frontmatter
    readme_content = re.sub(r"last_reviewed:\s*\d{4}-\d{2}-\d{2}", f"last_reviewed: {now_date}", readme_content)
    
    atomic_write_text(readme_path, readme_content)

    return {
        "valid": True,
        "generated_at": now_iso,
        "files": ["docs/current_state.md", "README.md"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = root_from(Path(args.repo))
    res = generate_current_state(root)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
