#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

MOVE_DIR_RULES = [
    ("docs/DOC", "docs/archive/legacy-doc-framework/{run_id}/DOC", "Formal DOC framework archived; canonical docs now live under docs/<topic>/ and docs/documentation/source_of_truth.yml."),
    ("docs/api/_build", "docs/generated/api-doc-builds/{run_id}/_build", "Generated Sphinx/API build output moved out of active API docs."),
    ("docs/api/build", "docs/generated/api-doc-builds/{run_id}/build", "Generated Sphinx/API build output moved out of active API docs."),
    ("docs/release/superseded", "docs/archive/release/superseded/{run_id}", "Superseded release documents archived away from active release surface."),
    ("docs/todos", "docs/archive/roadmaps-or-todos/{run_id}/todos", "Legacy TODO documents archived pending merge into canonical roadmap/backlog."),
    ("docs/patches", "docs/archive/patches/{run_id}/patches", "Patch notes archived after application."),
    ("docs/input", "docs/archive/imported-inputs/{run_id}/input", "Imported input documents archived and removed from active source-of-truth surface."),
    ("docs/pr", "docs/archive/pr-notes/{run_id}/pr", "PR notes archived as historical process records."),
]

MOVE_FILE_PATTERNS = [
    ("docs/docs_inventory.md", "docs/generated/legacy-inventories/{run_id}/docs_inventory.md", "Legacy generated inventory moved to generated documentation area."),
    ("docs/release/audit_callsite_inventory.md", "docs/generated/release-inventories/{run_id}/audit_callsite_inventory.md", "Generated release inventory moved to generated documentation area."),
    ("docs/release/consent_callsite_inventory.md", "docs/generated/release-inventories/{run_id}/consent_callsite_inventory.md", "Generated release inventory moved to generated documentation area."),
]

CANONICAL_DIRS = [
    "docs/documentation/migration_manifests",
    "docs/product",
    "docs/architecture",
    "docs/engineering",
    "docs/api",
    "docs/compliance",
    "docs/security",
    "docs/operations",
    "docs/release/current",
    "docs/generated",
    "docs/archive",
    "artifacts/evidence",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_redirect_stub(path: Path) -> bool:
    if path.is_file():
        try:
            return "Moved by EduBoost documentation housekeeping" in path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return False
    if path.is_dir():
        entries = [p.name for p in path.iterdir()]
        if entries == ["README.md"]:
            return is_redirect_stub(path / "README.md")
    return False


def write_stub(path: Path, original_rel: str, new_rel: str, reason: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    stub = path / "README.md"
    stub.write_text(f"""---
title: Archived documentation redirect
status: archived
owner: documentation-governance
reviewers: [release-management]
audience: reviewer
source_of_truth: false
supersedes: []
superseded_by: {new_rel}
last_reviewed: 2026-06-22
review_interval_days: 180
evidence_command: make docs-housekeeping-check
code_anchors: [docs/documentation/migration_manifests]
---

# Archived documentation redirect

Moved by EduBoost documentation housekeeping.

- Original path: `{original_rel}`
- New path: `{new_rel}`
- Reason: {reason}

This path is retained as a redirect stub only. It is not a current source-of-truth document.
""", encoding="utf-8")


def write_file_stub(path: Path, original_rel: str, new_rel: str, reason: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"""---
title: Archived documentation redirect
status: archived
owner: documentation-governance
reviewers: [release-management]
audience: reviewer
source_of_truth: false
supersedes: []
superseded_by: {new_rel}
last_reviewed: 2026-06-22
review_interval_days: 180
evidence_command: make docs-housekeeping-check
code_anchors: [docs/documentation/migration_manifests]
---

# Archived documentation redirect

Moved by EduBoost documentation housekeeping.

- Original path: `{original_rel}`
- New path: `{new_rel}`
- Reason: {reason}

This file is retained as a redirect stub only. It is not a current source-of-truth document.
""", encoding="utf-8")


def move_dir(root: Path, src_rel: str, dest_rel_template: str, reason: str, run_id: str, apply: bool, manifest: list[dict[str, object]]) -> None:
    src = root / src_rel
    dest_rel = dest_rel_template.format(run_id=run_id)
    dest = root / dest_rel
    entry = {"type": "directory", "original_path": src_rel, "new_path": dest_rel, "reason": reason, "action": "skipped", "redirect_stub": False}
    if not src.exists():
        entry["detail"] = "source missing"
        manifest.append(entry)
        return
    if is_redirect_stub(src):
        entry["detail"] = "source is already a redirect stub"
        manifest.append(entry)
        return
    if dest.exists():
        suffix = 1
        while (root / f"{dest_rel}-{suffix}").exists():
            suffix += 1
        dest_rel = f"{dest_rel}-{suffix}"
        dest = root / dest_rel
        entry["new_path"] = dest_rel
    entry["action"] = "move"
    entry["redirect_stub"] = True
    manifest.append(entry)
    if apply:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        write_stub(src, src_rel, dest_rel, reason)


def move_file(root: Path, src_rel: str, dest_rel_template: str, reason: str, run_id: str, apply: bool, manifest: list[dict[str, object]]) -> None:
    src = root / src_rel
    dest_rel = dest_rel_template.format(run_id=run_id)
    dest = root / dest_rel
    entry = {"type": "file", "original_path": src_rel, "new_path": dest_rel, "reason": reason, "action": "skipped", "redirect_stub": False}
    if not src.exists():
        entry["detail"] = "source missing"
        manifest.append(entry)
        return
    if is_redirect_stub(src):
        entry["detail"] = "source is already a redirect stub"
        manifest.append(entry)
        return
    if dest.exists():
        suffix = 1
        while (root / f"{dest_rel}-{suffix}").exists():
            suffix += 1
        dest_rel = f"{dest_rel}-{suffix}"
        dest = root / dest_rel
        entry["new_path"] = dest_rel
    entry["action"] = "move"
    entry["redirect_stub"] = True
    manifest.append(entry)
    if apply:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        write_file_stub(src, src_rel, dest_rel, reason)


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply EduBoost documentation housekeeping moves.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--run-id", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest: list[dict[str, object]] = []

    for rel in CANONICAL_DIRS:
        entry = {"type": "directory", "original_path": rel, "new_path": rel, "reason": "Ensure canonical directory exists", "action": "mkdir", "redirect_stub": False}
        manifest.append(entry)
        if args.apply:
            (root / rel).mkdir(parents=True, exist_ok=True)

    for src_rel, dest_template, reason in MOVE_DIR_RULES:
        move_dir(root, src_rel, dest_template, reason, args.run_id, args.apply, manifest)

    for src_rel, dest_template, reason in MOVE_FILE_PATTERNS:
        move_file(root, src_rel, dest_template, reason, args.run_id, args.apply, manifest)

    output = {
        "run_id": args.run_id,
        "generated_at": now_iso(),
        "mode": "apply" if args.apply else "dry-run",
        "repository": str(root),
        "notes": [
            "No documents are deleted by this script.",
            "docs/release-evidence is intentionally left in place because Phase 02R evidence automation currently depends on stable paths.",
            "Redirect stubs are not source-of-truth documents.",
        ],
        "actions": manifest,
    }

    manifest_path = root / f"docs/documentation/migration_manifests/{args.run_id}.json"
    if args.apply:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
