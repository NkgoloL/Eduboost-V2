#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch root README documentation links after Stage 2 housekeeping.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    readme = root / "README.md"
    if not readme.exists():
        print("Root README.md not found; skipping.")
        return 0
    text = readme.read_text(encoding="utf-8")
    original = text
    text = replace_once(
        text,
        "[`docs/current_state.md`](/docs/current_state.md), [`docs/project_status.md`](/docs/project_status.md), and the root\n[`docs/todos/todo.md`](/docs/todos/todo.md) live tracker.",
        "[`docs/current_state.md`](/docs/current_state.md), [`docs/project_status.md`](/docs/project_status.md), and\n[`docs/documentation/source_of_truth.yml`](docs/documentation/source_of_truth.yml).",
    )
    text = replace_once(
        text,
        "- Status index: [`docs/project_status.md`](/docs/project_status.md)",
        "- Status index: [`docs/project_status.md`](/docs/project_status.md)\n- Documentation source-of-truth register: [`docs/documentation/source_of_truth.yml`](docs/documentation/source_of_truth.yml)\n- Documentation housekeeping policy: [`docs/documentation/documentation_housekeeping_policy.md`](docs/documentation/documentation_housekeeping_policy.md)",
    )
    if text != original:
        readme.write_text(text, encoding="utf-8")
        print("Patched root README documentation links.")
    else:
        print("Root README documentation links already patched or expected block not found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
