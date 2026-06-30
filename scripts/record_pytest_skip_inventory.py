#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/pytest_skip_inventory.json"
OUT_MD = ROOT / "docs/release/pytest_skip_inventory.md"


def parse_summary(output: str) -> dict[str, int]:
    summary = {"passed": 0, "failed": 0, "skipped": 0, "warnings": 0}
    patterns = {
        "passed": r"(\d+)\s+passed",
        "failed": r"(\d+)\s+failed",
        "skipped": r"(\d+)\s+skipped",
        "warnings": r"(\d+)\s+warnings?",
    }
    for key, pattern in patterns.items():
        matches = re.findall(pattern, output)
        if matches:
            summary[key] = int(matches[-1])
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-evidence", action="store_true", help="write docs/release skip inventory")
    parser.add_argument("--pytest-args", nargs=argparse.REMAINDER, default=[])
    args = parser.parse_args()

    pytest_args = args.pytest_args or ["-c", "pytest.ini", "-q", "--no-cov"]
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *pytest_args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(result.stdout)

    summary = parse_summary(result.stdout)
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "returncode": result.returncode,
        "summary": summary,
        "policy": "Skipped tests are not-proven and cannot be used as closure evidence.",
        "command": " ".join([sys.executable, "-m", "pytest", *pytest_args]),
    }

    if args.write_evidence:
        OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        OUT_MD.write_text(
            "\n".join(
                [
                    "# Pytest Skip Inventory",
                    "",
                    f"Generated at: `{payload['generated_at']}`",
                    "",
                    f"- Passed: `{summary['passed']}`",
                    f"- Failed: `{summary['failed']}`",
                    f"- Skipped: `{summary['skipped']}`",
                    "",
                    "**Policy:** skipped tests are `not-proven`, not passing proof.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
        print(f"Wrote {OUT_MD.relative_to(ROOT)}")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
