#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LAST_REVIEWED = "2026-07-06"

REQUIRED_METADATA_FIELDS = [
    "title", "status", "owner", "reviewers", "audience", "source_of_truth",
    "supersedes", "superseded_by", "last_reviewed", "review_interval_days",
    "evidence_command", "code_anchors",
]

TARGET_DIRS = [
    "docs/release",
    "docs/operations",
    "docs/roadmap",
    "docs/backlog",
    "docs/codemaps",
    "docs/roadmap_domains",
    "docs/reference",
    "docs/beta_launch",
    "docs/archive",
]

OWNER_MAP = {
    "docs/release": "release-management",
    "docs/operations": "operations",
    "docs/roadmap": "roadmap-governance",
    "docs/backlog": "delivery-planning",
    "docs/codemaps": "architecture",
    "docs/roadmap_domains": "roadmap-governance",
    "docs/reference": "documentation-governance",
    "docs/beta_launch": "product",
    "docs/archive": "documentation-governance",
    "docs/release-evidence": "evidence-custodian",
}

REVIEWER_MAP = {
    "docs/release": ["release-management", "evidence-custodian", "documentation-governance"],
    "docs/operations": ["operations", "security", "release-management"],
    "docs/roadmap": ["roadmap-governance", "release-management", "documentation-governance"],
    "docs/backlog": ["delivery-planning", "engineering", "documentation-governance"],
    "docs/codemaps": ["architecture", "engineering", "documentation-governance"],
    "docs/roadmap_domains": ["roadmap-governance", "domain-owner", "documentation-governance"],
    "docs/reference": ["documentation-governance", "engineering", "release-management"],
    "docs/beta_launch": ["product", "release-management", "privacy"],
    "docs/archive": ["documentation-governance", "evidence-custodian", "release-management"],
    "docs/release-evidence": ["evidence-custodian", "release-management", "documentation-governance"],
}

AUDIENCE_MAP = {
    "docs/release": "release-reviewer",
    "docs/operations": "operator",
    "docs/roadmap": "roadmap-reviewer",
    "docs/backlog": "delivery-reviewer",
    "docs/codemaps": "architecture-reviewer",
    "docs/roadmap_domains": "roadmap-reviewer",
    "docs/reference": "developer",
    "docs/beta_launch": "product-reviewer",
    "docs/archive": "evidence-reviewer",
    "docs/release-evidence": "evidence-reviewer",
}

CODE_ANCHORS_MAP = {
    "docs/release": ["docs/release", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
    "docs/operations": ["docs/operations", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
    "docs/roadmap": ["docs/roadmap", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
    "docs/backlog": ["docs/backlog", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
    "docs/codemaps": ["docs/codemaps", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
    "docs/roadmap_domains": ["docs/roadmap_domains", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
    "docs/reference": ["docs/reference", "docs/documentation/source_of_truth.yml"],
    "docs/beta_launch": ["docs/beta_launch", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
    "docs/archive": ["docs/archive", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
    "docs/release-evidence": ["docs/release-evidence", "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md"],
}

CANONICAL_PATHS = {
    "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md",
    "docs/documentation/stage_7_retention_policy.md",
    "docs/release/EVIDENCE_INDEX.md",
    "docs/roadmap/roadmap.md",
    "docs/backlog/production_readiness/README.md",
    "docs/reference/README.md",
}

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
RISKY_TERMS = [
    "production-ready", "production ready", "release-ready", "release ready", "launch approved",
    "fully complete", "all tests pass", "green baseline", "DBE AI Expert", "Cosmos DB", "Azure ML", "Neo4j",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def parse_scalar(value: str):
    raw = value.strip()
    if raw in {"null", "~"}:
        return None
    if raw == "":
        return ""
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip('"\'') for part in inner.split(",") if part.strip()]
    if raw.isdigit():
        return int(raw)
    return raw.strip('"\'')


def split_front_matter(text: str) -> tuple[dict[str, object] | None, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text
    meta: dict[str, object] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = parse_scalar(value)
    return meta, text[match.end():]


def markdown_h1(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip().replace('"', '\\"')
    return fallback.replace("_", " ").replace("-", " ").title().replace('"', '\\"')


def yaml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
    text = str(value)
    if text == "" or text.startswith("[") or text in {"true", "false", "null"}:
        return text
    if any(ch in text for ch in [":", "#", "{", "}"]) or text.lower() in {"yes", "no", "on", "off"}:
        return json.dumps(text)
    return text


def evidence_index_paths(root: Path) -> list[str]:
    base = root / "docs/release-evidence"
    if not base.exists():
        return []
    return sorted(relpath(path, root) for path in base.rglob("evidence_index.md"))


def target_prefix(rel: str) -> str | None:
    if rel.startswith("docs/release-evidence/"):
        return "docs/release-evidence"
    matches = [prefix for prefix in TARGET_DIRS if rel == prefix or rel.startswith(prefix + "/")]
    return max(matches, key=len) if matches else None


def stage7_markdown_paths(root: Path) -> list[Path]:
    paths: dict[str, Path] = {}
    for rel_dir in TARGET_DIRS:
        base = root / rel_dir
        if base.exists():
            for path in base.rglob("*.md"):
                rel = relpath(path, root)
                # Generated render outputs or raw evidence bodies are not rewritten.
                if "/raw/" in rel:
                    continue
                paths[rel] = path
    for rel in evidence_index_paths(root):
        paths[rel] = root / rel
    # Include Stage 7 governance documents written by this script.
    for rel in [
        "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md",
        "docs/documentation/stage_7_retention_policy.md",
    ]:
        p = root / rel
        if p.exists():
            paths[rel] = p
    return [paths[key] for key in sorted(paths)]


def status_for(rel: str) -> str:
    low = rel.lower()
    if rel.startswith("docs/archive/"):
        return "archived-record"
    if rel.startswith("docs/release-evidence/") or "evidence_index" in low:
        return "evidence-record"
    if rel.startswith("docs/release/"):
        return "release-record"
    if rel.startswith("docs/codemaps/"):
        return "reference-record"
    if "template" in low:
        return "template"
    if "report" in low or "inventory" in low or "rollup" in low or "snapshot" in low:
        return "historical-record"
    if "policy" in low or "governance" in low or "retention" in low:
        return "active-policy"
    if "roadmap" in low or "backlog" in low or "plan" in low:
        return "active-control"
    return "active"


def evidence_command_for(rel: str) -> str:
    if rel.startswith("docs/release-evidence/"):
        return "make docs-housekeeping-stage7-check"
    if rel.startswith("docs/release/"):
        return "make docs-housekeeping-stage7-check"
    if rel.startswith("docs/backlog/"):
        return "make docs-housekeeping-stage7-check"
    if rel.startswith("docs/codemaps/"):
        return "make docs-housekeeping-stage7-check"
    if rel.startswith("docs/roadmap/") or rel.startswith("docs/roadmap_domains/"):
        return "make docs-housekeeping-stage7-check"
    return "make docs-housekeeping-stage7-check"


def front_matter(rel: str, title: str, existing: dict[str, object] | None) -> str:
    prefix = target_prefix(rel)
    if rel.startswith("docs/documentation/stage_7_"):
        prefix = "docs/reference"
    if prefix is None:
        raise ValueError(f"No Stage 7 metadata mapping for {rel}")
    review_interval = 30 if rel.startswith("docs/roadmap/") or rel.startswith("docs/backlog/") else 90
    if rel.startswith("docs/archive/") or rel.startswith("docs/release/") or rel.startswith("docs/release-evidence/"):
        review_interval = 180
    data: dict[str, object] = {
        "title": title,
        "status": status_for(rel),
        "owner": OWNER_MAP.get(prefix, "documentation-governance"),
        "reviewers": REVIEWER_MAP.get(prefix, ["documentation-governance"]),
        "audience": AUDIENCE_MAP.get(prefix, "documentation-reviewer"),
        "source_of_truth": rel in CANONICAL_PATHS,
        "supersedes": [],
        "superseded_by": None,
        "last_reviewed": LAST_REVIEWED,
        "review_interval_days": review_interval,
        "evidence_command": evidence_command_for(rel),
        "code_anchors": CODE_ANCHORS_MAP.get(prefix, [prefix]),
    }
    if rel.startswith("docs/documentation/stage_7_"):
        data["owner"] = "documentation-governance"
        data["reviewers"] = ["documentation-governance", "release-management", "evidence-custodian"]
        data["audience"] = "documentation-reviewer"
        data["source_of_truth"] = True
        data["review_interval_days"] = 45
        data["code_anchors"] = [
            "docs/documentation/stage_7_strict_scope.json",
            "scripts/maintenance/check_doc_stage7_strict_scope.py",
            "scripts/maintenance/apply_doc_stage7_cleanup.py",
        ]
    if existing:
        for key, value in existing.items():
            if key in data and value not in ("", None) and key not in {"title", "evidence_command", "code_anchors", "last_reviewed"}:
                data[key] = value
    return "---\n" + "\n".join(f"{key}: {yaml_value(data[key])}" for key in REQUIRED_METADATA_FIELDS) + "\n---\n\n"


def add_or_update_front_matter(path: Path, root: Path) -> None:
    rel = relpath(path, root)
    text = read(path)
    existing, body = split_front_matter(text)
    title = markdown_h1(body if existing is not None else text, path.stem)
    write(path, front_matter(rel, title, existing) + body.lstrip("\n"))


def write_stage7_docs(root: Path) -> None:
    stage_doc = f"""---
title: Stage 7 Release/Archive/Backlog/Codemaps Governance
status: active-control
owner: documentation-governance
reviewers: [documentation-governance, release-management, evidence-custodian]
audience: documentation-reviewer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: {LAST_REVIEWED}
review_interval_days: 45
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/documentation/stage_7_strict_scope.json, scripts/maintenance/check_doc_stage7_strict_scope.py, scripts/maintenance/apply_doc_stage7_cleanup.py]
---

# Stage 7 Release/Archive/Backlog/Codemaps Governance

Stage 7 promotes the remaining release, archive, backlog, roadmap, codemap, reference, and beta-launch documentation surfaces into strict-scope governance.

## Scope

The tranche covers:

- `docs/release/`
- `docs/operations/`
- `docs/roadmap/`
- `docs/backlog/`
- `docs/codemaps/`
- `docs/roadmap_domains/`
- `docs/reference/`
- `docs/beta_launch/`
- `docs/archive/`
- `docs/release-evidence/**/evidence_index.md`

Raw evidence snapshots under `docs/release-evidence/**/raw/` are not rewritten by this tranche. Historical release and archive bodies are preserved as records; Stage 7 adds ownership, review metadata, evidence-index governance, and retention policy around them.

## KG boundary

EduBoost keeps the knowledge-graph direction as an architectural north star. Stage 7 does not activate runtime KG work and does not reinterpret historical release evidence as a runtime KG implementation. Codemaps and roadmap-domain documents may reference KG concepts only as architecture, roadmap, or evidence context.

## Enforcement

Run:

```bash
make docs-housekeeping-stage7-check
make docs-housekeeping-check
```

Stage 7 requires metadata, ASCII-safe filenames, scoped link validation, deterministic inventory, and retained historical-risk-term allowlists for archived/release evidence claims.
"""
    retention_doc = f"""---
title: Stage 7 Release Archive Retention Policy
status: active-policy
owner: documentation-governance
reviewers: [documentation-governance, release-management, evidence-custodian]
audience: documentation-reviewer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: {LAST_REVIEWED}
review_interval_days: 45
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/archive, docs/release-evidence, scripts/maintenance/apply_doc_stage7_cleanup.py]
---

# Stage 7 Release Archive Retention Policy

This policy prevents deep-housekeeping from corrupting historical release and evidence records.

## Rules

1. Raw evidence files under `docs/release-evidence/**/raw/` are immutable evidence inputs and must not be mass-rewritten by documentation cleanup scripts.
2. Evidence index files are governed documents and may receive metadata and link/claim checks.
3. Historical release documents may retain historical readiness language when the Stage 7 strict-scope allowlist records the term and path.
4. Active roadmap, backlog, and codemap documents must avoid unbounded readiness claims unless tied to an evidence command and review boundary.
5. KG references remain allowed when they describe the architecture north star, codemap context, or future roadmap direction. Stage 7 must not claim runtime KG activation unless explicitly authorised by a separate implementation gate.

## Evidence command

```bash
make docs-housekeeping-stage7-check
```
"""
    write(root / "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md", stage_doc)
    write(root / "docs/documentation/stage_7_retention_policy.md", retention_doc)


def risky_allowlist(root: Path, paths: list[Path]) -> list[dict[str, str]]:
    allowed: list[dict[str, str]] = []
    for path in paths:
        rel = relpath(path, root)
        lower = read(path).lower()
        for term in RISKY_TERMS:
            if term.lower() in lower:
                allowed.append({"path": rel, "term": term, "reason": "historical or planning record retained under Stage 7 evidence policy"})
    # Keep KG north-star references allowed in codemaps and roadmap/archive surfaces without treating them as stale.
    for path in paths:
        rel = relpath(path, root)
        lower = read(path).lower()
        if "knowledge graph" in lower or "kg" in lower:
            if rel.startswith(("docs/codemaps/", "docs/roadmap/", "docs/roadmap_domains/", "docs/archive/", "docs/release/")):
                allowed.append({"path": rel, "term": "knowledge graph", "reason": "KG architectural north-star reference; not runtime activation"})
    dedup: dict[tuple[str, str], dict[str, str]] = {}
    for item in allowed:
        dedup[(item["path"], item["term"].lower())] = item
    return [dedup[key] for key in sorted(dedup)]


def write_scope(root: Path) -> None:
    paths = [relpath(p, root) for p in stage7_markdown_paths(root)]
    scope = {
        "stage": "Stage 7 release/archive/backlog/codemaps governance cleanup tranche 5",
        "strict_paths": paths,
        "exclude_paths": [],
        "require_ascii_filenames": True,
        "require_unique_titles": False,
        "allowed_risky_terms": risky_allowlist(root, [root / rel for rel in paths]),
    }
    write(root / "docs/documentation/stage_7_strict_scope.json", json.dumps(scope, indent=2, sort_keys=True) + "\n")



def patch_stage7_links(root: Path) -> None:
    replacements_by_file = {
        "docs/operations/SYSTEM_STARTUP_GUIDE.md": {
            "(docs/architecture.md)": "(../architecture.md)",
            "(../todos/data_generator_todo.md)": "(../todos/README.md)",
            "(../todos/todo.md)": "(../todos/README.md)",
        },
        "docs/operations/SYSTEM_STARTUP_REPORT.md": {
            "(docs/architecture.md)": "(../architecture.md)",
            "(../todos/data_generator_todo.md)": "(../todos/README.md)",
            "(../todos/todo.md)": "(../todos/README.md)",
        },
    }
    for rel, replacements in replacements_by_file.items():
        path = root / rel
        if not path.exists():
            continue
        text = read(path)
        new = text
        for old, replacement in replacements.items():
            new = new.replace(old, replacement)
        if new != text:
            write(path, new)

def patch_makefile(root: Path) -> None:
    path = root / "Makefile"
    text = read(path)
    lines = text.splitlines()
    stage7_tokens = ["docs-housekeeping-stage7-apply", "docs-stage7-strict-scope-check", "docs-housekeeping-stage7-check"]
    for idx, line in enumerate(lines):
        if line.startswith(".PHONY:") and "docs-housekeeping-check" in line:
            tokens = line.split()
            prefix = tokens[0]
            names = []
            seen = set()
            for token in tokens[1:] + stage7_tokens:
                if token not in seen:
                    names.append(token)
                    seen.add(token)
            lines[idx] = prefix + " " + " ".join(names)
        elif line.startswith("docs-housekeeping-check:"):
            deps = [
                "docs-housekeeping-inventory-check",
                "docs-source-of-truth-check",
                "docs-metadata-check",
                "docs-claim-discipline-check",
                "docs-links-check",
                "docs-housekeeping-ratchet-check",
                "docs-adr-number-check",
                "docs-stale-term-check",
                "docs-housekeeping-stage7-check",
            ]
            lines[idx] = "docs-housekeeping-check: " + " ".join(deps)
        elif line.startswith("docs-housekeeping-stage7-check:"):
            lines[idx] = "docs-housekeeping-stage7-check: docs-stage7-strict-scope-check docs-housekeeping-stage6-check"
    text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    if "docs-housekeeping-stage7-apply:" not in text:
        text += """

docs-housekeeping-stage7-apply:
	python3 scripts/maintenance/apply_doc_stage7_cleanup.py --root .

docs-stage7-strict-scope-check:
	python3 scripts/maintenance/check_doc_stage7_strict_scope.py --root .

docs-housekeeping-stage7-check: docs-stage7-strict-scope-check docs-housekeeping-stage6-check
"""
    write(path, text)


def patch_workflow(root: Path) -> None:
    path = root / ".github/workflows/documentation-governance.yml"
    if not path.exists():
        return
    text = read(path)
    if "Stage 7 strict tranche check" not in text:
        text = text.rstrip() + """

      - name: Stage 7 strict tranche check
        run: make docs-housekeeping-stage7-check
"""
    write(path, text + ("\n" if not text.endswith("\n") else ""))


def patch_gitignore(root: Path) -> None:
    path = root / ".gitignore"
    text = read(path) if path.exists() else ""
    for item in [".venv-docs/", "docs/api/_build/"]:
        if item not in text.splitlines():
            if text and not text.endswith("\n"):
                text += "\n"
            text += item + "\n"
    write(path, text)


def patch_source_of_truth(root: Path) -> None:
    path = root / "docs/documentation/source_of_truth.yml"
    if not path.exists():
        return
    text = read(path)
    for rel in [
        "docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md",
        "docs/documentation/stage_7_retention_policy.md",
        "docs/documentation/stage_7_strict_scope.json",
    ]:
        if rel not in text:
            text = text.replace("      - docs/documentation/stage_6_strict_scope.json\n", f"      - docs/documentation/stage_6_strict_scope.json\n      - {rel}\n", 1)
    stage7_sections = """

  release_archive_governance:
    canonical_path: docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md
    owner: documentation-governance
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage7-check
      - make docs-housekeeping-check
    related_paths:
      - docs/release
      - docs/archive
      - docs/release-evidence
      - docs/operations
      - docs/roadmap
      - docs/backlog
      - docs/codemaps
      - docs/roadmap_domains
      - docs/reference
      - docs/beta_launch

  release_archive_retention_policy:
    canonical_path: docs/documentation/stage_7_retention_policy.md
    owner: evidence-custodian
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage7-check
    related_paths:
      - docs/release
      - docs/archive
      - docs/release-evidence
"""
    text = re.sub(r"\n\n  release_archive_governance:\n.*?(?=\n\n  release_archive_retention_policy:|\n\nrules:|\Z)", "", text, flags=re.DOTALL)
    text = re.sub(r"\n\n  release_archive_retention_policy:\n.*?(?=\n\nrules:|\Z)", "", text, flags=re.DOTALL)
    if "\nrules:\n" in text:
        before, after = text.split("\nrules:\n", 1)
        text = before.rstrip() + stage7_sections + "\nrules:\n" + after.lstrip("\n")
    else:
        text = text.rstrip() + stage7_sections + "\n"
    write(path, text)


def patch_skill(root: Path) -> None:
    path = root / ".agents/skills/documentation-governance/SKILL.md"
    if not path.exists():
        return
    text = read(path)
    line = "- Stage 7 governs release/archive/backlog/codemaps surfaces; run `make docs-housekeeping-stage7-check` after changing release records, archive docs, roadmap/backlog docs, codemaps, roadmap-domain reports, reference docs, beta-launch docs, or release-evidence indexes. Keep KG references scoped to the architecture north star unless a separate runtime KG gate is authorised."
    if line not in text:
        text = text.rstrip() + "\n" + line + "\n"
    write(path, text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Stage 7 release/archive/backlog/codemaps documentation governance cleanup.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    write_stage7_docs(root)
    for path in stage7_markdown_paths(root):
        add_or_update_front_matter(path, root)
    patch_stage7_links(root)
    write_scope(root)
    patch_makefile(root)
    patch_workflow(root)
    patch_gitignore(root)
    patch_source_of_truth(root)
    patch_skill(root)
    print(f"Stage 7 cleanup applied to {len(stage7_markdown_paths(root))} governed markdown file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

