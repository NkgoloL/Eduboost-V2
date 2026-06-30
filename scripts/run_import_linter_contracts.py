#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/architecture/import_linter_contract_run.md"


def main() -> int:
    executable = shutil.which("lint-imports")
    lines = [
        "# Import-Linter Contract Run",
        "",
        f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
    ]

    if not executable:
        lines.extend([
            "**Status:** skipped_missing_tool",
            "",
            "Install `import-linter` in the project virtual environment to enforce `.importlinter` contracts in CI.",
            "",
        ])
        OUT.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {OUT.relative_to(ROOT)}")
        return 0

    result = subprocess.run(["lint-imports"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    lines.extend([
        f"**Status:** {'pass' if result.returncode == 0 else 'fail'}",
        "",
        "```text",
        result.stdout.rstrip(),
        "```",
        "",
    ])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
