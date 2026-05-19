#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_JSON = DOCS / "docs_inventory.json"
OUT_MD = DOCS / "docs_inventory.md"
OUT_GAP = DOCS / "docs_gap_report.md"

GENERATED = {
    "docs/docs_inventory.json",
    "docs/docs_inventory.md",
    "docs/docs_gap_report.md",
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


@dataclass(frozen=True)
class DocumentInventory:
    generated_at: str
    commit: str
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


def _title(path: Path) -> str:
    if path.suffix.lower() not in {".md", ".markdown"}:
        return path.name
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip() or path.name
    except Exception:
        return path.name
    return path.name


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iter_docs() -> list[Path]:
    if not DOCS.exists():
        return []
    paths: list[Path] = []
    for pattern in ["**/*.md", "**/*.json", "**/*.yml", "**/*.yaml"]:
        paths.extend(DOCS.glob(pattern))
    return sorted({path for path in paths if path.is_file()})


def build_inventory() -> DocumentInventory:
    items: list[DocumentInventoryItem] = []
    categories: dict[str, int] = {}

    for path in iter_docs():
        rel = path.relative_to(ROOT).as_posix()
        if rel in GENERATED:
            # Generated files are represented when they already exist, but the
            # generator computes drift from non-generated source docs.
            generated = True
        else:
            generated = False

        category = _category(path)
        categories[category] = categories.get(category, 0) + 1
        items.append(
            DocumentInventoryItem(
                path=rel,
                size_bytes=0 if generated else path.stat().st_size,
                sha256="GENERATED" if generated else _sha(path),
                title=_title(path),
                category=category,
                generated=generated,
            )
        )

    missing = [path for path in IMPORTANT_DOCS if not (ROOT / path).exists()]

    return DocumentInventory(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        commit=current_commit(),
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


def write_inventory() -> DocumentInventory:
    inventory = build_inventory()
    OUT_JSON.write_text(render_json(inventory), encoding="utf-8")
    OUT_MD.write_text(render_md(inventory), encoding="utf-8")
    OUT_GAP.write_text(render_gap(inventory), encoding="utf-8")
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

    if expected.missing_important_docs:
        errors.append("Missing important docs: " + ", ".join(expected.missing_important_docs))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated docs intelligence is stale")
    parser.add_argument("--write", action="store_true", help="write generated docs intelligence artifacts")
    args = parser.parse_args()

    if args.check:
        errors = check_inventory()
        if errors:
            for error in errors:
                print(f"- FAIL {error}")
            return 1
        print("Documentation intelligence inventory is current.")
        return 0

    inventory = write_inventory()
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_GAP.relative_to(ROOT)}")
    print(f"Documents: {inventory.document_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
