#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/release/warning_integrity_evidence.md"

def main() -> int:
    cmd = [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit", "-q", "--no-cov", "-W", "error::RuntimeWarning"]
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        f"# Warning Integrity Evidence\n\nGenerated: `{datetime.now(timezone.utc).isoformat()}`\n\n"
        f"Command: `{' '.join(cmd)}`\n\nReturn code: `{result.returncode}`\n\n"
        f"```text\n{result.stdout}\n```\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return result.returncode

if __name__ == "__main__":
    raise SystemExit(main())
