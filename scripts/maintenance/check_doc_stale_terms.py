#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from doc_utils import iter_markdown, read_markdown_document, relpath, parse_lfs_gitattributes, should_relax_metadata, write_json_deterministic

STALE_TERMS = [
    "DBE AI Expert",
    "Cosmos DB",
    "Azure ML",
    "Neo4j",
    "knowledge graph",
]


def collect(root: Path, include_relaxed: bool) -> dict[str, list[str]]:
    lfs_patterns = parse_lfs_gitattributes(root)
    hits: dict[str, list[str]] = defaultdict(list)
    for path in sorted(iter_markdown(root), key=lambda p: relpath(p, root)):
        rel = relpath(path, root)
        if not include_relaxed and should_relax_metadata(rel):
            continue
        doc = read_markdown_document(path, root, lfs_patterns)
        if doc.content_kind != "markdown":
            continue
        lower = doc.text.lower()
        for term in STALE_TERMS:
            if term.lower() in lower:
                hits[term].append(rel)
    return {term: sorted(paths) for term, paths in sorted(hits.items())}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check stale off-project documentation terms with ratchet baseline.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--baseline", default="docs/documentation/stale_term_baseline.json")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Require zero stale-term hits outside relaxed areas.")
    parser.add_argument("--include-relaxed", action="store_true", help="Include archive/generated/evidence/report areas.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    hits = collect(root, include_relaxed=args.include_relaxed)
    baseline_path = root / args.baseline

    if args.update:
        write_json_deterministic(baseline_path, {
            "schema_version": "doc-stale-term-baseline/v1",
            "note": "Stage 2 ratchet baseline. Remove stale terms over time and refresh to lock in improvements.",
            "include_relaxed": args.include_relaxed,
            "stale_terms": hits,
        })
        print(f"Updated {args.baseline}")
        return 0

    if args.strict and hits:
        print("Stale off-project terms found:")
        for term, paths in hits.items():
            print(f"  - {term}: {len(paths)} file(s)")
            for path in paths[:25]:
                print(f"      {path}")
        return 1

    if not baseline_path.exists():
        print(f"Missing stale-term baseline: {args.baseline}")
        print("Create it with: python3 scripts/maintenance/check_doc_stale_terms.py --root . --update")
        return 1

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    allowed = {str(k): sorted(v) for k, v in baseline.get("stale_terms", {}).items()}
    failures: list[str] = []
    for term, paths in hits.items():
        new_paths = sorted(set(paths) - set(allowed.get(term, [])))
        if new_paths:
            failures.append(f"{term}: new stale-term hits: {', '.join(new_paths[:20])}")
    for term, paths in allowed.items():
        resolved = sorted(set(paths) - set(hits.get(term, [])))
        if resolved:
            failures.append(f"{term}: stale-term hits appear resolved; refresh baseline to lock in: {', '.join(resolved[:20])}")

    if failures:
        print("Stale-term ratchet failed:")
        for failure in failures[:200]:
            print(f"  - {failure}")
        if len(failures) > 200:
            print(f"  ... {len(failures) - 200} more")
        return 1

    print("Stale-term ratchet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
