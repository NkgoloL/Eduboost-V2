from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "docs/architecture/diagnostic_item_bank_canonicality.yml"
STATUS_JSON = ROOT / "docs/release/diagnostic_item_bank_canonicality_status.json"
STATUS_MD = ROOT / "docs/release/diagnostic_item_bank_canonicality_status.md"

CANONICAL_TABLE = "diagnostic_items"
SUPPORTING_TABLE = "irt_items"
UNRESOLVED_BLOCKER = "DIAG-SCORE-001"

REQUIRED_POLICY_MARKERS = [
    "decision: diagnostic_items-runtime-required",
    "canonical_item_bank: diagnostic_items",
    "supporting_item_bank: irt_items",
    "classification: runtime-required",
    "expected_min_rows: 1",
    "beta_blocking_when_empty: true",
    "migration_action: seed-required",
    "unresolved_blocker: DIAG-SCORE-001",
]


@dataclass(frozen=True)
class ReferenceRecord:
    path: str
    line_number: int
    line_excerpt: str
    runtime_surface: bool


@dataclass(frozen=True)
class DiagnosticItemBankCanonicalityStatus:
    generated_at: str
    current_commit: str
    status: str
    policy_path: str
    decision: str
    canonical_table: str
    supporting_table: str
    unresolved_blocker: str
    policy_markers_present: dict[str, bool]
    diagnostic_items_references: list[ReferenceRecord]
    runtime_diagnostic_items_references: list[ReferenceRecord]
    blockers: list[str]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def current_commit() -> str:
    result = _run(["git", "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _candidate_files() -> list[Path]:
    roots = [
        ROOT / "app",
        ROOT / "backend",
        ROOT / "alembic",
        ROOT / "scripts",
        ROOT / "tests",
        ROOT / "docs",
    ]
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for suffix in ("*.py", "*.md", "*.yml", "*.yaml"):
            files.extend(path for path in root.rglob(suffix) if path.is_file())
    return sorted(set(files))


def _is_runtime_surface(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return rel.startswith("app/") or rel.startswith("backend/")


def _scan_references(token: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    pattern = re.compile(rf"\b{re.escape(token)}\b")

    for path in _candidate_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("docs/docs_"):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            if pattern.search(line):
                records.append(
                    ReferenceRecord(
                        path=rel,
                        line_number=line_number,
                        line_excerpt=line.strip()[:240],
                        runtime_surface=_is_runtime_surface(path),
                    )
                )

    return records


def _policy_markers() -> dict[str, bool]:
    text = POLICY_PATH.read_text(encoding="utf-8") if POLICY_PATH.exists() else ""
    return {marker: marker in text for marker in REQUIRED_POLICY_MARKERS}


def write_status() -> DiagnosticItemBankCanonicalityStatus:
    blockers: list[str] = []

    if not POLICY_PATH.exists():
        blockers.append("diagnostic item-bank canonicality policy file is missing")

    markers = _policy_markers()
    for marker, present in markers.items():
        if not present:
            blockers.append(f"policy missing marker: {marker}")

    diagnostic_refs = _scan_references(CANONICAL_TABLE)
    runtime_refs = [record for record in diagnostic_refs if record.runtime_surface]

    if not diagnostic_refs:
        blockers.append("no diagnostic_items references found; runtime-required policy is unsupported")

    if not runtime_refs:
        blockers.append(
            "no runtime diagnostic_items references found; policy should be reconsidered before marking runtime-required"
        )

    status = (
        "diagnostic-item-bank-policy-accepted"
        if not blockers
        else "diagnostic-item-bank-policy-not-proven"
    )

    result = DiagnosticItemBankCanonicalityStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status=status,
        policy_path=str(POLICY_PATH.relative_to(ROOT)),
        decision="diagnostic_items-runtime-required",
        canonical_table=CANONICAL_TABLE,
        supporting_table=SUPPORTING_TABLE,
        unresolved_blocker=UNRESOLVED_BLOCKER,
        policy_markers_present=markers,
        diagnostic_items_references=diagnostic_refs,
        runtime_diagnostic_items_references=runtime_refs,
        blockers=blockers,
    )

    STATUS_JSON.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    _write_markdown(result)
    return result


def _write_markdown(status: DiagnosticItemBankCanonicalityStatus) -> None:
    lines = [
        "# Diagnostic Item-Bank Policy Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**Policy:** `{status.policy_path}`",
        f"**Decision:** `{status.decision}`",
        f"**Canonical table:** `{status.canonical_table}`",
        f"**Supporting table:** `{status.supporting_table}`",
        f"**Unresolved blocker:** `{status.unresolved_blocker}`",
        "",
        "## Policy markers",
        "",
        "| Marker | Present |",
        "|---|---:|",
    ]

    for marker, present in status.policy_markers_present.items():
        lines.append(f"| `{marker}` | {present} |")

    lines.extend(
        [
            "",
            "## Runtime diagnostic_items references",
            "",
            "| Path | Line | Excerpt |",
            "|---|---:|---|",
        ]
    )

    if status.runtime_diagnostic_items_references:
        for record in status.runtime_diagnostic_items_references:
            lines.append(
                f"| `{record.path}` | {record.line_number} | `{record.line_excerpt}` |"
            )
    else:
        lines.append("| `-` | 0 | `none` |")

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- This policy does not close DIAG-SCORE-001.",
            "- Empty `diagnostic_items` remains beta-blocking under DIAG-SCORE-001.",
            "- This policy does not seed `diagnostic_items`.",
            "- This policy does not prove scoring quality, item exposure correctness, or adaptive recommendation behavior.",
            "- This policy supersedes the earlier attempted `irt_items`-canonical-only classification.",
            "",
        ]
    )

    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    result = write_status()
    print(result.status)
    if result.blockers:
        for blocker in result.blockers:
            print(f"- {blocker}")
        raise SystemExit(1)
