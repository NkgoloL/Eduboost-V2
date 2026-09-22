#!/usr/bin/env python3
"""Verify Longitudinal Educational Validation (LEV) task register integrity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify LEV task register integrity.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    regp = root / "docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json"
    errors: list[str] = []
    warnings: list[str] = []

    if not regp.exists():
        errors.append(f"missing register: {regp}")
    else:
        d = json.loads(regp.read_text())
        tasks = d.get("tasks", [])
        ids = [t.get("id") for t in tasks]
        if len(tasks) != 222:
            errors.append(f"expected 222 tasks, got {len(tasks)}")
        if len(set(ids)) != len(ids):
            errors.append("duplicate task IDs")

        known = set(ids)
        statuses = set(d.get("allowed_statuses", []))

        for t in tasks:
            cid = t.get("canonical_id")
            if cid != "LEV-" + t.get("id", ""):
                errors.append(f"bad canonical id: {cid}")
            if t.get("status") not in statuses:
                errors.append(f"{cid}: bad status {t.get('status')}")
            for dep in t.get("depends_on", []):
                if dep not in known:
                    errors.append(f"{cid}: unknown dependency {dep}")

            card = root / t.get("task_card", "")
            evp = root / t.get("task_evidence_record", "")
            if not card.exists():
                errors.append(f"{cid}: missing task card {card}")
            if not evp.exists():
                errors.append(f"{cid}: missing evidence record {evp}")
            else:
                ev = json.loads(evp.read_text())
                if ev.get("task_id") != t.get("id"):
                    errors.append(f"{cid}: evidence task mismatch")
                if ev.get("status") != t.get("status"):
                    errors.append(f"{cid}: status differs between register and evidence")
                if t.get("status") == "closed":
                    if not ev.get("evidence_files") or not ev.get("approvals"):
                        errors.append(f"{cid}: closed without evidence and approvals")
                    if t.get("cannot_be_completed_by_code_alone") and ev.get("evidence_type") != "empirical_field":
                        errors.append(f"{cid}: closed without empirical_field evidence")

            for f in t.get("existing_repository_files", []):
                if not (root / f).exists():
                    warnings.append(f"{cid}: current file no longer exists: {f}")

        # Detect direct dependency cycles.
        graph = {t["id"]: t.get("depends_on", []) for t in tasks}
        temp: set[str] = set()
        done: set[str] = set()

        def visit(n: str) -> None:
            if n in temp:
                errors.append(f"dependency cycle at {n}")
                return
            if n in done:
                return
            temp.add(n)
            for x in graph.get(n, []):
                visit(x)
            temp.remove(n)
            done.add(n)

        for n in graph:
            visit(n)

    result = {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "task_count": 222 if not errors or regp.exists() else 0,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("VALID" if result["valid"] else "INVALID\n" + "\n".join(errors))

    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
