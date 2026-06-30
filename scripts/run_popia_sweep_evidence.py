#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/release/popia_sweep_evidence.md"

def main() -> int:
    script = ROOT / "scripts/popia_sweep.py"
    if not script.exists():
        OUT.write_text("# POPIA Sweep Evidence\n\n**Status:** pending — `scripts/popia_sweep.py` not found.\n", encoding="utf-8")
        print(f"Wrote {OUT.relative_to(ROOT)}")
        return 0

    cmd = [sys.executable, "scripts/popia_sweep.py", "--fail-on-issues"]
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    OUT.write_text(
        f"# POPIA Sweep Evidence\n\nGenerated: `{datetime.now(timezone.utc).isoformat()}`\n\n"
        f"Command: `{' '.join(cmd)}`\n\nReturn code: `{result.returncode}`\n\n"
        f"```text\n{result.stdout}\n```\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return result.returncode

if __name__ == "__main__":
    raise SystemExit(main())
