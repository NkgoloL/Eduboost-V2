#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/security/pip_audit_report.md"


def main() -> int:
    exe = shutil.which("pip-audit")
    lines = ["# pip-audit Report", "", f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`", ""]
    if exe is None:
        lines.extend([
            "**Status:** skipped_missing_tool",
            "",
            "Install in the project virtual environment to run:",
            "",
            "```bash",
            "python -m pip install pip-audit",
            "pip-audit",
            "```",
            "",
        ])
        OUT.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {OUT.relative_to(ROOT)}")
        return 0

    result = subprocess.run([exe], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    lines.extend([f"**Status:** {'pass' if result.returncode == 0 else 'findings'}", "", "```text", result.stdout.rstrip(), "```", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
