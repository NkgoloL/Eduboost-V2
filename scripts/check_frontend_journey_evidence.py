#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "app/frontend/src/lib/api/client.ts",
    "app/frontend/src/lib/api/services.ts",
    "app/frontend/src/components/eduboost/RouteGuard.tsx",
    "docs/frontend/frontend_api_client_inventory.md",
    "docs/frontend/frontend_auth_consent_denial_contract.md",
    "docs/frontend/learner_vertical_journey_contract.md",
    "docs/frontend/parent_vertical_journey_contract.md",
    "tests/fixtures/frontend/learner_journey_fixture.json",
    "tests/fixtures/frontend/parent_journey_fixture.json",
    "app/frontend/src/__tests__/ApiLayer.test.ts",
    "app/frontend/src/__tests__/LearnerJourneys.test.ts",
)


@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def check_all() -> list[Result]:
    return [Result(p, (ROOT / p).exists(), "present" if (ROOT / p).exists() else "missing") for p in REQUIRED]


def main() -> int:
    results = check_all()
    print("Frontend journey evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
