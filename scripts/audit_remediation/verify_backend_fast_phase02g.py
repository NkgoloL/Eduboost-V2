#!/usr/bin/env python3
"""Verify TA Phase 02G POPIA async-session and route-contract remediation."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def verify() -> dict[str, object]:
    errors: list[str] = []

    popia_service = _read("app/services/popia_service.py")
    learner_repo = _read("app/repositories/learner_repository.py")
    blocker_register = _read("docs/roadmap/execution/technical_audit_remediation/blocker_register.json")

    required_snippets = [
        "import inspect",
        "async def _maybe_await(value: Any) -> Any:",
        "async def _add(self, *objects: Any) -> None:",
        "await _maybe_await(self.db.add(obj))",
        "await self._add(erasure_request)",
        "await self._add(learner)",
    ]
    for snippet in required_snippets:
        if snippet not in popia_service:
            errors.append(f"popia_service.py missing required snippet: {snippet}")

    direct_service_adds = [
        line for line in popia_service.splitlines()
        if "self.db.add(" in line and "await _maybe_await" not in line
    ]
    if direct_service_adds:
        errors.append("popia_service.py still has direct self.db.add calls outside the async-safe helper")

    if "import inspect" not in learner_repo:
        errors.append("learner_repository.py must import inspect")
    if "add_result = db.add(learner)" not in learner_repo:
        errors.append("LearnerRepository.soft_delete must capture db.add result")
    if "if inspect.isawaitable(add_result):" not in learner_repo or "await add_result" not in learner_repo:
        errors.append("LearnerRepository.soft_delete must await AsyncMock-backed db.add results")

    if "phase_02g_slice" not in blocker_register:
        errors.append("blocker_register.json missing phase_02g_slice entry")
    if "popia_async_route_contract" not in blocker_register:
        errors.append("blocker_register.json missing POPIA Phase 02G failure category")

    return {"valid": not errors, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print("Phase 02G POPIA async route-contract verification passed")
    else:
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
