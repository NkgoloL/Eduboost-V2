#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/architecture/import_linter_availability.md"


def main() -> int:
    executable = shutil.which("lint-imports")
    status = "available" if executable else "missing"
    lines = [
        "# Import-Linter Availability",
        "",
        f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        f"**Status:** {status}",
        "",
    ]
    if executable:
        result = subprocess.run(["lint-imports", "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        lines.extend(["```text", result.stdout.strip(), "```", ""])
    else:
        lines.extend([
            "Install in the active project virtual environment before Phase 1 strict import contracts:",
            "",
            "```bash",
            "python -m pip install import-linter",
            "```",
            "",
        ])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
