"""List documentation-defined coverage commands by class."""
from __future__ import annotations

import argparse
import json
from scripts.coverage_suites.coverage_contract import coverage_commands


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("coverage_class", choices=("product", "runtime", "governance", "advisory"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    commands = [item for item in coverage_commands() if item["coverage_class"] == args.coverage_class]
    result = {"coverage_class": args.coverage_class, "dry_run": args.dry_run, "commands": commands}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if commands else 1


if __name__ == "__main__":
    raise SystemExit(main())
