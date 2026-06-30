from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone, timedelta
import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS_JSON = ROOT / "docs/release/jwt_secret_rotation_evidence_status.json"
STATUS_MD = ROOT / "docs/release/jwt_secret_rotation_evidence_status.md"
ACCEPTED_STATUS = "jwt-secret-rotation-accepted"
NOT_ACCEPTED_STATUS = "jwt-secret-rotation-not-accepted"
MIN_SECRET_LENGTH = 32
ALGORITHM = "HS256"
PLACEHOLDER_TOKENS = {"<", ">", "TODO", "TBD", "REAL_", "example.com", "changeme", "change-me", "secret", "password", "dev-only", "..."}

@dataclass(frozen=True)
class GitHubRunEvidence:
    run_id: str
    run_url: str
    workflow_name: str
    run_status: str
    conclusion: str
    head_sha: str
    blockers: list[str]

@dataclass(frozen=True)
class SecretEvidence:
    present: bool
    length: int
    fingerprint: str
    placeholder_like: bool

@dataclass(frozen=True)
class TokenSelfTest:
    access_issue_verify: bool
    refresh_issue_verify: bool
    access_tamper_rejected: bool
    refresh_tamper_rejected: bool
    access_refresh_separated: bool
    blockers: list[str]

@dataclass(frozen=True)
class JwtSecretRotationEvidenceStatus:
    generated_at: str
    current_commit: str
    status: str
    evidence_environment: str
    algorithm: str
    secret_store: str
    rotation_reference: str
    rotation_date: str
    rotation_result: str
    access_current: SecretEvidence
    refresh_current: SecretEvidence
    access_previous_fingerprint: str
    refresh_previous_fingerprint: str
    access_rotated: bool
    refresh_rotated: bool
    token_self_test: TokenSelfTest
    github_run: GitHubRunEvidence
    verified_by: str
    date_verified: str
    blockers: list[str]

def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)

def current_commit() -> str:
    r = _run(["git", "rev-parse", "HEAD"])
    return r.stdout.strip() if r.returncode == 0 else "unknown"

def _env(name: str) -> str:
    return os.getenv(name, "").strip()

def has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token.lower() in lowered for token in PLACEHOLDER_TOKENS)

def _short_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16] if value else ""

def _normalize_fingerprint(value: str) -> str:
    clean = value.strip().lower()
    if re.fullmatch(r"[0-9a-f]{16,64}", clean):
        return clean[:16]
    return _short_fingerprint(clean) if clean else ""

def _secret_evidence(value: str) -> SecretEvidence:
    return SecretEvidence(bool(value), len(value), _short_fingerprint(value), has_placeholder(value) if value else False)

def _access_secret() -> str:
    for name in ["JWT_ACCESS_SECRET_CURRENT", "JWT_SECRET_CURRENT", "JWT_SECRET_KEY", "SECRET_KEY"]:
        if _env(name): return _env(name)
    return ""

def _refresh_secret() -> str:
    for name in ["JWT_REFRESH_SECRET_CURRENT", "JWT_REFRESH_SECRET_KEY", "REFRESH_SECRET_KEY"]:
        if _env(name): return _env(name)
    return ""

def _previous_access_fingerprint() -> str:
    return _normalize_fingerprint(_env("JWT_ACCESS_SECRET_PREVIOUS_FINGERPRINT")) or _short_fingerprint(_env("JWT_ACCESS_SECRET_PREVIOUS"))

def _previous_refresh_fingerprint() -> str:
    return _normalize_fingerprint(_env("JWT_REFRESH_SECRET_PREVIOUS_FINGERPRINT")) or _short_fingerprint(_env("JWT_REFRESH_SECRET_PREVIOUS"))

def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

def _b64d(value: str) -> bytes:
    return base64.urlsafe_b64decode((value + "=" * (-len(value) % 4)).encode("ascii"))

def issue_hs256_jwt(secret: str, *, token_use: str) -> str:
    now = datetime.now(timezone.utc)
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = {"sub": "jwt-evidence", "aud": "eduboost-v2", "iss": "eduboost-v2-release-gate", "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=5)).timestamp()), "token_use": token_use}
    signing_input = ".".join([_b64e(json.dumps(header, separators=(",", ":"), sort_keys=True).encode()), _b64e(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())])
    sig = hmac.new(secret.encode(), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64e(sig)}"

def verify_hs256_jwt(token: str, secret: str, *, expected_use: str) -> bool:
    try:
        hraw, praw, sraw = token.split(".")
        signing_input = f"{hraw}.{praw}"
        expected = hmac.new(secret.encode(), signing_input.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64d(sraw)): return False
        header, payload = json.loads(_b64d(hraw)), json.loads(_b64d(praw))
        return header.get("alg") == ALGORITHM and payload.get("token_use") == expected_use and int(payload.get("exp", 0)) > int(datetime.now(timezone.utc).timestamp())
    except Exception:
        return False

def _tamper(token: str) -> str:
    p = token.split(".")
    if len(p) != 3: return token + "x"
    p[2] = p[2][:-1] + ("A" if not p[2].endswith("A") else "B")
    return ".".join(p)

def run_token_self_test(access_secret: str, refresh_secret: str) -> TokenSelfTest:
    blockers: list[str] = []
    separated = bool(access_secret and refresh_secret and access_secret != refresh_secret)
    access_ok = refresh_ok = access_tamper = refresh_tamper = False
    try:
        at = issue_hs256_jwt(access_secret, token_use="access")
        rt = issue_hs256_jwt(refresh_secret, token_use="refresh")
        access_ok = verify_hs256_jwt(at, access_secret, expected_use="access")
        refresh_ok = verify_hs256_jwt(rt, refresh_secret, expected_use="refresh")
        access_tamper = not verify_hs256_jwt(_tamper(at), access_secret, expected_use="access")
        refresh_tamper = not verify_hs256_jwt(_tamper(rt), refresh_secret, expected_use="refresh")
    except Exception as exc:
        blockers.append(f"JWT self-test raised {type(exc).__name__}: {exc}")
    if not access_ok: blockers.append("access token issue/verify self-test failed")
    if not refresh_ok: blockers.append("refresh token issue/verify self-test failed")
    if not access_tamper: blockers.append("access token tamper rejection failed")
    if not refresh_tamper: blockers.append("refresh token tamper rejection failed")
    if not separated: blockers.append("access and refresh secrets must be different")
    return TokenSelfTest(access_ok, refresh_ok, access_tamper, refresh_tamper, separated, blockers)

def _gh_available() -> bool:
    return _run(["gh", "--version"]).returncode == 0

def _view_run(run_id: str) -> dict[str, Any] | None:
    r = _run(["gh", "run", "view", run_id, "--json", "databaseId,status,conclusion,headSha,url,workflowName,createdAt"])
    if r.returncode != 0: return None
    try: return json.loads(r.stdout)
    except Exception: return None

def collect_github_run_evidence(run_id: str, expected_sha: str) -> GitHubRunEvidence:
    blockers: list[str] = []
    if not run_id:
        return GitHubRunEvidence("", "", "", "", "", "", ["JWT_EVIDENCE_RUN_ID is required for accepted evidence"])
    if not re.fullmatch(r"[0-9]+", run_id): blockers.append("JWT_EVIDENCE_RUN_ID is not numeric")
    if not _gh_available(): blockers.append("GitHub CLI is unavailable or not authenticated")
    run = _view_run(run_id) if not blockers else None
    if run is None:
        blockers.append(f"unable to read GitHub Actions run {run_id}")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)
    url = str(run.get("url") or f"https://github.com/NkgoloL/Eduboost-V2/actions/runs/{run_id}").strip()
    workflow = str(run.get("workflowName") or "").strip()
    status = str(run.get("status") or "").strip()
    conclusion = str(run.get("conclusion") or "").strip()
    head_sha = str(run.get("headSha") or "").strip()
    if f"/actions/runs/{run_id}" not in url: blockers.append("run URL does not contain numeric run ID")
    if status != "completed": blockers.append(f"GitHub Actions run status is {status or 'missing'}, expected completed")
    if conclusion != "success": blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")
    if head_sha != expected_sha: blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {expected_sha}")
    if not workflow: blockers.append("workflow name is missing")
    return GitHubRunEvidence(run_id, url, workflow, status, conclusion, head_sha, blockers)

def write_status() -> JwtSecretRotationEvidenceStatus:
    blockers: list[str] = []
    sha, accept = current_commit(), _env("JWT_EVIDENCE_ACCEPT") == "1"
    evidence_env, store, ref, date, rotation_result = _env("JWT_EVIDENCE_ENV"), _env("JWT_SECRET_STORE"), _env("JWT_ROTATION_REFERENCE"), _env("JWT_ROTATION_DATE"), _env("JWT_ROTATION_RESULT")
    access_secret, refresh_secret = _access_secret(), _refresh_secret()
    access_current, refresh_current = _secret_evidence(access_secret), _secret_evidence(refresh_secret)
    prev_access, prev_refresh = _previous_access_fingerprint(), _previous_refresh_fingerprint()
    access_rotated = bool(prev_access and access_current.fingerprint and prev_access != access_current.fingerprint)
    refresh_rotated = bool(prev_refresh and refresh_current.fingerprint and prev_refresh != refresh_current.fingerprint)
    for label, ev in [("access", access_current), ("refresh", refresh_current)]:
        if not ev.present: blockers.append(f"current {label} JWT secret is missing")
        if ev.present and ev.length < MIN_SECRET_LENGTH: blockers.append(f"current {label} JWT secret length is {ev.length}, expected at least {MIN_SECRET_LENGTH}")
        if ev.placeholder_like: blockers.append(f"current {label} JWT secret looks placeholder-like")
    token_test = run_token_self_test(access_secret, refresh_secret) if access_secret and refresh_secret else TokenSelfTest(False, False, False, False, False, ["JWT token self-test skipped because current secrets are missing"])
    blockers.extend(token_test.blockers)
    if accept:
        if evidence_env not in {"staging", "production"}: blockers.append("JWT_EVIDENCE_ENV must be staging or production")
        if not store or has_placeholder(store): blockers.append("JWT_SECRET_STORE is missing or placeholder-like")
        if not ref or has_placeholder(ref): blockers.append("JWT_ROTATION_REFERENCE is missing or placeholder-like")
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date): blockers.append("JWT_ROTATION_DATE must be YYYY-MM-DD")
        if rotation_result != "passed": blockers.append("JWT_ROTATION_RESULT must be passed")
        if not prev_access: blockers.append("previous access JWT fingerprint/secret is required for rotation evidence")
        if not prev_refresh: blockers.append("previous refresh JWT fingerprint/secret is required for rotation evidence")
        if prev_access and not access_rotated: blockers.append("current access JWT fingerprint matches previous fingerprint; rotation not proven")
        if prev_refresh and not refresh_rotated: blockers.append("current refresh JWT fingerprint matches previous fingerprint; rotation not proven")
        gh = collect_github_run_evidence(_env("JWT_EVIDENCE_RUN_ID"), sha)
        blockers.extend(gh.blockers)
    else:
        gh = GitHubRunEvidence("", "", "", "", "", "", [])
    status = ACCEPTED_STATUS if accept and not blockers else NOT_ACCEPTED_STATUS
    result = JwtSecretRotationEvidenceStatus(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), sha, status, evidence_env, ALGORITHM, store, ref, date, rotation_result, access_current, refresh_current, prev_access, prev_refresh, access_rotated, refresh_rotated, token_test, gh, "github-actions" if status == ACCEPTED_STATUS else "unverified", datetime.now(timezone.utc).strftime("%Y-%m-%d"), blockers)
    STATUS_JSON.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    _write_markdown(result)
    return result

def _write_markdown(status: JwtSecretRotationEvidenceStatus) -> None:
    lines = [
        "# JWT Secret Rotation Evidence Status", "", f"Generated at: `{status.generated_at}`", f"Commit: `{status.current_commit}`", "",
        f"**Status:** `{status.status}`", f"**Environment:** `{status.evidence_environment}`", f"**Algorithm:** `{status.algorithm}`", f"**Secret store:** `{status.secret_store}`", f"**Rotation reference:** `{status.rotation_reference}`", f"**Rotation date:** `{status.rotation_date}`", f"**Rotation result:** `{status.rotation_result}`", f"**Run ID:** `{status.github_run.run_id}`", f"**Run URL:** `{status.github_run.run_url}`", f"**Workflow:** `{status.github_run.workflow_name}`", "",
        "## Redacted secret evidence", "", "| Secret | Present | Length | Fingerprint prefix | Placeholder-like |", "|---|---:|---:|---|---:|",
        f"| access current | {status.access_current.present} | {status.access_current.length} | `{status.access_current.fingerprint}` | {status.access_current.placeholder_like} |",
        f"| refresh current | {status.refresh_current.present} | {status.refresh_current.length} | `{status.refresh_current.fingerprint}` | {status.refresh_current.placeholder_like} |",
        f"| access previous | {bool(status.access_previous_fingerprint)} | n/a | `{status.access_previous_fingerprint}` | n/a |",
        f"| refresh previous | {bool(status.refresh_previous_fingerprint)} | n/a | `{status.refresh_previous_fingerprint}` | n/a |", "",
        "## Rotation proof", "", f"- Access secret rotated: `{status.access_rotated}`", f"- Refresh secret rotated: `{status.refresh_rotated}`", "",
        "## JWT self-test", "", f"- Access issue/verify: `{status.token_self_test.access_issue_verify}`", f"- Refresh issue/verify: `{status.token_self_test.refresh_issue_verify}`", f"- Access tamper rejected: `{status.token_self_test.access_tamper_rejected}`", f"- Refresh tamper rejected: `{status.token_self_test.refresh_tamper_rejected}`", f"- Access/refresh separated: `{status.token_self_test.access_refresh_separated}`", "", "## Blockers", "",
    ]
    lines.extend([f"- {b}" for b in status.blockers] if status.blockers else ["- None"])
    lines.extend(["", "## No false-closure rules", "", "- This proof closes JWT-001 only in JWT_EVIDENCE_ACCEPT=1 mode.", "- Raw JWT secrets are never written to release evidence.", "- Access and refresh secrets must be present, non-placeholder, at least 32 characters, and different.", "- Previous fingerprints or previous secret values are required to prove rotation.", "- Current fingerprints must differ from previous fingerprints.", "- JWT issue/verify/tamper-reject self-tests must pass.", "- A successful GitHub Actions run matching current commit is required.", "- This proof does not close ARQ, DIAG-SCORE, AUDIT-WRITE, DB-ROLLBACK, approvals, frontend runtime, image/SBOM, security scans, or beta release.", ""])
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    s = write_status()
    print(s.status)
    print(f"access_fingerprint={s.access_current.fingerprint}")
    print(f"refresh_fingerprint={s.refresh_current.fingerprint}")
    print(f"access_rotated={s.access_rotated}")
    print(f"refresh_rotated={s.refresh_rotated}")
    if s.blockers:
        for b in s.blockers: print(f"- {b}")
        raise SystemExit(1)
