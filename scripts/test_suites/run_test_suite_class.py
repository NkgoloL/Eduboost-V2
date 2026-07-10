"""Run or print commands for a PRD-11.1R test-suite class."""
from __future__ import annotations

import argparse
import json
import subprocess
from scripts.test_suites.test_suite_taxonomy import DEFAULT_SUITE_COMMANDS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite_class", choices=[cmd.suite_class for cmd in DEFAULT_SUITE_COMMANDS])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    command = next(cmd for cmd in DEFAULT_SUITE_COMMANDS if cmd.suite_class == args.suite_class)
    payload = {
        "suite_class": command.suite_class,
        "command": command.command,
        "purpose": command.purpose,
        "release_blocking": command.release_blocking,
        "requires_live_stack": command.requires_live_stack,
        "executed": not args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else command.command)
        return 0
    result = subprocess.run(command.command, shell=True)
    payload["returncode"] = result.returncode
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
