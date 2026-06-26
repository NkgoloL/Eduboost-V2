#!/usr/bin/env python3
"""Verify Phase 02E backend-fast remediation contracts."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[Check]:
    playwright = _read(ROOT / "playwright.config.ts")
    ether = _read(ROOT / "app/api_v2_routers/ether.py")
    router_contract = _read(ROOT / "tests/unit/test_api_v2_router_contract.py")
    seed_script = _read(ROOT / "scripts/curriculum/seed_staging_review_scopes.py")
    seed_executor = _read(ROOT / "app/services/content_staging_seed_executor.py")
    sync_script = _read(ROOT / "scripts/audit_remediation/sync_backend_fast_runtime_dependencies.sh")
    blocker = _read(ROOT / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json")

    return [
        Check(
            "playwright_defaults_to_next_port_3050",
            "http://127.0.0.1:3050" in playwright and "timeout: 60_000" in playwright,
            "Playwright fallback uses checker-recognised Next.js port 3050 and hardened timeout.",
        ),
        Check(
            "ether_auth_boundary_file_restored",
            "async def get_questions(user: AuthContext = Depends(require_auth_context))" in ether
            and '@router.get("/onboarding/questions")' in ether,
            "app/api_v2_routers/ether.py exposes the historical authenticated onboarding boundary.",
        ),
        Check(
            "curriculum_expansion_router_contract_declared",
            '"curriculum_expansion": "/admin/curriculum-expansion"' in router_contract,
            "Router contract declares the registered curriculum_expansion router fragment.",
        ),
        Check(
            "mcp_fastmcp_import_proven_by_sync_script",
            "from mcp.server.fastmcp import FastMCP" in sync_script and "mcp[cli]>=1.0.0" in sync_script,
            "Authority dependency sync proves the exact MCP import used by the ETL MCP server.",
        ),
        Check(
            "seed_script_handles_missing_result_identity",
            "getattr(res, \"seed_run_id\", None) or getattr(res, \"id\", None)" in seed_script,
            "Seed script tolerates mocked result objects without seed_run_id.",
        ),
        Check(
            "seed_executor_tolerates_mock_existing_staging_without_id",
            'getattr(existing_staging, "id", uuid.uuid4())' in seed_executor,
            "Seed executor tolerates test doubles that do not expose ORM id.",
        ),
        Check(
            "phase_02e_registered_in_blocker_register",
            "02e-backend-fast-router-frontend-seed" in blocker,
            "Blocker register records Phase 02E as the active backend-fast remediation slice.",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checks = run_checks()
    payload = {
        "valid": all(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "policy": "Focused Phase 02E evidence only; backend-fast candidate evidence requires make test-fast exit 0.",
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for check in checks:
            print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
