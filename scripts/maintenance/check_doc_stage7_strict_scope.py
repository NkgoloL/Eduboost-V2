#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from doc_utils import REQUIRED_METADATA_FIELDS, markdown_h1, parse_front_matter, relpath

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
RISKY_TERMS = [
    "production-ready", "production ready", "release-ready", "release ready", "launch approved",
    "fully complete", "all tests pass", "green baseline", "DBE AI Expert", "Cosmos DB", "Azure ML", "Neo4j",
]
HISTORICAL_LINK_PREFIXES = ("docs/archive/", "docs/release/", "docs/release-evidence/")


def is_external(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https", "mailto", "tel"}


def load_scope(root: Path, scope_path: str) -> dict[str, object]:
    path = root / scope_path
    if not path.exists():
        raise FileNotFoundError(f"Missing Stage 7 strict-scope config: {scope_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def is_excluded(rel: str, excludes: list[str]) -> bool:
    return any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in excludes)


def expand_paths(root: Path, config: dict[str, object]) -> list[Path]:
    strict_paths = [str(item) for item in config.get("strict_paths", [])]
    excludes = [str(item) for item in config.get("exclude_paths", [])]
    files: list[Path] = []
    for item in strict_paths:
        path = root / item
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md"), key=lambda p: p.as_posix()))
        elif path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
        else:
            raise FileNotFoundError(f"Stage 7 strict path does not exist or is not markdown: {item}")
    unique: dict[str, Path] = {}
    for path in files:
        rel = relpath(path, root)
        if not is_excluded(rel, excludes):
            unique[rel] = path
    return [unique[key] for key in sorted(unique)]


def allowed_term(config: dict[str, object], rel: str, term: str) -> bool:
    for item in config.get("allowed_risky_terms", []):
        if not isinstance(item, dict):
            continue
        if item.get("path") == rel and str(item.get("term", "")).lower() == term.lower():
            return True
    return False


def local_link_failures(path: Path, root: Path, text: str) -> list[str]:
    rel = relpath(path, root)
    if rel.startswith(HISTORICAL_LINK_PREFIXES):
        return []
    failures: list[str] = []
    for match in LINK_RE.finditer(text):
        raw = match.group(1).strip()
        if not raw or raw.startswith("#") or is_external(raw):
            continue
        if raw.startswith("file://"):
            failures.append(f"local file URI is not allowed: {raw}")
            continue
        target_part = raw.split("#", 1)[0].strip()
        if not target_part:
            continue
        if target_part.startswith("<") and target_part.endswith(">"):
            target_part = target_part[1:-1]
        target_part = unquote(target_part)
        if len(target_part) > 2048:
            continue
        target = (root / target_part[1:]) if target_part.startswith("/") else (path.parent / target_part)
        try:
            exists = target.exists()
        except OSError:
            exists = False
        if not exists:
            failures.append(f"broken link -> {raw}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Stage 7 release/archive/backlog/codemaps strict documentation tranche scope.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--scope", default="docs/documentation/stage_7_strict_scope.json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    config = load_scope(root, args.scope)
    stage_label = str(config.get("stage") or "Stage 7 strict-scope")
    files = expand_paths(root, config)
    failures: list[str] = []
    titles: dict[str, list[str]] = {}

    if config.get("require_ascii_filenames", True):
        for path in files:
            rel = relpath(path, root)
            if any(ord(char) > 127 for char in rel) or "#U" in rel:
                failures.append(f"{rel}: non-ASCII or escaped-Unicode filename is not allowed in strict scope")

    for path in files:
        rel = relpath(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_front_matter(text)
        if not meta:
            failures.append(f"{rel}: missing YAML front matter")
        else:
            missing = [field for field in REQUIRED_METADATA_FIELDS if field not in meta]
            if missing:
                failures.append(f"{rel}: missing metadata fields: {', '.join(missing)}")
            if str(meta.get("status", "")).lower() in {"", "unknown"}:
                failures.append(f"{rel}: status must be explicit")
            if str(meta.get("source_of_truth", "")).lower() not in {"true", "false", "yes", "no"}:
                failures.append(f"{rel}: source_of_truth must be boolean-like")
        title = str((meta or {}).get("title") or markdown_h1(text) or "").strip().lower()
        if title:
            titles.setdefault(title, []).append(rel)
        for issue in local_link_failures(path, root, text):
            failures.append(f"{rel}: {issue}")
        lower = text.lower()
        for term in RISKY_TERMS:
            if term.lower() in lower and not allowed_term(config, rel, term):
                failures.append(f"{rel}: unallowed risky/stale term in strict scope: {term}")

    if config.get("require_unique_titles", False):
        for title, paths in sorted(titles.items()):
            if len(paths) > 1:
                failures.append(f"duplicate title in strict scope '{title}': {', '.join(paths)}")

    if failures:
        print(f"{stage_label} check failed:")
        for failure in failures[:200]:
            print(f"  - {failure}")
        if len(failures) > 200:
            print(f"  ... {len(failures) - 200} more")
        return 1

    print(f"{stage_label} check passed for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

