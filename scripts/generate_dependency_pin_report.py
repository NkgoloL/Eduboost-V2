#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/security/dependency_pin_report.json"
OUT_MD = ROOT / "docs/security/dependency_pin_report.md"
REQUIREMENT_FILES = [
    ROOT / "requirements.txt",
    ROOT / "requirements/base.txt",
    ROOT / "requirements/dev.txt",
    ROOT / "requirements/prod.txt",
    ROOT / "requirements/production.txt",
    ROOT / "requirements/test.txt",
]
PIN_RE = re.compile(r"^[A-Za-z0-9_.-]+(?:\[[^\]]+\])?==[^#\s]+")
COMMENT_OR_OPTION_RE = re.compile(r"^\s*(#|--|-r\s+|-c\s+|$)")


def classify_line(line: str) -> str:
    stripped = line.strip()
    if COMMENT_OR_OPTION_RE.match(stripped):
        return "ignored"
    if PIN_RE.match(stripped):
        return "pinned"
    if any(op in stripped for op in (">=", "~=", ">", "<", "!=")):
        return "range_or_unpinned"
    if stripped:
        return "unpinned"
    return "ignored"


def main() -> int:
    rows = []
    blockers = []
    for path in REQUIREMENT_FILES:
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            classification = classify_line(line)
            if classification in {"range_or_unpinned", "unpinned"}:
                blockers.append(f"{path.relative_to(ROOT)}:{lineno}: {line.strip()}")
            rows.append({"file": str(path.relative_to(ROOT)), "line": lineno, "classification": classification, "text": line.strip()})

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass" if not blockers else "blocked_unpinned_dependencies",
        "blockers": blockers,
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = ["# Dependency Pin Report", "", f"Generated at: `{payload['generated_at']}`", "", f"**Status:** {payload['status']}", "", "## Blockers", ""]
    lines.extend(f"- `{item}`" for item in blockers)
    if not blockers:
        lines.append("- None")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
