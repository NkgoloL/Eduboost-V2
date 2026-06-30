#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app/api_v2_routers/popia.py"
REPORT = ROOT / "docs/release/popia_consent_lifecycle_repair_report.md"
LIFECYCLE_TOKENS = ("grant_consent", "deny_consent", "withdraw_consent", "renew_consent")


def _function_block_text(source: str, node: ast.AST) -> str:
    lines = source.splitlines()
    return "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])


def main() -> int:
    failures: list[str] = []
    print("POPIA consent lifecycle repair check")

    source = ROUTER.read_text(encoding="utf-8")
    tree = ast.parse(source)

    if "app.services.consent_service" in source:
        print("- FAIL deprecated consent service import still present")
        failures.append("deprecated consent service import")
    else:
        print("- PASS deprecated consent service import absent")

    if "app.modules.consent.service" in source:
        print("- PASS canonical consent service import present")
    else:
        print("- FAIL canonical consent service import missing")
        failures.append("canonical consent service import")

    if "Depends(lambda: uuid.uuid4())" in source:
        print("- FAIL generated actor UUID dependency still present")
        failures.append("generated actor dependency")
    else:
        print("- PASS generated actor UUID dependency absent")

    if "get_canonical_consent_service" in source:
        print("- PASS canonical consent dependency helper present")
    else:
        print("- FAIL canonical consent dependency helper missing")
        failures.append("canonical consent dependency helper")

    lifecycle_functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
        and any(token in node.name for token in LIFECYCLE_TOKENS)
    ]
    if lifecycle_functions:
        print(f"- PASS lifecycle functions found: {[node.name for node in lifecycle_functions]}")
    else:
        print("- FAIL no lifecycle functions found")
        failures.append("no lifecycle functions")

    for node in lifecycle_functions:
        block = _function_block_text(source, node)
        args = [arg.arg for arg in node.args.args + node.args.kwonlyargs]
        if "current_user" not in args:
            print(f"- FAIL {node.name}: current_user dependency missing")
            failures.append(f"{node.name} current_user")
        else:
            print(f"- PASS {node.name}: current_user dependency present")
        if "_enforce_popia_learner_write" not in block:
            print(f"- FAIL {node.name}: learner-write enforcement missing")
            failures.append(f"{node.name} learner-write")
        else:
            print(f"- PASS {node.name}: learner-write enforcement present")
        if "_authenticated_actor_id" not in block:
            print(f"- FAIL {node.name}: authenticated actor extraction missing")
            failures.append(f"{node.name} actor")
        else:
            print(f"- PASS {node.name}: authenticated actor extraction present")

    if REPORT.exists():
        print("- PASS repair report exists")
    else:
        print("- FAIL repair report missing")
        failures.append("repair report")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS POPIA consent lifecycle repair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
