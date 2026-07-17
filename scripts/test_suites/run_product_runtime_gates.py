"""List or run PRD-11.0R product/runtime gate commands.

By default this script is read-only and lists the commands that must provide
independent evidence.  Use --execute intentionally; CI can wire exact commands
once the relevant runtime stack exists.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from typing import Any

from scripts.test_suites.product_runtime_gate import evaluate_product_runtime_gate_contract, load_contract, ROOT


def _commands_for(gate_class: str) -> list[dict[str, Any]]:
    contract = load_contract(ROOT)
    domains = contract.get("domains", []) if isinstance(contract.get("domains"), list) else []
    return [item for item in domains if isinstance(item, dict) and item.get("class") == gate_class]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gate_class", choices=["product", "runtime", "all"])
    parser.add_argument("--dry-run", action="store_true", help="List commands without running them.")
    parser.add_argument("--execute", action="store_true", help="Run configured commands. Use intentionally.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    classes = ["product", "runtime"] if args.gate_class == "all" else [args.gate_class]
    contract = evaluate_product_runtime_gate_contract(ROOT)
    selected = [command for gate_class in classes for command in _commands_for(gate_class)]
    results: list[dict[str, Any]] = []
    if args.execute:
        for item in selected:
            completed = subprocess.run(str(item["command"]), shell=True, cwd=ROOT)  # nosec B602
            results.append({"id": item.get("id"), "class": item.get("class"), "command": item.get("command"), "returncode": completed.returncode})
    payload = {
        "valid": contract.get("valid") is True and (not args.execute or all(item["returncode"] == 0 for item in results)),
        "contract_valid": contract.get("valid") is True,
        "mode": "execute" if args.execute else "dry_run",
        "selected_classes": classes,
        "commands": selected,
        "results": results,
        "release_claim_allowed": False,
        "reason": "Product/runtime command outputs must be captured separately before release readiness can be claimed.",
    }
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
