from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path.cwd().resolve()
LAST_REVIEWED = "2026-06-24"

REQUIRED_METADATA_FIELDS = [
    "title", "status", "owner", "reviewers", "audience", "source_of_truth",
    "supersedes", "superseded_by", "last_reviewed", "review_interval_days",
    "evidence_command", "code_anchors",
]

TARGET_DIRS = [
    "docs/frontend", "docs/backend", "docs/database", "docs/deployment", "docs/testing",
    "docs/observability", "docs/disaster_recovery", "docs/operations_support", "docs/runbooks",
    "docs/content_factory", "docs/caps", "docs/curriculum", "docs/diagnostics", "docs/irt",
    "docs/learning_science", "docs/ai",
]

OWNER_MAP = {
    "docs/frontend": "frontend", "docs/backend": "backend", "docs/database": "database",
    "docs/deployment": "release-management", "docs/testing": "quality",
    "docs/observability": "operations", "docs/disaster_recovery": "operations",
    "docs/operations_support": "operations", "docs/runbooks": "operations",
    "docs/content_factory": "content-factory", "docs/caps": "curriculum", "docs/curriculum": "curriculum",
    "docs/diagnostics": "diagnostics", "docs/irt": "diagnostics", "docs/learning_science": "learning-science",
    "docs/ai": "ai-safety",
}
REVIEWER_MAP = {
    "docs/frontend": "[frontend, product, privacy]", "docs/backend": "[backend, architecture, security]",
    "docs/database": "[backend, database, release-management]", "docs/deployment": "[release-management, operations, security]",
    "docs/testing": "[quality, engineering, release-management]", "docs/observability": "[operations, security, backend]",
    "docs/disaster_recovery": "[operations, security, privacy]", "docs/operations_support": "[operations, support, privacy]",
    "docs/runbooks": "[operations, engineering, release-management]", "docs/content_factory": "[content-factory, curriculum, engineering]",
    "docs/caps": "[curriculum, content-factory, product]", "docs/curriculum": "[curriculum, content-factory, learning-science]",
    "docs/diagnostics": "[diagnostics, learning-science, backend]", "docs/irt": "[diagnostics, learning-science, backend]",
    "docs/learning_science": "[learning-science, diagnostics, curriculum]", "docs/ai": "[ai-safety, curriculum, privacy]",
}
AUDIENCE_MAP = {
    "docs/frontend": "developer", "docs/backend": "developer", "docs/database": "developer",
    "docs/deployment": "operator", "docs/testing": "quality-reviewer", "docs/observability": "operator",
    "docs/disaster_recovery": "operator", "docs/operations_support": "operator", "docs/runbooks": "operator",
    "docs/content_factory": "developer", "docs/caps": "curriculum-reviewer", "docs/curriculum": "curriculum-reviewer",
    "docs/diagnostics": "developer", "docs/irt": "developer", "docs/learning_science": "learning-science-reviewer",
    "docs/ai": "safety-reviewer",
}
CODE_ANCHORS_MAP = {
    "docs/frontend": "[app/frontend, docs/frontend/README.md]",
    "docs/backend": "[app/api_v2.py, app/api_v2_routers, docs/backend/README.md]",
    "docs/database": "[alembic, app/repositories, scripts/validate_schema_integrity.py]",
    "docs/deployment": "[Dockerfile, docker-compose.yml, docker-compose.prod.yml, .github/workflows]",
    "docs/testing": "[tests, pytest.ini, Makefile]",
    "docs/observability": "[app/api_v2.py, docs/observability]",
    "docs/disaster_recovery": "[docs/disaster_recovery, scripts]",
    "docs/operations_support": "[docs/operations_support, docs/runbooks]",
    "docs/runbooks": "[docs/runbooks, docs/operations]",
    "docs/content_factory": "[app/services/content_factory, data/content_factory, docs/content_factory]",
    "docs/caps": "[docs/caps, app/services/content_factory]",
    "docs/curriculum": "[docs/curriculum, app/services/content_factory]",
    "docs/diagnostics": "[app/modules/diagnostics, docs/diagnostics]",
    "docs/irt": "[app/services, docs/irt]",
    "docs/learning_science": "[docs/learning_science, docs/diagnostics]",
    "docs/ai": "[app/services, docs/ai]",
}
CANONICAL_PATHS = {
    "docs/frontend/README.md", "docs/backend/README.md", "docs/database/schema_integrity.md",
    "docs/deployment/README.md", "docs/testing/README.md",
    "docs/observability/production_observability_architecture_contract.md",
    "docs/disaster_recovery/backup_restore_architecture_contract.md",
    "docs/operations_support/incident_response_operations_support_architecture_contract.md",
    "docs/content_factory/control_plane.md", "docs/caps/grade4_maths_coverage_matrix.md",
    "docs/curriculum/caps_topic_map_production_contract.md", "docs/diagnostics/README.md",
    "docs/irt/README.md", "docs/learning_science/mastery_model.md", "docs/ai/ai_safety_boundary_contract.md",
}
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def h1(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip().replace('"', '\\"')
    return fallback.replace("_", " ").replace("-", " ").title().replace('"', '\\"')

def split_front_matter(text: str) -> tuple[dict[str, str] | None, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, text[match.end():]

def target_prefix(rel: str) -> str | None:
    matches = [prefix for prefix in TARGET_DIRS if rel == prefix or rel.startswith(prefix + "/")]
    return max(matches, key=len) if matches else None

def status_for(rel: str) -> str:
    low = rel.lower()
    evidence_tokens = ["handover", "evidence", "audit", "inventory", "matrix", "report", "closure", "checklist", "baseline", "validation", "status", "drill", "incident", "pir"]
    if any(token in low for token in evidence_tokens):
        return "current-evidence"
    if "runbook" in low or "/runbooks/" in low:
        return "active-runbook"
    return "active"

def front_matter(rel: str, title: str, existing: dict[str, str] | None) -> str:
    prefix = target_prefix(rel)
    if prefix is None:
        raise ValueError(f"No Stage 5 metadata mapping for {rel}")
    data = {
        "title": f'"{title}"',
        "status": status_for(rel),
        "owner": OWNER_MAP[prefix],
        "reviewers": REVIEWER_MAP[prefix],
        "audience": AUDIENCE_MAP[prefix],
        "source_of_truth": "true" if rel in CANONICAL_PATHS else "false",
        "supersedes": "[]",
        "superseded_by": "null",
        "last_reviewed": LAST_REVIEWED,
        "review_interval_days": "60",
        "evidence_command": '"make docs-housekeeping-stage5-check"',
        "code_anchors": CODE_ANCHORS_MAP[prefix],
    }
    if existing:
        for key, value in existing.items():
            if key in data and value not in {"", "null"} and key not in {"title", "evidence_command", "code_anchors", "last_reviewed"}:
                data[key] = value
    return "---\n" + "\n".join(f"{key}: {data[key]}" for key in REQUIRED_METADATA_FIELDS) + "\n---\n\n"

def add_or_update_front_matter(path: Path) -> None:
    rel = path.relative_to(ROOT).as_posix()
    text = read(path)
    existing, body = split_front_matter(text)
    title = h1(body if existing is not None else text, path.stem)
    write(path, front_matter(rel, title, existing) + body.lstrip("\n"))

def replace_in_file(rel: str, replacements: list[tuple[str, str]]) -> None:
    path = ROOT / rel
    if not path.exists():
        return
    text = read(path)
    for old, new in replacements:
        text = text.replace(old, new)
    write(path, text)

def update_source_of_truth_register() -> None:
    path = ROOT / "docs/documentation/source_of_truth.yml"
    text = read(path)
    text = text.replace(
        "      - docs/documentation/stage_4_deep_housekeeping.md\n      - docs/documentation/stage_4_strict_scope.json\n",
        "      - docs/documentation/stage_4_deep_housekeeping.md\n      - docs/documentation/stage_4_strict_scope.json\n      - docs/documentation/stage_5_technical_delivery_housekeeping.md\n      - docs/documentation/stage_5_strict_scope.json\n",
    )
    stage5_sections = """

  frontend_runtime:
    canonical_path: docs/frontend/README.md
    owner: frontend
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage5-check
      - cd app/frontend && pnpm run type-check
    related_paths:
      - docs/frontend
      - app/frontend

  backend_runtime:
    canonical_path: docs/backend/README.md
    owner: backend
    review_interval_days: 45
    evidence_commands:
      - make runtime-check
      - make test-fast
    related_paths:
      - app/api_v2.py
      - app/api_v2_routers
      - docs/database

  database_schema:
    canonical_path: docs/database/schema_integrity.md
    owner: database
    review_interval_days: 45
    evidence_commands:
      - python3 scripts/validate_schema_integrity.py
      - python3 scripts/verify_migration_graph.py
    related_paths:
      - alembic
      - app/repositories

  deployment_delivery:
    canonical_path: docs/deployment/README.md
    owner: release-management
    review_interval_days: 45
    evidence_commands:
      - docker compose config
      - docker compose -f docker-compose.prod.yml config
    related_paths:
      - docs/deployment
      - .github/workflows

  testing_quality:
    canonical_path: docs/testing/README.md
    owner: quality
    review_interval_days: 45
    evidence_commands:
      - make test-fast
      - make docs-housekeeping-stage5-check
    related_paths:
      - tests
      - docs/testing

  observability_operations:
    canonical_path: docs/observability/production_observability_architecture_contract.md
    owner: operations
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage5-check
    related_paths:
      - docs/observability
      - docs/operations_support

  disaster_recovery:
    canonical_path: docs/disaster_recovery/backup_restore_architecture_contract.md
    owner: operations
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage5-check
    related_paths:
      - docs/disaster_recovery
      - docs/disaster_recovery/runbooks

  content_factory:
    canonical_path: docs/content_factory/control_plane.md
    owner: content-factory
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage5-check
    related_paths:
      - docs/content_factory
      - data/content_factory

  caps_curriculum:
    canonical_path: docs/curriculum/caps_topic_map_production_contract.md
    owner: curriculum
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage5-check
    related_paths:
      - docs/caps
      - docs/curriculum

  diagnostics_learning_science:
    canonical_path: docs/diagnostics/README.md
    owner: diagnostics
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage5-check
    related_paths:
      - docs/diagnostics
      - docs/irt
      - docs/learning_science

  ai_safety:
    canonical_path: docs/ai/ai_safety_boundary_contract.md
    owner: ai-safety
    review_interval_days: 45
    evidence_commands:
      - make docs-housekeeping-stage5-check
    related_paths:
      - docs/ai
      - app/services
"""
    if "  frontend_runtime:" not in text:
        text = text.replace("\nrules:\n", stage5_sections + "\nrules:\n")
    text = text.replace("last_reviewed: 2026-06-23", "last_reviewed: 2026-06-24")
    write(path, text)

def update_makefile() -> None:
    path = ROOT / "Makefile"
    text = read(path)
    first_line_end = text.find("\n")
    if "docs-housekeeping-stage5-check" not in text:
        text = text.replace("docs-housekeeping-stage4-check", "docs-housekeeping-stage4-check docs-housekeeping-stage5-apply docs-stage5-strict-scope-check docs-housekeeping-stage5-check", 1)
    text = text.replace(
        "docs-housekeeping-stage3-check docs-housekeeping-stage4-check",
        "docs-housekeeping-stage3-check docs-housekeeping-stage4-check docs-housekeeping-stage5-check",
    )
    if "# Stage 5 documentation technical-delivery and learning-engine strict tranche." not in text:
        text += """

# Stage 5 documentation technical-delivery and learning-engine strict tranche.
docs-housekeeping-stage5-apply:
	python3 scripts/maintenance/apply_doc_stage5_cleanup.py --root .

docs-stage5-strict-scope-check:
	python3 scripts/maintenance/check_doc_stage5_strict_scope.py --root .

docs-housekeeping-stage5-check: docs-stage5-strict-scope-check docs-housekeeping-stage4-check
"""
    write(path, text)

def update_workflow() -> None:
    path = ROOT / ".github/workflows/documentation-governance.yml"
    if not path.exists():
        return
    text = read(path)
    if "Stage 5 strict tranche check" not in text:
        text = text.replace(
            "      - name: Stage 4 strict tranche check\n        run: make docs-housekeeping-stage4-check\n",
            "      - name: Stage 4 strict tranche check\n        run: make docs-housekeeping-stage4-check\n      - name: Stage 5 strict tranche check\n        run: make docs-housekeeping-stage5-check\n",
        )
    write(path, text)

def update_skill() -> None:
    path = ROOT / ".agents/skills/documentation-governance/SKILL.md"
    if not path.exists():
        return
    text = read(path)
    if "## Stage 5 strict tranche" not in text:
        text += """

## Stage 5 strict tranche

When editing technical delivery or learning-engine documentation under `docs/frontend/`, `docs/backend/`, `docs/database/`, `docs/deployment/`, `docs/testing/`, `docs/observability/`, `docs/disaster_recovery/`, `docs/operations_support/`, `docs/runbooks/`, `docs/content_factory/`, `docs/caps/`, `docs/curriculum/`, `docs/diagnostics/`, `docs/irt/`, `docs/learning_science/`, or `docs/ai/`, run `make docs-housekeeping-stage5-check` in addition to the default housekeeping gate.
"""
    write(path, text)

def write_stage5_docs() -> None:
    write(ROOT / "docs/documentation/stage_5_technical_delivery_housekeeping.md", """---
title: "Stage 5 Technical Delivery and Learning-Engine Documentation Housekeeping"
status: active
owner: documentation-governance
reviewers: [engineering, operations, curriculum, ai-safety, quality]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 30
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [docs/documentation/stage_5_strict_scope.json, scripts/maintenance/check_doc_stage5_strict_scope.py]
---

# Stage 5 Technical Delivery and Learning-Engine Documentation Housekeeping

Stage 5 expands strict documentation housekeeping beyond the Stage 4 canonical architecture/product/API/compliance/security tranche.

## Scope

Strict enforcement now covers technical delivery and learning-engine documentation:

- `docs/frontend/`
- `docs/backend/`
- `docs/database/`
- `docs/deployment/`
- `docs/testing/`
- `docs/observability/`
- `docs/disaster_recovery/`
- `docs/operations_support/`
- `docs/runbooks/`
- `docs/content_factory/`
- `docs/caps/`
- `docs/curriculum/`
- `docs/diagnostics/`
- `docs/irt/`
- `docs/learning_science/`
- `docs/ai/`

## Gate

Run:

```bash
make docs-housekeeping-stage5-check
make docs-housekeeping-check
```

The global strict gate remains a future target. Stage 5 keeps the ratchet model: current scoped areas must stay clean, while release/evidence/archive debt is reduced in later tranches.
""")
    scope = {"stage": "Stage 5 strict documentation cleanup tranche 3", "strict_paths": TARGET_DIRS, "exclude_paths": [], "require_ascii_filenames": True, "require_unique_titles": True, "allowed_risky_terms": []}
    write(ROOT / "docs/documentation/stage_5_strict_scope.json", json.dumps(scope, indent=2, sort_keys=True) + "\n")

def write_stage5_scripts() -> None:
    write(ROOT / "scripts/maintenance/apply_doc_stage5_cleanup.py", """#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAST_REVIEWED = "2026-06-24"

REQUIRED_METADATA_FIELDS = [
    "title",
    "status",
    "owner",
    "reviewers",
    "audience",
    "source_of_truth",
    "supersedes",
    "superseded_by",
    "last_reviewed",
    "review_interval_days",
    "evidence_command",
    "code_anchors",
]

TARGET_DIRS = [
    "docs/frontend",
    "docs/backend",
    "docs/database",
    "docs/deployment",
    "docs/testing",
    "docs/observability",
    "docs/disaster_recovery",
    "docs/operations_support",
    "docs/runbooks",
    "docs/content_factory",
    "docs/caps",
    "docs/curriculum",
    "docs/diagnostics",
    "docs/irt",
    "docs/learning_science",
    "docs/ai",
]

OWNER_MAP = {
    "docs/frontend": "frontend",
    "docs/backend": "backend",
    "docs/database": "database",
    "docs/deployment": "release-management",
    "docs/testing": "quality",
    "docs/observability": "operations",
    "docs/disaster_recovery": "operations",
    "docs/operations_support": "operations",
    "docs/runbooks": "operations",
    "docs/content_factory": "content-factory",
    "docs/caps": "curriculum",
    "docs/curriculum": "curriculum",
    "docs/diagnostics": "diagnostics",
    "docs/irt": "diagnostics",
    "docs/learning_science": "learning-science",
    "docs/ai": "ai-safety",
}

REVIEWER_MAP = {
    "docs/frontend": "[frontend, product, privacy]",
    "docs/backend": "[backend, architecture, security]",
    "docs/database": "[backend, database, release-management]",
    "docs/deployment": "[release-management, operations, security]",
    "docs/testing": "[quality, engineering, release-management]",
    "docs/observability": "[operations, security, backend]",
    "docs/disaster_recovery": "[operations, security, privacy]",
    "docs/operations_support": "[operations, support, privacy]",
    "docs/runbooks": "[operations, engineering, release-management]",
    "docs/content_factory": "[content-factory, curriculum, engineering]",
    "docs/caps": "[curriculum, content-factory, product]",
    "docs/curriculum": "[curriculum, content-factory, learning-science]",
    "docs/diagnostics": "[diagnostics, learning-science, backend]",
    "docs/irt": "[diagnostics, learning-science, backend]",
    "docs/learning_science": "[learning-science, diagnostics, curriculum]",
    "docs/ai": "[ai-safety, curriculum, privacy]",
}

AUDIENCE_MAP = {
    "docs/frontend": "developer",
    "docs/backend": "developer",
    "docs/database": "developer",
    "docs/deployment": "operator",
    "docs/testing": "quality-reviewer",
    "docs/observability": "operator",
    "docs/disaster_recovery": "operator",
    "docs/operations_support": "operator",
    "docs/runbooks": "operator",
    "docs/content_factory": "developer",
    "docs/caps": "curriculum-reviewer",
    "docs/curriculum": "curriculum-reviewer",
    "docs/diagnostics": "developer",
    "docs/irt": "developer",
    "docs/learning_science": "learning-science-reviewer",
    "docs/ai": "safety-reviewer",
}

CODE_ANCHORS_MAP = {
    "docs/frontend": "[app/frontend, docs/frontend/README.md]",
    "docs/backend": "[app/api_v2.py, app/api_v2_routers, docs/backend/README.md]",
    "docs/database": "[alembic, app/repositories, scripts/validate_schema_integrity.py]",
    "docs/deployment": "[Dockerfile, docker-compose.yml, docker-compose.prod.yml, .github/workflows]",
    "docs/testing": "[tests, pytest.ini, Makefile]",
    "docs/observability": "[app/api_v2.py, docs/observability]",
    "docs/disaster_recovery": "[docs/disaster_recovery, scripts]",
    "docs/operations_support": "[docs/operations_support, docs/runbooks]",
    "docs/runbooks": "[docs/runbooks, docs/operations]",
    "docs/content_factory": "[app/services/content_factory, data/content_factory, docs/content_factory]",
    "docs/caps": "[docs/caps, app/services/content_factory]",
    "docs/curriculum": "[docs/curriculum, app/services/content_factory]",
    "docs/diagnostics": "[app/modules/diagnostics, docs/diagnostics]",
    "docs/irt": "[app/services, docs/irt]",
    "docs/learning_science": "[docs/learning_science, docs/diagnostics]",
    "docs/ai": "[app/services, docs/ai]",
}

CANONICAL_PATHS = {
    "docs/frontend/README.md",
    "docs/backend/README.md",
    "docs/database/schema_integrity.md",
    "docs/deployment/README.md",
    "docs/testing/README.md",
    "docs/observability/production_observability_architecture_contract.md",
    "docs/disaster_recovery/backup_restore_architecture_contract.md",
    "docs/operations_support/incident_response_operations_support_architecture_contract.md",
    "docs/content_factory/control_plane.md",
    "docs/caps/grade4_maths_coverage_matrix.md",
    "docs/curriculum/caps_topic_map_production_contract.md",
    "docs/diagnostics/README.md",
    "docs/irt/README.md",
    "docs/learning_science/mastery_model.md",
    "docs/ai/ai_safety_boundary_contract.md",
}

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def split_front_matter(text: str) -> tuple[dict[str, str] | None, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, text[match.end():]


def h1(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip().replace('"', '\\"')
    return fallback.replace("_", " ").replace("-", " ").title().replace('"', '\\"')


def target_prefix(rel: str) -> str | None:
    matches = [prefix for prefix in TARGET_DIRS if rel == prefix or rel.startswith(prefix + "/")]
    return max(matches, key=len) if matches else None


def status_for(rel: str) -> str:
    lower = rel.lower()
    evidence_tokens = [
        "handover",
        "evidence",
        "audit",
        "inventory",
        "matrix",
        "report",
        "closure",
        "checklist",
        "baseline",
        "validation",
        "status",
        "drill",
        "incident",
        "pir",
    ]
    if any(token in lower for token in evidence_tokens):
        return "current-evidence"
    if "runbook" in lower or "/runbooks/" in lower:
        return "active-runbook"
    return "active"


def format_value(value: object) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(json.dumps(item) for item in value) + "]"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    return str(value)


def build_front_matter(rel: str, title: str, existing: dict[str, str] | None) -> str:
    prefix = target_prefix(rel)
    if prefix is None:
        raise ValueError(f"No Stage 5 metadata mapping for {rel}")
    data = {
        "title": title,
        "status": status_for(rel),
        "owner": OWNER_MAP[prefix],
        "reviewers": REVIEWER_MAP[prefix],
        "audience": AUDIENCE_MAP[prefix],
        "source_of_truth": "true" if rel in CANONICAL_PATHS else "false",
        "supersedes": [],
        "superseded_by": None,
        "last_reviewed": LAST_REVIEWED,
        "review_interval_days": 60,
        "evidence_command": "make docs-housekeeping-stage5-check",
        "code_anchors": CODE_ANCHORS_MAP[prefix],
    }
    if existing:
        for key, value in existing.items():
            if key in data and value not in {"", "null"} and key not in {"title", "evidence_command", "code_anchors", "last_reviewed"}:
                data[key] = value
    lines = [f"---"]
    for key in REQUIRED_METADATA_FIELDS:
        lines.append(f"{key}: {format_value(data[key])}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def add_or_update_front_matter(path: Path) -> None:
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    existing, body = split_front_matter(text)
    title = h1(body if existing is not None else text, path.stem)
    new_text = build_front_matter(rel, title, existing) + body.lstrip("\n")
    path.write_text(new_text, encoding="utf-8")


def replace_text(rel: str, replacements: list[tuple[str, str]]) -> None:
    path = ROOT / rel
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = sys.argv[1:]
    if "--root" in args:
        idx = args.index("--root")
        if idx + 1 < len(args):
            global ROOT
            ROOT = Path(args[idx + 1]).resolve()
    for dirname in TARGET_DIRS:
        path = ROOT / dirname
        if path.exists():
            for markdown in sorted(path.rglob("*.md"), key=lambda p: p.as_posix()):
                add_or_update_front_matter(markdown)
    replace_text(
        "docs/frontend/post-rc5-dependency-maintenance.md",
        [("(../../OUTSTANDING_TODO_ITEMS.md)", "(../archive/roadmaps-or-todos/OUTSTANDING_TODO_ITEMS.md.bak)")],
    )
    replace_text(
        "docs/frontend/FE-PWA-MANIFEST-ICON-001-validation.md",
        [("production-ready", "ready for controlled release evidence"), ("Production-ready", "Ready for controlled release evidence")],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""")
    write(ROOT / "scripts/maintenance/check_doc_stage5_strict_scope.py", """#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    args = sys.argv[1:]
    if "--root" in args:
        idx = args.index("--root")
        if idx + 1 < len(args):
            root = Path(args[idx + 1]).resolve()
    command = [sys.executable, str(root / "scripts/maintenance/check_doc_stage3_strict_scope.py"), "--root", str(root), "--scope", "docs/documentation/stage_5_strict_scope.json"]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
""")

def main() -> int:
    for dirname in TARGET_DIRS:
        root = ROOT / dirname
        if root.exists():
            for path in sorted(root.rglob("*.md"), key=lambda p: p.as_posix()):
                add_or_update_front_matter(path)
    replace_in_file("docs/frontend/post-rc5-dependency-maintenance.md", [("(../../OUTSTANDING_TODO_ITEMS.md)", "(../archive/roadmaps-or-todos/OUTSTANDING_TODO_ITEMS.md.bak)")])
    replace_in_file("docs/frontend/FE-PWA-MANIFEST-ICON-001-validation.md", [("production-ready", "ready for controlled release evidence"), ("Production-ready", "Ready for controlled release evidence")])
    replace_in_file("docs/content_factory/CONTENT_GENERATION_CONFIG.md", [("[scripts/curriculum/content_generation_config.py](scripts/curriculum/content_generation_config.py)", "`scripts/curriculum/content_generation_config.py`")])
    write_stage5_docs(); write_stage5_scripts(); update_makefile(); update_workflow(); update_skill(); update_source_of_truth_register()
    print("Stage 5 cleanup applied.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
