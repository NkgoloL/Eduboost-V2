#!/usr/bin/env python3
"""Apply PRD-0.6 workflow command hygiene transformations.

This script deliberately performs narrow workflow hygiene only:
- direct `pytest ...` command invocations become `PYTHONPATH=. python3 -m pytest ...`
- existing `python -m pytest` / `python3 -m pytest` commands are preserved
- comments and pip-install dependency lines are preserved
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

DIRECT_PYTEST_RE = re.compile(r"(?<![-\w.])pytest(\s|$)")
MODULE_PYTEST_RE = re.compile(r"python3?\s+-m\s+pytest")


def is_direct_pytest_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if MODULE_PYTEST_RE.search(line):
        return False
    if "pip install" in line and "pytest" in line:
        return False
    return bool(DIRECT_PYTEST_RE.search(line))


def rewrite_line(line: str) -> tuple[str, bool]:
    if not is_direct_pytest_line(line):
        return line, False
    if "run: pytest" in line:
        return line.replace("run: pytest", "run: PYTHONPATH=. python3 -m pytest", 1), True
    return DIRECT_PYTEST_RE.sub(lambda match: "PYTHONPATH=. python3 -m pytest" + match.group(1), line, count=1), True


def rewrite_workflow(path: Path) -> dict[str, Any]:
    original = path.read_text(encoding="utf-8")
    changed_lines: list[int] = []
    new_lines: list[str] = []
    for idx, line in enumerate(original.splitlines(keepends=True), start=1):
        rewritten, changed = rewrite_line(line)
        if changed:
            changed_lines.append(idx)
        new_lines.append(rewritten)
    new_text = "".join(new_lines)
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")
    return {"path": str(path), "changed": new_text != original, "changed_lines": changed_lines}


def apply(root: Path) -> dict[str, Any]:
    workflow_root = root / ".github" / "workflows"
    workflows = sorted(workflow_root.glob("*.yml")) + sorted(workflow_root.glob("*.yaml")) if workflow_root.exists() else []
    results = [rewrite_workflow(path) for path in workflows]
    changed = [item for item in results if item["changed"]]
    return {"workflow_count": len(workflows), "changed_workflow_count": len(changed), "changed_workflows": changed}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = apply(Path(args.root))
    if args.json:
        import json
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.6 workflow hygiene changed {result['changed_workflow_count']} workflow(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
