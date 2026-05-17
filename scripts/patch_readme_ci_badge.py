#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
OWNER_REPO = "nkgolomatjila-svg/Eduboost_V.2"
WORKFLOW = "ci-cd.yml"

def main() -> int:
    if not README.exists():
        print("README.md not found; skipping badge patch.")
        return 0

    text = README.read_text(encoding="utf-8")
    original = text
    text = re.sub(
        r"https://github\.com/[^/\s)]+/[^/\s)]+/actions/workflows/([^/\s)]+)/badge\.svg(?:\?branch=[^\s)]*)?",
        f"https://github.com/{OWNER_REPO}/actions/workflows/\\1/badge.svg?branch=master",
        text,
    )
    text = re.sub(
        r"https://github\.com/[^/\s)]+/[^/\s)]+/actions/workflows/([^/\s)]+)",
        f"https://github.com/{OWNER_REPO}/actions/workflows/\\1",
        text,
    )

    if "actions/workflows" not in text:
        badge = f"[![CI/CD](https://github.com/{OWNER_REPO}/actions/workflows/{WORKFLOW}/badge.svg?branch=master)](https://github.com/{OWNER_REPO}/actions/workflows/{WORKFLOW})\n\n"
        text = badge + text

    if text != original:
        README.write_text(text, encoding="utf-8")
        print("Patched README CI badge to this fork.")
    else:
        print("README CI badge unchanged.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
