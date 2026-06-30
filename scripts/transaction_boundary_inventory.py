from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    ROOT / "app/api_v2_routers",
    ROOT / "app/services",
    ROOT / "app/modules",
]
OUT_JSON = ROOT / "docs/architecture/transaction_boundary_inventory.json"
OUT_MD = ROOT / "docs/architecture/transaction_boundary_inventory.md"

MUTATION_METHODS = {
    "add",
    "delete",
    "commit",
    "flush",
    "execute",
    "merge",
    "create",
    "update",
    "upsert",
    "revoke",
    "grant",
    "deny",
    "withdraw",
    "renew",
    "complete",
    "award",
    "store",
    "consume",
    "save",
}

TRANSACTION_MARKERS = {
    "begin",
    "transaction",
    "unit_of_work",
    "UnitOfWork",
    "atomic",
    "rollback",
}

CRITICAL_AREAS = {
    "auth_register": ["register", "create_dev_session"],
    "auth_refresh": ["refresh", "consume_refresh", "refresh_token"],
    "popia_lifecycle": ["consent", "grant", "deny", "withdraw", "renew", "revoke"],
    "diagnostics_response": ["diagnostic", "respond", "submit", "mastery", "theta"],
    "lesson_completion": ["lesson", "complete", "gamification", "xp"],
}


@dataclass(frozen=True)
class FunctionMutationFinding:
    file: str
    function: str
    lineno: int
    mutation_calls: list[str] = field(default_factory=list)
    transaction_markers: list[str] = field(default_factory=list)
    critical_areas: list[str] = field(default_factory=list)
    status: str = "not-classified"


@dataclass(frozen=True)
class TransactionBoundaryInventory:
    generated_at: str
    scan_roots: list[str]
    findings: list[FunctionMutationFinding]
    candidate_count: int
    critical_candidate_count: int
    policy: str


def _iter_python_files() -> Iterable[Path]:
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        yield from sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
    return None


def _contains_marker(text: str, markers: set[str]) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for marker in markers:
        if marker.lower() in lowered:
            found.append(marker)
    return sorted(set(found), key=str.lower)


def _critical_areas(file: str, function: str, text: str) -> list[str]:
    blob = f"{file} {function} {text}".lower()
    areas: list[str] = []
    for area, needles in CRITICAL_AREAS.items():
        if all(needle.lower() in blob for needle in needles[:1]) and any(needle.lower() in blob for needle in needles[1:]):
            areas.append(area)
    return sorted(set(areas))


def _source_segment(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return ""
    return segment


def _scan_function(path: Path, source: str, node: ast.AST) -> FunctionMutationFinding | None:
    function_name = getattr(node, "name", "<unknown>")
    calls: list[str] = []
    for child in ast.walk(node):
        name = _call_name(child)
        if name and name in MUTATION_METHODS:
            calls.append(name)

    if not calls:
        return None

    rel = path.relative_to(ROOT).as_posix()
    text = _source_segment(source, node)
    transaction_markers = _contains_marker(text, TRANSACTION_MARKERS)
    areas = _critical_areas(rel, function_name, text)

    unique_calls = sorted(set(calls), key=str.lower)
    if transaction_markers:
        status = "transaction-marker-present"
    elif len(unique_calls) >= 2 or areas:
        status = "multi-write-candidate-not-proven"
    else:
        status = "single-mutation-candidate"

    return FunctionMutationFinding(
        file=rel,
        function=function_name,
        lineno=getattr(node, "lineno", 0),
        mutation_calls=unique_calls,
        transaction_markers=transaction_markers,
        critical_areas=areas,
        status=status,
    )


def generate_inventory() -> TransactionBoundaryInventory:
    findings: list[FunctionMutationFinding] = []
    for path in _iter_python_files():
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                finding = _scan_function(path, source, node)
                if finding is not None:
                    findings.append(finding)

    candidate_count = sum(1 for finding in findings if "candidate" in finding.status)
    critical_candidate_count = sum(1 for finding in findings if finding.critical_areas)
    return TransactionBoundaryInventory(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        scan_roots=[root.relative_to(ROOT).as_posix() for root in SCAN_ROOTS],
        findings=sorted(findings, key=lambda item: (item.file, item.lineno, item.function)),
        candidate_count=candidate_count,
        critical_candidate_count=critical_candidate_count,
        policy="Multi-write candidates remain not-proven until rollback/integration tests demonstrate atomicity.",
    )


def write_inventory(inventory: TransactionBoundaryInventory) -> None:
    OUT_JSON.write_text(json.dumps(asdict(inventory), indent=2), encoding="utf-8")
    lines = [
        "# Transaction Boundary Inventory",
        "",
        f"Generated at: `{inventory.generated_at}`",
        "",
        f"Candidate count: `{inventory.candidate_count}`",
        f"Critical candidate count: `{inventory.critical_candidate_count}`",
        "",
        f"Policy: {inventory.policy}",
        "",
        "| File | Function | Line | Status | Critical areas | Mutation calls | Transaction markers |",
        "|---|---|---:|---|---|---|---|",
    ]
    for finding in inventory.findings:
        lines.append(
            "| "
            f"`{finding.file}` | `{finding.function}` | {finding.lineno} | `{finding.status}` | "
            f"`{', '.join(finding.critical_areas) or '-'}` | "
            f"`{', '.join(finding.mutation_calls) or '-'}` | "
            f"`{', '.join(finding.transaction_markers) or '-'}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    inventory = generate_inventory()
    write_inventory(inventory)
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Candidates: {inventory.candidate_count}")
    print(f"Critical candidates: {inventory.critical_candidate_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
