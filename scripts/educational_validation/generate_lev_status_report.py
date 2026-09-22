#!/usr/bin/env python3
"""Generate LEV task status report markdown."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LEV status report")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    register_path = root / "docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json"
    data = json.loads(register_path.read_text())

    by: dict[str, Counter[str]] = defaultdict(Counter)
    for task in data["tasks"]:
        by[task["workstream_id"]][task["status"]] += 1

    lines = [
        "# LEV Status Report",
        "",
        f"Total tasks: {len(data['tasks'])}",
        "",
        "| Workstream | Not started | Blocked | In progress | Candidate | Evidence | Review | Closed | Waived |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for ws in sorted(by):
        c = by[ws]
        lines.append(
            f"| {ws} | {c['not_started']} | {c['blocked']} | {c['in_progress']} | "
            f"{c['candidate_complete']} | {c['evidence_recorded']} | {c['independent_review']} | "
            f"{c['closed']} | {c['waived']} |"
        )

    text = "\n".join(lines) + "\n"
    out = Path(args.output) if args.output else root / "docs/roadmap/production_readiness/lev/status_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(out)


if __name__ == "__main__":
    main()
