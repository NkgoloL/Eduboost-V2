#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "requirements/constraints.snapshot.txt"
REPORT = ROOT / "docs/security/dependency_constraints_snapshot.md"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable, "-m", "pip", "freeze"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    OUT.write_text(result.stdout, encoding="utf-8")
    REPORT.write_text(
        "\n".join([
            "# Dependency Constraints Snapshot",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            f"Command return code: `{result.returncode}`",
            "",
            f"Snapshot: `{OUT.relative_to(ROOT)}`",
            "",
            "This is an environment snapshot, not a curated lock file. Use it to seed dependency pinning review.",
            "",
        ]),
        encoding="utf-8",
    )
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
