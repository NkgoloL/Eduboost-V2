#!/usr/bin/env python3
"""Verify Technical Audit Phase 02F backend-fast remediation assets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check(name: str, ok: bool, detail: str) -> dict[str, object]:
    return {"name": name, "valid": bool(ok), "detail": detail}


def verify() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    seed_executor = read("app/services/content_staging_seed_executor.py")
    item_model = read("app/models/diagnostic_item.py")
    item_service = read("app/modules/diagnostics/item_bank_service.py")
    router_contract = read("tests/unit/test_api_v2_router_contract.py")
    study_plans = read("app/api_v2_routers/study_plans.py")
    doc = read("docs/roadmap/execution/technical_audit_remediation/02f_backend_fast_item_seed_router.md")

    checks.extend([
        check(
            "seed_executor_session_helpers",
            "async def _session_commit" in seed_executor
            and "async def _session_rollback" in seed_executor
            and "await _session_commit(session)" in seed_executor
            and "await _session_rollback(session)" in seed_executor,
            "Content staging seed executor uses safe session helpers for real AsyncSession and unit-test doubles.",
        ),
        check(
            "seed_executor_returns_result",
            "return StagingSeedRunResult(" in seed_executor
            and "seeded_count=seeded_count" in seed_executor
            and "skipped_count=skipped_count_total" in seed_executor,
            "seed_staging returns a result object with seeded/skipped counts.",
        ),
        check(
            "diagnostic_item_default_quality_state",
            "quality_state = self.irt_quality_state or \"uncalibrated\"" in item_model,
            "DiagnosticItem availability treats missing DB default as uncalibrated.",
        ),
        check(
            "item_bank_selection_default_quality_state",
            "if not isinstance(state, str) or not state:" in item_service
            and "state = \"uncalibrated\"" in item_service,
            "ItemBankService selection treats missing/non-string IRT quality state as uncalibrated.",
        ),
        check(
            "tutor_router_contract_declared",
            '"tutor": "/tutor"' in router_contract,
            "V2 router contract declares the tutor router fragment.",
        ),
        check(
            "study_plan_db_import_contract",
            "from app.core.database import AsyncSessionLocal, get_db" in study_plans
            and "db: AsyncSession = Depends(get_db)" in study_plans,
            "Study plan routes expose the DB import and get_db dependency expected by the consent-gate contract.",
        ),
        check(
            "phase02f_documented_boundaries",
            "No passing backend-fast evidence" in doc
            and "No runtime knowledge-graph implementation" in doc,
            "Phase 02F docs preserve backend-fast and KG boundaries.",
        ),
    ])

    valid = all(c["valid"] for c in checks)
    return {"valid": valid, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for c in result["checks"]:
            print(f"{'PASS' if c['valid'] else 'FAIL'} {c['name']}: {c['detail']}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
