#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_JSON = DOCS / "docs_inventory.json"
OUT_MD = DOCS / "docs_inventory.md"
OUT_GAP = DOCS / "docs_gap_report.md"
OUT_PLAN = DOCS / "docs_generation_plan.md"

GENERATED = {
    "docs/docs_inventory.json",
    "docs/docs_inventory.md",
    "docs/docs_gap_report.md",
    "docs/docs_generation_plan.md",
}

IMPORTANT_DOCS = [
    "docs/release/evidence_status_registry.yml",
    "docs/release/ci_evidence.md",
    "docs/release/transaction_rollback_rollup_report.md",
    "docs/release/no_false_closure_status_after_1631_1670.md",
    "docs/architecture/transaction_boundary_inventory.md",
    "docs/architecture/router_repository_boundary_inventory.md",
]


@dataclass(frozen=True)
class DocumentInventoryItem:
    path: str
    size_bytes: int
    sha256: str
    title: str
    category: str
    generated: bool
    headings: list[dict[str, int | str]]
    links: list[dict[str, str]]
    statuses: list[str]
    dates: list[str]
    evidence_references: list[str]


@dataclass(frozen=True)
class DocumentInventory:
    generated_at: str
    commit: str
    files_scanned: int
    document_count: int
    generated_count: int
    categories: dict[str, int]
    documents: list[DocumentInventoryItem]
    missing_important_docs: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def extract_headings(text: str) -> list[dict[str, int | str]]:
    headings: list[dict[str, int | str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(
                {
                    "level": len(match.group(1)),
                    "text": match.group(2).strip(),
                    "line": lineno,
                }
            )
    return headings


def extract_title(path: Path, text: str, headings: list[dict[str, int | str]] | None = None) -> str:
    headings = headings if headings is not None else extract_headings(text)
    for heading in headings:
        if heading["level"] == 1:
            return str(heading["text"])
    if headings:
        return str(headings[0]["text"])
    return path.stem.replace("_", " ").replace("-", " ").title() or path.name


def classify(path: Path, title: str, text: str) -> str:
    haystack = f"{path.as_posix()} {title} {text[:4000]}".lower()
    if any(term in haystack for term in ["popia", "consent", "privacy", "data subject"]):
        return "compliance_popia"
    if "release" in haystack or "evidence" in haystack:
        return "release"
    if "architecture" in haystack or "adr" in haystack:
        return "architecture"
    if "security" in haystack or "auth" in haystack:
        return "security"
    if "api" in haystack or "openapi" in haystack:
        return "api"
    return "general"


def extract_statuses(text: str) -> list[str]:
    statuses: list[str] = []
    for match in re.finditer(r"\b(todo|pending|blocked|pass|passed|fail|failed|not[- ]proven|external[- ]blocked)\b", text, re.IGNORECASE):
        status = match.group(1).lower().replace(" ", "-")
        if status not in statuses:
            statuses.append(status)
    return statuses


def extract_dates(text: str) -> list[str]:
    dates: list[str] = []
    for match in re.finditer(r"\b\d{4}-\d{2}-\d{2}\b", text):
        value = match.group(0)
        if value not in dates:
            dates.append(value)
    return dates


def extract_links(path: Path, text: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    markdown_spans: list[tuple[int, int]] = []
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        target = match.group(2).strip()
        markdown_spans.append(match.span(2))
        links.append(
            {
                "text": match.group(1).strip(),
                "target": target,
                "kind": "external" if target.startswith(("http://", "https://")) else "local",
            }
        )

    for match in re.finditer(r"https?://[^\s)]+", text):
        if any(start <= match.start() < end for start, end in markdown_spans):
            continue
        links.append({"text": match.group(0), "target": match.group(0), "kind": "external"})
    return links


def extract_local_path_references(text: str) -> list[str]:
    references: list[str] = []
    for match in re.finditer(r"\b(?:docs|app|scripts|tests)/[A-Za-z0-9_./-]+", text):
        value = match.group(0).rstrip(".,);:")
        if value not in references:
            references.append(value)
    return references


def extract_evidence_references(links: list[dict[str, str]], local_paths: list[str]) -> list[str]:
    refs: list[str] = []
    candidates = [link["target"] for link in links if link.get("kind") == "local"] + local_paths
    for candidate in candidates:
        lowered = candidate.lower()
        if "evidence" in lowered or lowered.startswith("docs/release/"):
            if candidate not in refs:
                refs.append(candidate)
    return refs


def _category(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("docs/release/"):
        return "release"
    if rel.startswith("docs/architecture/"):
        return "architecture"
    if rel.startswith("docs/security/"):
        return "security"
    if rel.startswith("docs/adr/"):
        return "adr"
    if rel.startswith("docs/api") or rel.startswith("docs/openapi"):
        return "api"
    return "general"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _title(path: Path) -> str:
    if path.suffix.lower() not in {".md", ".markdown"}:
        return path.name
    text = _read_text(path)
    return extract_title(path, text, extract_headings(text))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iter_docs(source_roots: list[Path] | None = None) -> list[Path]:
    if source_roots:
        paths: list[Path] = []
        for source in source_roots:
            resolved = source if source.is_absolute() else ROOT / source
            if resolved.is_file():
                paths.append(resolved)
                continue
            if resolved.is_dir():
                for pattern in ["**/*.md", "**/*.json", "**/*.yml", "**/*.yaml"]:
                    paths.extend(resolved.glob(pattern))
        return sorted({path for path in paths if path.is_file()})
    if not DOCS.exists():
        return []
    paths: list[Path] = []
    for pattern in ["**/*.md", "**/*.json", "**/*.yml", "**/*.yaml"]:
        paths.extend(DOCS.glob(pattern))
    return sorted({path for path in paths if path.is_file()})


def build_inventory(source_roots: list[Path] | None = None) -> DocumentInventory:
    items: list[DocumentInventoryItem] = []
    categories: dict[str, int] = {}

    for path in iter_docs(source_roots):
        rel = path.relative_to(ROOT).as_posix()
        if rel in GENERATED:
            # Generated files are represented when they already exist, but the
            # generator computes drift from non-generated source docs.
            generated = True
        else:
            generated = False

        text = "" if generated else _read_text(path)
        headings = [] if generated else extract_headings(text)
        title = path.name if generated else extract_title(path, text, headings)
        links = [] if generated else extract_links(path, text)
        local_refs = [] if generated else extract_local_path_references(text)
        category = _category(path) if rel.startswith("docs/") else classify(path, title, text)
        categories[category] = categories.get(category, 0) + 1
        items.append(
            DocumentInventoryItem(
                path=rel,
                size_bytes=0 if generated else path.stat().st_size,
                sha256="GENERATED" if generated else _sha(path),
                title=title,
                category=category,
                generated=generated,
                headings=headings,
                links=links,
                statuses=[] if generated else extract_statuses(text),
                dates=[] if generated else extract_dates(text),
                evidence_references=[] if generated else extract_evidence_references(links, local_refs),
            )
        )

    missing = [path for path in IMPORTANT_DOCS if not (ROOT / path).exists()]

    return DocumentInventory(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        commit=current_commit(),
        files_scanned=len(items),
        document_count=len(items),
        generated_count=sum(1 for item in items if item.generated),
        categories=dict(sorted(categories.items())),
        documents=items,
        missing_important_docs=missing,
    )


def _stable_payload(inventory: DocumentInventory) -> dict:
    payload = asdict(inventory)
    # Do not include wall-clock timestamp in check comparisons.
    payload["generated_at"] = "STABLE"
    return payload


def render_json(inventory: DocumentInventory) -> str:
    return json.dumps(asdict(inventory), indent=2, sort_keys=True) + "\n"


def render_md(inventory: DocumentInventory) -> str:
    lines = [
        "# Documentation Inventory",
        "",
        f"Generated at: `{inventory.generated_at}`",
        f"Commit: `{inventory.commit}`",
        "",
        f"- Documents: `{inventory.document_count}`",
        f"- Generated docs: `{inventory.generated_count}`",
        "",
        "## Categories",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for category, count in inventory.categories.items():
        lines.append(f"| `{category}` | {count} |")

    lines.extend(["", "## Documents", "", "| Path | Category | Title | Size | Generated |", "|---|---|---|---:|---:|"])
    for item in inventory.documents:
        lines.append(f"| `{item.path}` | `{item.category}` | {item.title} | {item.size_bytes} | {item.generated} |")

    return "\n".join(lines) + "\n"


def render_gap(inventory: DocumentInventory) -> str:
    lines = [
        "# Documentation Gap Report",
        "",
        f"Generated at: `{inventory.generated_at}`",
        f"Commit: `{inventory.commit}`",
        "",
        "## Important document coverage",
        "",
        "| Required document | Present |",
        "|---|---:|",
    ]
    missing = set(inventory.missing_important_docs)
    for path in IMPORTANT_DOCS:
        lines.append(f"| `{path}` | {path not in missing} |")

    lines.extend(["", "## Gaps", ""])
    if inventory.missing_important_docs:
        lines.extend(f"- Missing `{path}`" for path in inventory.missing_important_docs)
    else:
        lines.append("- No required documentation intelligence gaps detected.")

    lines.extend(
        [
            "",
            "## No false-closure note",
            "",
            "This report tracks documentation intelligence freshness. It does not prove CI authority, external approvals, staging readiness, or production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def render_generation_plan(inventory: DocumentInventory) -> str:
    lines = [
        "# Documentation Generation Plan",
        "",
        "## Inputs",
        "",
        f"- Files scanned: `{inventory.files_scanned}`",
        f"- Generated docs: `{inventory.generated_count}`",
        "",
        "## Next Artifacts",
        "",
        "- Refresh the inventory before generating release summaries.",
        "- Use evidence references from the inventory for higher-level documents.",
        "- Keep external approval, CI authority, and staging evidence separate from documentation freshness.",
        "",
    ]
    return "\n".join(lines)


def _output_paths(output_dir: Path) -> tuple[Path, Path, Path, Path]:
    return (
        output_dir / "docs_inventory.json",
        output_dir / "docs_inventory.md",
        output_dir / "docs_gap_report.md",
        output_dir / "docs_generation_plan.md",
    )


def write_inventory(source_roots: list[Path] | None = None, output_dir: Path | None = None) -> DocumentInventory:
    inventory = build_inventory(source_roots)
    output_dir = output_dir or DOCS
    output_dir.mkdir(parents=True, exist_ok=True)
    out_json, out_md, out_gap, out_plan = _output_paths(output_dir)
    out_json.write_text(render_json(inventory), encoding="utf-8")
    out_md.write_text(render_md(inventory), encoding="utf-8")
    out_gap.write_text(render_gap(inventory), encoding="utf-8")
    out_plan.write_text(render_generation_plan(inventory), encoding="utf-8")
    return inventory


def check_inventory() -> list[str]:
    expected = build_inventory()

    errors: list[str] = []
    expected_json = json.loads(render_json(expected))
    if OUT_JSON.exists():
        actual_json = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        expected_stable = expected_json | {"generated_at": "STABLE"}
        actual_stable = actual_json | {"generated_at": "STABLE"}
        # Commit may legitimately change between generation and check after a
        # commit. Treat it as informational for drift.
        expected_stable["commit"] = "STABLE"
        actual_stable["commit"] = "STABLE"
        if expected_stable != actual_stable:
            errors.append("docs/docs_inventory.json is stale")
    else:
        errors.append("docs/docs_inventory.json is missing")

    if not OUT_MD.exists():
        errors.append("docs/docs_inventory.md is missing")
    if not OUT_GAP.exists():
        errors.append("docs/docs_gap_report.md is missing")
    if not OUT_PLAN.exists():
        errors.append("docs/docs_generation_plan.md is missing")

    if expected.missing_important_docs:
        errors.append("Missing important docs: " + ", ".join(expected.missing_important_docs))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated docs intelligence is stale")
    parser.add_argument("--write", action="store_true", help="write generated docs intelligence artifacts")
    parser.add_argument("--source-root", action="append", default=[], help="file or directory to inventory")
    parser.add_argument("--output-dir", default=str(DOCS), help="directory for generated inventory artifacts")
    args = parser.parse_args()

    if args.check:
        errors = check_inventory()
        if errors:
            for error in errors:
                print(f"- FAIL {error}")
            return 1
        print("Documentation intelligence inventory is current.")
        return 0

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    source_roots = [Path(path) for path in args.source_root] or None
    inventory = write_inventory(source_roots, output_dir)
    out_json, out_md, out_gap, out_plan = _output_paths(output_dir)
    print(f"Wrote {out_json.relative_to(ROOT) if out_json.is_relative_to(ROOT) else out_json}")
    print(f"Wrote {out_md.relative_to(ROOT) if out_md.is_relative_to(ROOT) else out_md}")
    print(f"Wrote {out_gap.relative_to(ROOT) if out_gap.is_relative_to(ROOT) else out_gap}")
    print(f"Wrote {out_plan.relative_to(ROOT) if out_plan.is_relative_to(ROOT) else out_plan}")
    print(f"Documents: {inventory.document_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
