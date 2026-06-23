#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from doc_utils import (
    iter_markdown,
    markdown_h1,
    parse_front_matter,
    parse_lfs_gitattributes,
    read_markdown_document,
    relpath,
    should_relax_metadata,
    write_json_deterministic,
)

RISKY_TERMS = [
    "production-ready",
    "production ready",
    "release-ready",
    "release ready",
    "launch approved",
    "fully complete",
    "all tests pass",
    "green baseline",
    "DBE AI Expert",
    "Cosmos DB",
    "Azure ML",
    "Neo4j",
]

LOCAL_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
MAX_LINK_TARGET_LEN = 2048
SCHEMA_VERSION = "doc-inventory/v2-deterministic-lfs-aware"


def target_exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False


def count_local_broken_links(path: Path, root: Path, text: str) -> int:
    count = 0
    for match in LOCAL_LINK_RE.finditer(text):
        raw = match.group(1).strip()
        if not raw or raw.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw):
            if raw.startswith("file://"):
                count += 1
            continue
        target_part = raw.split("#", 1)[0].strip()
        if not target_part:
            continue
        if target_part.startswith("<") and target_part.endswith(">"):
            target_part = target_part[1:-1]
        if len(target_part) > MAX_LINK_TARGET_LEN:
            continue
        target = (root / target_part[1:]) if target_part.startswith("/") else (path.parent / target_part)
        if not target_exists(target):
            count += 1
    return count


def normalise_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(rows, key=lambda r: str(r["path"]))


def normalise_findings(findings: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(findings, key=lambda r: (str(r["severity"]), str(r["type"]), str(r["path"]), str(r["detail"])))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic EduBoost documentation inventory and findings.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-json", default="")
    parser.add_argument("--out-csv", default="")
    parser.add_argument("--out-findings", default="")
    parser.add_argument("--strict-legacy", action="store_true", help="Include archive/generated/evidence areas in findings.")
    parser.add_argument("--include-run-metadata", action="store_true", help="Include timestamp and absolute root. Do not use for committed inventory.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    lfs_patterns = parse_lfs_gitattributes(root)
    rows: list[dict[str, object]] = []
    findings: list[dict[str, object]] = []
    titles: dict[str, list[str]] = defaultdict(list)
    dir_counts: Counter[str] = Counter()
    finding_counts: Counter[str] = Counter()

    for path in sorted(iter_markdown(root), key=lambda p: relpath(p, root)):
        doc = read_markdown_document(path, root, lfs_patterns)
        rel = doc.rel
        text = doc.text
        meta = parse_front_matter(text)
        title = str(meta.get("title") or markdown_h1(text) or "")
        h1 = markdown_h1(text) or ""
        status = str(meta.get("status") or "")
        owner = str(meta.get("owner") or "")
        audience = str(meta.get("audience") or "")
        source_of_truth = meta.get("source_of_truth", "")
        relaxed_legacy = should_relax_metadata(rel)
        if doc.content_kind == "git_lfs_tracked_skipped_content":
            line_count = 0
            byte_count = doc.lfs_size
            broken_links = 0
            risky_hits: list[str] = []
        else:
            line_count = text.count("\n") + 1 if text else 0
            byte_count = len(text.encode("utf-8"))
            risky_hits = [term for term in RISKY_TERMS if term.lower() in text.lower()]
            broken_links = count_local_broken_links(path, root, text)
        first_dir = "/".join(rel.split("/")[:2]) if "/" in rel else "."
        dir_counts[first_dir] += 1
        if title:
            titles[title.lower()].append(rel)
        row = {
            "path": rel,
            "content_kind": doc.content_kind,
            "lfs_sha256": doc.lfs_sha256,
            "lfs_size": doc.lfs_size,
            "title": title,
            "h1": h1,
            "status": status,
            "owner": owner,
            "audience": audience,
            "source_of_truth": source_of_truth,
            "last_reviewed": meta.get("last_reviewed", ""),
            "review_interval_days": meta.get("review_interval_days", ""),
            "line_count": line_count,
            "byte_count": byte_count,
            "risky_terms": ";".join(risky_hits),
            "broken_local_links": broken_links,
            "has_front_matter": bool(meta),
        }
        rows.append(row)
        if doc.content_kind == "git_lfs_tracked_skipped_content":
            # LFS markdown is tracked deterministically by oid/size, but content checks are skipped
            # because GitHub source ZIPs contain pointers while git-lfs clones contain expanded content.
            pass
        elif not meta and (args.strict_legacy or not relaxed_legacy):
            finding = {"severity": "medium", "type": "missing_metadata", "path": rel, "detail": "No YAML front matter"}
            findings.append(finding)
            finding_counts[finding["type"]] += 1
        if doc.content_kind != "git_lfs_tracked_skipped_content" and risky_hits and (args.strict_legacy or not relaxed_legacy):
            finding = {"severity": "high", "type": "risky_or_stale_terms", "path": rel, "detail": "; ".join(risky_hits)}
            findings.append(finding)
            finding_counts[finding["type"]] += 1
        if broken_links and (args.strict_legacy or not relaxed_legacy):
            finding = {"severity": "high", "type": "broken_local_links", "path": rel, "detail": str(broken_links)}
            findings.append(finding)
            finding_counts[finding["type"]] += 1
        if line_count > 500 and (args.strict_legacy or not relaxed_legacy):
            finding = {"severity": "low", "type": "oversized_document", "path": rel, "detail": f"{line_count} lines"}
            findings.append(finding)
            finding_counts[finding["type"]] += 1

    for title, paths in sorted(titles.items()):
        if title and len(paths) > 1:
            for rel in sorted(paths):
                finding = {"severity": "medium", "type": "duplicate_title", "path": rel, "detail": f"Duplicate title appears in {len(paths)} files"}
                findings.append(finding)
                finding_counts[finding["type"]] += 1

    rows = normalise_rows(rows)
    findings = normalise_findings(findings)
    finding_counts = Counter(str(item["type"]) for item in findings)
    summary: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "inventory_mode": "deterministic-lfs-aware",
        "repository_root": ".",
        "markdown_files": len(rows),
        "files_with_metadata": sum(1 for r in rows if r["has_front_matter"]),
        "files_with_owner": sum(1 for r in rows if r["owner"]),
        "files_with_source_of_truth": sum(1 for r in rows if str(r["source_of_truth"]).lower() in {"true", "yes"}),
        "lfs_tracked_markdown_files": sum(1 for r in rows if r["content_kind"] == "git_lfs_tracked_skipped_content"),
        "broken_local_link_count": sum(
            int(r["broken_local_links"])
            for r in rows
            if args.strict_legacy or not should_relax_metadata(str(r["path"]))
        ),
        "finding_count": len(findings),
        "finding_counts_by_type": dict(sorted(finding_counts.items())),
        "top_directories": [[name, count] for name, count in dir_counts.most_common(30)],
    }
    if args.include_run_metadata:
        summary["generated_at"] = datetime.now(timezone.utc).isoformat()
        summary["absolute_root"] = str(root)

    inventory_payload = {"summary": summary, "documents": rows, "findings": findings}

    if args.out_csv:
        out = root / args.out_csv
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=list(rows[0].keys()) if rows else ["path"],
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
    if args.out_findings:
        out = root / args.out_findings
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="") as f:
            fieldnames = ["severity", "type", "path", "detail"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(findings)
    if args.out_json:
        write_json_deterministic(root / args.out_json, inventory_payload)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
