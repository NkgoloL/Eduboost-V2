#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

RENAME_MAP = {
    "docs/adr/ADR-033-learner-tutor-safety-boundary.md": "docs/adr/ADR-033-learner-tutor-safety-boundary.md",
    "docs/adr/ADR-034-irt-quality-self-healing.md": "docs/adr/ADR-034-irt-quality-self-healing.md",
}
H1_MAP = {
    "# ADR-033 — Learner Tutor Safety and Context Boundary": "# ADR-033 — Learner Tutor Safety and Context Boundary",
    "# ADR-034 — IRT Quality and Self-Healing Controls": "# ADR-034 — IRT Quality and Self-Healing Controls",
    "# ADR-033 - Learner Tutor Safety and Context Boundary": "# ADR-033 - Learner Tutor Safety and Context Boundary",
    "# ADR-034 - IRT Quality and Self-Healing Controls": "# ADR-034 - IRT Quality and Self-Healing Controls",
}
REFERENCE_MAP = {old: new for old, new in RENAME_MAP.items()}
REFERENCE_MAP.update({
    "ADR-033-learner-tutor-safety-boundary.md": "ADR-033-learner-tutor-safety-boundary.md",
    "ADR-034-irt-quality-self-healing.md": "ADR-034-irt-quality-self-healing.md",
})


def has_front_matter(text: str) -> bool:
    return text.startswith("---\n") and "\n---\n" in text[4:]


def title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def quote_yaml(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def metadata_for(path: Path, root: Path, text: str) -> str:
    rel = path.relative_to(root).as_posix()
    title = title_from_text(text, path.stem.replace("-", " ").strip())
    owner = "frontend" if "/frontend/" in rel else "architecture"
    if rel == "README.md":
        owner = "product"
    if rel.startswith("docs/documentation/"):
        owner = "documentation-governance"
    status = "template" if path.name.upper() == "TEMPLATE.MD" else "active"
    reviewers = "[engineering, architecture]"
    if owner == "frontend":
        reviewers = "[frontend, architecture]"
    elif owner == "documentation-governance":
        reviewers = "[engineering, release-management]"
    elif owner == "product":
        reviewers = "[product, engineering, privacy]"
    return "\n".join([
        "---",
        f"title: {quote_yaml(title)}",
        f"status: {status}",
        f"owner: {owner}",
        f"reviewers: {reviewers}",
        "audience: developer",
        "source_of_truth: false",
        "supersedes: []",
        "superseded_by: null",
        "last_reviewed: 2026-06-23",
        "review_interval_days: 180",
        "evidence_command: make docs-housekeeping-stage3-check",
        "code_anchors: []",
        "---",
        "",
    ])


def prepend_metadata(path: Path, root: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if has_front_matter(text):
        return False
    path.write_text(metadata_for(path, root, text) + text, encoding="utf-8", newline="\n")
    return True


def update_references(root: Path) -> int:
    changed = 0
    patterns = ["*.md", "*.py", "*.yml", "*.yaml", "*.json", "*.txt"]
    files: set[Path] = set()
    for pattern in patterns:
        files.update(root.rglob(pattern))
    skip_parts = {".git", "node_modules", ".venv", "venv"}
    for path in sorted(files):
        if any(part in skip_parts for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = text
        for old, replacement in REFERENCE_MAP.items():
            new = new.replace(old, replacement)
        new = new.replace("[Frontend spike report template](../frontend/spike_report_template.md)", "[Frontend spike report template](../frontend/spike_report_template.md)")
        for old, replacement in H1_MAP.items():
            new = new.replace(old, replacement)
        if new != text:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def rename_duplicates(root: Path) -> int:
    count = 0
    for old_rel, new_rel in RENAME_MAP.items():
        old = root / old_rel
        new = root / new_rel
        if old.exists():
            new.parent.mkdir(parents=True, exist_ok=True)
            if new.exists():
                old.unlink()
            else:
                shutil.move(str(old), str(new))
            count += 1
    return count


def update_adr_readme(root: Path) -> None:
    path = root / "docs/adr/README.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    note = """
## Stage 3 ADR numbering rule

ADR numbers in `docs/adr/*.md` must be unique. Stage 3 resolved the prior duplicate root-level `ADR-030` and `ADR-031` numbers by preserving the original decisions and renumbering the later conflicting records to `ADR-033` and `ADR-034`.

Run `make docs-housekeeping-stage3-check` before merging ADR changes.
""".strip()
    if "## Stage 3 ADR numbering rule" not in text:
        text = text.rstrip() + "\n\n" + note + "\n"
        path.write_text(text, encoding="utf-8", newline="\n")


def update_source_of_truth(root: Path) -> None:
    path = root / "docs/documentation/source_of_truth.yml"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if "docs/documentation/stage_3_documentation_housekeeping.md" not in text:
        needle = "      - docs/documentation/stale_documentation_register.md\n"
        replacement = needle + "      - docs/documentation/stage_3_documentation_housekeeping.md\n      - docs/documentation/stage_3_strict_scope.json\n"
        text = text.replace(needle, replacement)
    text = re.sub(r"last_reviewed: 2026-06-22", "last_reviewed: 2026-06-23", text, count=1)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Stage 3 documentation cleanup tranche 1.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    renamed = rename_duplicates(root)
    refs = update_references(root)
    metadata = 0
    metadata_paths = []
    if (root / "docs/adr").exists():
        metadata_paths.extend(sorted((root / "docs/adr").rglob("*.md"), key=lambda p: p.as_posix()))
    if (root / "docs/documentation").exists():
        metadata_paths.extend(sorted((root / "docs/documentation").rglob("*.md"), key=lambda p: p.as_posix()))
    if (root / "README.md").exists():
        metadata_paths.append(root / "README.md")
    for path in metadata_paths:
        metadata += 1 if prepend_metadata(path, root) else 0
    update_adr_readme(root)
    update_source_of_truth(root)
    print(json.dumps({"renamed_files": renamed, "reference_files_changed": refs, "metadata_added": metadata}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
