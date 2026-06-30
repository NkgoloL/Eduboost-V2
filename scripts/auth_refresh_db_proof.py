from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_JSON = ROOT / "docs/release/auth_refresh_db_proof_status.json"
STATUS_MD = ROOT / "docs/release/auth_refresh_db_proof_status.md"
EVIDENCE_MD = ROOT / "docs/release/auth_refresh_db_proof_evidence.md"

REQUIRED_FIELDS = [
    "Database DSN label",
    "Test command",
    "Test result",
    "Refresh persistence result",
    "Logout revocation result",
    "Revoke-all result",
    "Reuse detection result",
    "Evidence URL",
    "Commit SHA",
    "Verified by",
    "Date verified",
]

RESULT_FIELDS = {
    "Test result",
    "Refresh persistence result",
    "Logout revocation result",
    "Revoke-all result",
    "Reuse detection result",
}

PASS_VALUES = {"pass", "passed", "green", "ok", "success", "successful"}
PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}
PLACEHOLDER_TOKENS = {"example.com", "placeholder", "<", ">", "dummy", "fake", "test-only"}


@dataclass(frozen=True)
class EvidenceField:
    name: str
    value: str
    valid: bool
    reason: str


@dataclass(frozen=True)
class AuthRefreshDbProofStatus:
    generated_at: str
    current_commit: str
    status: str
    dsn_present: bool
    pytest_return_code: int | None
    pytest_summary: str
    evidence_fields: list[EvidenceField]
    blockers: list[str]
    no_false_closure_rules: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def evidence_template() -> str:
    lines = ["# Auth Refresh DB Proof Evidence", "", "**Item:** AUTH-REFRESH-DB-PROOF-001", ""]
    for field in REQUIRED_FIELDS:
        lines.extend([f"**{field}:** pending", ""])
    lines.extend(
        [
            "## Required proof",
            "",
            "- Refresh token is persisted after login/refresh flow.",
            "- Logout invalidates the active refresh token.",
            "- Revoke-all invalidates all user refresh tokens.",
            "- Reuse of an already-consumed refresh token is rejected.",
            "- Tests execute against a disposable real DB target, not a mock-only harness.",
            "",
            "## No false-closure rule",
            "",
            "This file is not proof while any required field is pending or any result field is not `passed`.",
            "",
        ]
    )
    return "\n".join(lines)


def write_evidence_template() -> None:
    if EVIDENCE_MD.exists() and "**Item:** AUTH-REFRESH-DB-PROOF-001" in EVIDENCE_MD.read_text(encoding="utf-8"):
        return
    EVIDENCE_MD.write_text(evidence_template(), encoding="utf-8")


def _field(text: str, name: str) -> str:
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip().strip("`").strip() if match else ""


def _pending(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token in lowered for token in PLACEHOLDER_TOKENS)


def _url(value: str) -> bool:
    return not _placeholder(value) and (value.startswith("https://") or value.startswith("http://"))


def _sha(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{7,40}", value.strip()))


def evidence_fields() -> list[EvidenceField]:
    write_evidence_template()
    text = EVIDENCE_MD.read_text(encoding="utf-8")
    fields: list[EvidenceField] = []
    for name in REQUIRED_FIELDS:
        value = _field(text, name)
        if _pending(value):
            fields.append(EvidenceField(name, value, False, "pending"))
        elif _placeholder(value):
            fields.append(EvidenceField(name, value, False, "placeholder value"))
        elif name in RESULT_FIELDS and value.strip().lower() not in PASS_VALUES:
            fields.append(EvidenceField(name, value, False, "must be passed"))
        elif name == "Evidence URL" and not _url(value):
            fields.append(EvidenceField(name, value, False, "must be non-placeholder URL"))
        elif name == "Commit SHA" and not _sha(value):
            fields.append(EvidenceField(name, value, False, "must look like git SHA"))
        else:
            fields.append(EvidenceField(name, value, True, "ok"))
    return fields


def run_db_pytest() -> tuple[int | None, str]:
    dsn = os.getenv("AUTH_REFRESH_DB_PROOF_DSN", "").strip()
    if not dsn:
        return None, "AUTH_REFRESH_DB_PROOF_DSN not set; DB proof not executed"

    env = {**os.environ, "PYTHONPATH": str(ROOT), "AUTH_REFRESH_DB_PROOF_ENABLED": "1"}
    result = subprocess.run(
        [
            "python3",
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/integration/test_auth_refresh_db_proof.py",
            "-q",
            "--no-cov",
            "--tb=short",
            "-rs",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=180,
    )
    return result.returncode, result.stdout[-4000:]


def output_has_skips(summary: str) -> bool:
    lowered = summary.lower()
    return "skipped" in lowered or "= skipped" in lowered or " s " in f" {lowered} "


def build_status(run_pytest: bool = False) -> AuthRefreshDbProofStatus:
    write_evidence_template()
    dsn_present = bool(os.getenv("AUTH_REFRESH_DB_PROOF_DSN", "").strip())
    return_code: int | None = None
    summary = "DB pytest not requested"

    if run_pytest:
        return_code, summary = run_db_pytest()

    fields = evidence_fields()
    blockers: list[str] = []
    if not dsn_present:
        blockers.append("AUTH_REFRESH_DB_PROOF_DSN is not set")
    if run_pytest and return_code != 0:
        blockers.append("DB pytest did not pass")
    if run_pytest and output_has_skips(summary):
        blockers.append("DB pytest output contains skipped tests; skipped DB proof is not accepted")
    for field in fields:
        if not field.valid:
            blockers.append(f"evidence field {field.name}: {field.reason}")

    accepted = dsn_present and run_pytest and return_code == 0 and not output_has_skips(summary) and all(f.valid for f in fields)
    status = "auth-refresh-db-proof-accepted" if accepted else "auth-refresh-db-proof-external-blocked"

    return AuthRefreshDbProofStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status=status,
        dsn_present=dsn_present,
        pytest_return_code=return_code,
        pytest_summary=summary,
        evidence_fields=fields,
        blockers=blockers,
        no_false_closure_rules=[
            "Skipped DB tests are not proof.",
            "Mock-only tests are not DB proof.",
            "AUTH_REFRESH_DB_PROOF_DSN must be explicit.",
            "Release mode requires accepted DB proof evidence.",
        ],
    )


def write_status(run_pytest: bool = False) -> AuthRefreshDbProofStatus:
    status = build_status(run_pytest=run_pytest)
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Auth Refresh DB Proof Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**DSN present:** `{status.dsn_present}`",
        f"**Pytest return code:** `{status.pytest_return_code}`",
        "",
        "## Evidence fields",
        "",
        "| Field | Value | Valid | Reason |",
        "|---|---|---:|---|",
    ]
    for field in status.evidence_fields:
        lines.append(f"| `{field.name}` | `{field.value}` | {field.valid} | {field.reason} |")

    lines.extend(["", "## Pytest summary", "", "```text", status.pytest_summary[-3000:], "```", "", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in status.no_false_closure_rules)
    lines.append("")
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
