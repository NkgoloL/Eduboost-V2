from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Iterable

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

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

DEFAULT_EXCLUDED_DIR_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage_html",
    "htmlcov",
}

LEGACY_RELAXED_PREFIXES = (
    "docs/archive/",
    "docs/release-evidence/",
    "docs/generated/",
    "artifacts/",
    "audits/",
    "reports/",
)


def relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def is_excluded(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDED_DIR_PARTS for part in path.parts)


def iter_markdown(root: Path) -> Iterable[Path]:
    for base in [root / "docs", root / "audits", root / "reports", root / ".github"]:
        if base.exists():
            for path in base.rglob("*.md"):
                if not is_excluded(path):
                    yield path
    for path in root.glob("*.md"):
        if path.is_file():
            yield path


def parse_front_matter(text: str) -> dict[str, object]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}
    raw = match.group(1)
    parsed: dict[str, object] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {"true", "false"}:
            parsed[key] = value == "true"
        elif value == "null":
            parsed[key] = None
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            parsed[key] = [v.strip().strip('"\'') for v in inner.split(",") if v.strip()]
        else:
            parsed[key] = value.strip('"\'')
    return parsed


def has_front_matter(text: str) -> bool:
    return bool(FRONT_MATTER_RE.match(text))


def markdown_h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def git_changed_markdown(root: Path) -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only", "--diff-filter=ACMRT", "origin/master...HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        try:
            output = subprocess.check_output(
                ["git", "diff", "--name-only", "--diff-filter=ACMRT"],
                cwd=root,
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            return []
    paths = []
    for line in output.splitlines():
        if line.endswith(".md"):
            path = root / line
            if path.exists():
                paths.append(path)
    return paths


def load_source_of_truth_paths(root: Path) -> list[Path]:
    register = root / "docs/documentation/source_of_truth.yml"
    if not register.exists():
        return []
    paths: list[Path] = []
    for line in register.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("canonical_path:"):
            _, value = stripped.split(":", 1)
            value = value.strip().strip('"\'')
            if value:
                paths.append(root / value)
    return paths


def should_relax_metadata(rel: str) -> bool:
    return rel.startswith(LEGACY_RELAXED_PREFIXES)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
