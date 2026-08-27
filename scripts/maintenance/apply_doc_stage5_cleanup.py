#!/usr/bin/env python3
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

FRONT_MATTER_RE = re.compile(r"\A---\s*(.*?)---\s*", re.DOTALL)


def parse_front_matter_value(value: str) -> object:
    text = value.strip()
    if not text:
        return ""

    candidate = text
    for _ in range(10):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            break
        if isinstance(parsed, str):
            if parsed == candidate:
                break
            candidate = parsed
            continue
        return parsed

    if candidate in {"true", "false"}:
        return candidate == "true"
    if candidate == "null":
        return None
    if re.fullmatch(r"-?\d+", candidate):
        return int(candidate)
    if candidate.startswith("[") and candidate.endswith("]"):
        inner = candidate[1:-1].strip()
        if not inner:
            return []
        items: list[object] = []
        for raw_item in inner.split(","):
            item = raw_item.strip()
            if not item:
                continue
            try:
                parsed_item = json.loads(item)
            except json.JSONDecodeError:
                if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                    parsed_item = item[1:-1]
                else:
                    parsed_item = item
            items.append(parsed_item)
        return items
    if (candidate.startswith('"') and candidate.endswith('"')) or (candidate.startswith("'") and candidate.endswith("'")):
        return candidate[1:-1]
    return candidate


def split_front_matter(text: str) -> tuple[dict[str, object] | None, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text
    meta: dict[str, object] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = parse_front_matter_value(value)
    return meta, text[match.end():]


def h1(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback.replace("_", " ").replace("-", " ").title()


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


def build_front_matter(rel: str, title: str, existing: dict[str, object] | None) -> str:
    prefix = target_prefix(rel)
    if prefix is None:
        raise ValueError(f"No Stage 5 metadata mapping for {rel}")
    data = {
        "title": title,
        "status": status_for(rel),
        "owner": OWNER_MAP[prefix],
        "reviewers": REVIEWER_MAP[prefix],
        "audience": AUDIENCE_MAP[prefix],
        "source_of_truth": rel in CANONICAL_PATHS,
        "supersedes": [],
        "superseded_by": None,
        "last_reviewed": LAST_REVIEWED,
        "review_interval_days": 60,
        "evidence_command": "make docs-housekeeping-stage5-check",
        "code_anchors": CODE_ANCHORS_MAP[prefix],
    }
    if existing:
        for key, value in existing.items():
            if key in data and value is not None and value != "" and key not in {"title", "evidence_command", "code_anchors", "last_reviewed"}:
                data[key] = value
    lines = ["---"]
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
