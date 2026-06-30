from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_MD = ROOT / "docs/release/auth_refresh_db_proof_evidence.md"
STATUS_JSON = ROOT / "docs/release/auth_refresh_db_evidence_status.json"
STATUS_MD = ROOT / "docs/release/auth_refresh_db_evidence_status.md"

FIELDS = [
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

ENV_MAP = {
    "Database DSN label": "AUTH_REFRESH_DB_DSN_LABEL",
    "Test command": "AUTH_REFRESH_DB_TEST_COMMAND",
    "Test result": "AUTH_REFRESH_DB_TEST_RESULT",
    "Refresh persistence result": "AUTH_REFRESH_DB_REFRESH_PERSISTENCE_RESULT",
    "Logout revocation result": "AUTH_REFRESH_DB_LOGOUT_REVOCATION_RESULT",
    "Revoke-all result": "AUTH_REFRESH_DB_REVOKE_ALL_RESULT",
    "Reuse detection result": "AUTH_REFRESH_DB_REUSE_DETECTION_RESULT",
    "Evidence URL": "AUTH_REFRESH_DB_EVIDENCE_URL",
    "Commit SHA": "AUTH_REFRESH_DB_COMMIT_SHA",
    "Verified by": "AUTH_REFRESH_DB_VERIFIED_BY",
    "Date verified": "AUTH_REFRESH_DB_DATE_VERIFIED",
}

RESULT_FIELDS = {
    "Test result",
    "Refresh persistence result",
    "Logout revocation result",
    "Revoke-all result",
    "Reuse detection result",
}

PASS_VALUES = {"pass", "passed", "green", "ok", "success", "successful"}
PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}

PLACEHOLDER_TOKENS = {
    "example.com",
    "example.org",
    "example.net",
    "<",
    ">",
    "...",
    "…",
    "placeholder",
    "fake",
    "dummy",
    "test-only",
    "sample",
    "changeme",
    "change_me",
    "change-me",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "real_run_id",
    "run_id",
    "real_id",
    "real_sha",
    "real_commit",
    "real_dsn",
    "real_auth_refresh_db_proof_dsn",
    "$real_",
    "${real_",
    "yyyy-mm-dd",
    "<sha>",
    "<name>",
    "<run_id>",
    "redacted",
    "[redacted]",
    "replace_me",
    "replace-me",
    "replace me",
}


@dataclass(frozen=True)
class FieldStatus:
    name: str
    value: str
    valid: bool
    reason: str


@dataclass(frozen=True)
class AuthRefreshDbEvidenceStatus:
    generated_at: str
    current_commit: str
    status: str
    accepted: bool
    fields: list[FieldStatus]
    blockers: list[str]


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


def normalize(value: object) -> str:
    return str(value or "").strip().strip("`").strip()


def _compact(value: object) -> str:
    return normalize(value).lower().replace("-", "_").replace(" ", "_")


def placeholder_reason(value: object) -> str | None:
    text = normalize(value)
    lowered = text.lower()
    compact = _compact(text)

    if lowered in PENDING_VALUES or lowered.startswith("pending"):
        return "pending value"

    for token in PLACEHOLDER_TOKENS:
        token_l = token.lower()
        token_compact = token_l.replace("-", "_").replace(" ", "_")
        if token_l in lowered or token_compact in compact:
            return f"contains placeholder token: {token}"

    if re.search(r"\bREAL_[A-Z0-9_]*\b", text):
        return "contains symbolic REAL_* placeholder"

    if re.search(r"\$[{]?(REAL|PLACEHOLDER|DUMMY|FAKE|TEST)[A-Z0-9_]*[}]?", text):
        return "contains symbolic shell placeholder"

    if re.search(r"<[^>]+>", text) or re.search(r"\[[^\]]*(placeholder|redacted|run|sha|url)[^\]]*\]", lowered):
        return "contains bracket placeholder"

    return None


def has_placeholder(value: object) -> bool:
    return placeholder_reason(value) is not None


def template() -> str:
    lines = ["# Auth Refresh DB Proof Evidence", "", "**Item:** AUTH-REFRESH-DB-PROOF-001", ""]
    for field in FIELDS:
        lines.extend([f"**{field}:** pending", ""])
    lines.extend(
        [
            "## Required proof",
            "",
            "- Refresh token is persisted after login/refresh flow.",
            "- Logout invalidates the active refresh token.",
            "- Revoke-all invalidates all user refresh tokens.",
            "- Reuse of an already-consumed refresh token is rejected.",
            "- Evidence URL points to CI/staging logs or an auditable proof artifact.",
            "",
            "## No false-closure rule",
            "",
            "This file is not proof while any required field is pending or placeholder-like.",
            "",
        ]
    )
    return "\n".join(lines)


def ensure_template() -> None:
    if EVIDENCE_MD.exists() and "**Item:** AUTH-REFRESH-DB-PROOF-001" in EVIDENCE_MD.read_text(encoding="utf-8"):
        return
    EVIDENCE_MD.write_text(template(), encoding="utf-8")


def parse_fields(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for field in FIELDS:
        match = re.search(rf"\*\*{re.escape(field)}:\*\*\s*(.+)", text, flags=re.IGNORECASE)
        values[field] = normalize(match.group(1)) if match else ""
    return values


def evidence_values() -> dict[str, str]:
    ensure_template()
    return parse_fields(EVIDENCE_MD.read_text(encoding="utf-8"))


def validate_field(name: str, value: object) -> FieldStatus:
    text = normalize(value)
    reason = placeholder_reason(text)
    if reason:
        return FieldStatus(name, text, False, reason)
    if name in RESULT_FIELDS and text.lower() not in PASS_VALUES:
        return FieldStatus(name, text, False, "result must be passed")
    if name == "Evidence URL":
        if not re.match(r"^https?://[^\s/$.?#].[^\s]*$", text):
            return FieldStatus(name, text, False, "must be valid URL")
        if not re.search(r"/actions/runs/\d+|/runs/\d+|/artifacts/|/builds/|/pipelines/|\d{6,}", text):
            return FieldStatus(name, text, False, "must include a concrete run/build/artifact identifier")
    if name == "Commit SHA" and not re.fullmatch(r"[0-9a-fA-F]{7,40}", text):
        return FieldStatus(name, text, False, "must look like git SHA")
    if name == "Date verified" and not re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return FieldStatus(name, text, False, "must be YYYY-MM-DD")
    return FieldStatus(name, text, True, "ok")


def build_status() -> AuthRefreshDbEvidenceStatus:
    fields = [validate_field(name, value) for name, value in evidence_values().items()]
    blockers = [f"{field.name}: {field.reason}" for field in fields if not field.valid]
    return AuthRefreshDbEvidenceStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="auth-refresh-db-evidence-accepted" if not blockers else "auth-refresh-db-evidence-external-blocked",
        accepted=not blockers,
        fields=fields,
        blockers=blockers,
    )


def render_evidence(values: dict[str, str]) -> str:
    lines = ["# Auth Refresh DB Proof Evidence", "", "**Item:** AUTH-REFRESH-DB-PROOF-001", ""]
    for field in FIELDS:
        lines.extend([f"**{field}:** {normalize(values.get(field, ''))}", ""])
    lines.extend(
        [
            "## Required proof",
            "",
            "- Refresh token is persisted after login/refresh flow.",
            "- Logout invalidates the active refresh token.",
            "- Revoke-all invalidates all user refresh tokens.",
            "- Reuse of an already-consumed refresh token is rejected.",
            "- Evidence URL points to CI/staging logs or an auditable proof artifact.",
            "",
            "## No false-closure rule",
            "",
            "This file is not proof while any required field is pending or placeholder-like.",
            "",
        ]
    )
    return "\n".join(lines)


def attach_from_env() -> AuthRefreshDbEvidenceStatus:
    values = {field: normalize(os.getenv(env_name, "")) for field, env_name in ENV_MAP.items()}
    field_statuses = [validate_field(name, value) for name, value in values.items()]
    blockers = [f"{field.name}: {field.reason}" for field in field_statuses if not field.valid]
    if blockers:
        raise SystemExit("Refusing to attach invalid auth refresh DB evidence:\n- " + "\n- ".join(blockers))
    EVIDENCE_MD.write_text(render_evidence(values), encoding="utf-8")
    return write_status()


def write_status() -> AuthRefreshDbEvidenceStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# Auth Refresh DB Evidence Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**Accepted:** `{status.accepted}`",
        "",
        "| Field | Value | Valid | Reason |",
        "|---|---|---:|---|",
    ]
    for field in status.fields:
        lines.append(f"| `{field.name}` | `{field.value}` | {field.valid} | {field.reason} |")
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
            "- Accepted metadata does not independently verify remote URLs.",
            "- Accepted metadata must still correspond to real DB-backed test logs.",
            "- Placeholder-like accepted evidence is reclassified to external-blocked.",
            "- This evidence gate does not approve beta release.",
            "",
        ]
    )
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
