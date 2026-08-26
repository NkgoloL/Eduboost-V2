from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import hashlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts._subprocess import check_output, run
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

# Historical/generated/evidence areas are intentionally relaxed for default adoption gates.
# Stage 2 adds ratchet checks so these areas cannot get worse while the cleanup proceeds.
LEGACY_RELAXED_PREFIXES = (
    "docs/archive/",
    "docs/release-evidence/",
    "docs/generated/",
    "artifacts/",
    "audits/",
    "reports/",
)

LFS_POINTER_HEADER = "version https://git-lfs.github.com/spec/v1"
LFS_OID_RE = re.compile(r"^oid sha256:([a-fA-F0-9]{64})$", re.MULTILINE)
LFS_SIZE_RE = re.compile(r"^size (\d+)$", re.MULTILINE)


@dataclass(frozen=True)
class MarkdownDocument:
    path: Path
    rel: str
    text: str
    content_kind: str
    lfs_sha256: str = ""
    lfs_size: int = 0


def relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def is_excluded(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDED_DIR_PARTS for part in path.parts)


def iter_markdown(root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for base in [root / "docs", root / "audits", root / "reports", root / ".github"]:
        if base.exists():
            for path in sorted(base.rglob("*.md"), key=lambda p: relpath(p, root)):
                if not is_excluded(path) and path not in seen:
                    seen.add(path)
                    yield path
    for path in sorted(root.glob("*.md"), key=lambda p: p.name):
        if path.is_file() and path not in seen:
            seen.add(path)
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
    commands = [
        ["git", "diff", "--name-only", "--diff-filter=ACMRT", "origin/master...HEAD"],
        ["git", "diff", "--name-only", "--diff-filter=ACMRT"],
    ]
    output = ""
    for command in commands:
        try:
            output = check_output(command, cwd=root, text=True, stderr=subprocess.DEVNULL)
            break
        except Exception:
            output = ""
    paths = []
    for line in output.splitlines():
        if line.endswith(".md"):
            path = root / line
            if path.exists():
                paths.append(path)
    return sorted(paths, key=lambda p: relpath(p, root))


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


def parse_lfs_gitattributes(root: Path) -> set[str]:
    """Return exact LFS-tracked markdown paths declared in .gitattributes.

    This intentionally supports the repo's current exact-path usage. Glob patterns are
    preserved as best-effort suffix/prefix checks by is_lfs_tracked().
    """
    attrs = root / ".gitattributes"
    if not attrs.exists():
        return set()
    tracked: set[str] = set()
    for raw in attrs.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "filter=lfs" not in line:
            continue
        pattern = line.split()[0].strip()
        if pattern.startswith("/"):
            pattern = pattern[1:]
        tracked.add(pattern)
    return tracked


def _pattern_matches(rel: str, pattern: str) -> bool:
    if pattern == rel:
        return True
    # Lightweight support for common .gitattributes glob forms without adding dependencies.
    if "*" in pattern:
        regex = "^" + re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*") + "$"
        return bool(re.match(regex, rel))
    return False


def is_lfs_tracked(rel: str, root: Path, lfs_patterns: set[str] | None = None) -> bool:
    patterns = lfs_patterns if lfs_patterns is not None else parse_lfs_gitattributes(root)
    return any(_pattern_matches(rel, pattern) for pattern in patterns)


def parse_lfs_pointer(text: str) -> tuple[str, int] | None:
    if not text.startswith(LFS_POINTER_HEADER):
        return None
    oid_match = LFS_OID_RE.search(text)
    size_match = LFS_SIZE_RE.search(text)
    if not oid_match or not size_match:
        return None
    return oid_match.group(1).lower(), int(size_match.group(1))


def stable_lfs_identity(path: Path, root: Path) -> tuple[str, int]:
    raw_bytes = path.read_bytes()
    raw_text = raw_bytes.decode("utf-8", errors="replace")
    pointer = parse_lfs_pointer(raw_text)
    if pointer:
        return pointer
    return hashlib.sha256(raw_bytes).hexdigest(), len(raw_bytes)


def read_markdown_document(path: Path, root: Path, lfs_patterns: set[str] | None = None) -> MarkdownDocument:
    rel = relpath(path, root)
    if is_lfs_tracked(rel, root, lfs_patterns):
        sha256, size = stable_lfs_identity(path, root)
        return MarkdownDocument(
            path=path,
            rel=rel,
            text="",
            content_kind="git_lfs_tracked_skipped_content",
            lfs_sha256=sha256,
            lfs_size=size,
        )
    return MarkdownDocument(
        path=path,
        rel=rel,
        text=path.read_text(encoding="utf-8", errors="replace"),
        content_kind="markdown",
    )


def write_json_deterministic(path: Path, payload: object) -> None:
    ensure_parent(path)
    import json

    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
