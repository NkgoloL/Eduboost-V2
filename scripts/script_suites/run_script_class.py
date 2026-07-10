"""List or run scripts by PRD-11.2R script taxonomy class."""
from __future__ import annotations

import argparse
import json
from scripts.script_suites.script_taxonomy import DEFAULT_SCRIPT_COMMANDS, inventory_scripts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("script_class", choices=[cmd.script_class for cmd in DEFAULT_SCRIPT_COMMANDS])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    inventory = [item for item in inventory_scripts() if item["script_class"] == args.script_class]
    command = next(cmd for cmd in DEFAULT_SCRIPT_COMMANDS if cmd.script_class == args.script_class)
    payload = {
        "script_class": args.script_class,
        "purpose": command.purpose,
        "release_blocking": command.release_blocking,
        "requires_live_stack": command.requires_live_stack,
        "executed": False,
        "count": len(inventory),
        "scripts": inventory,
    }
    # PRD-11.2R intentionally lists scripts rather than executing arbitrary helpers.
    # Execution orchestration is handled by the later runtime/coverage restoration gates.
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "\n".join(item["path"] for item in inventory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
