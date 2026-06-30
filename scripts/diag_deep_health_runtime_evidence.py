from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/diag_deep_health_runtime_status.json"
OUT_MD = ROOT / "docs/release/diag_deep_health_runtime_status.md"
ACCEPTED_STATUS = "diag-deep-health-runtime-accepted"
NOT_ACCEPTED_STATUS = "diag-deep-health-runtime-not-accepted"
PLACEHOLDER_TOKENS = {"example.com", "localhost", "127.0.0.1", "0.0.0.0", "<", ">", "REAL_", "TODO", "TBD", "..."}
REQUIRED_COMPONENT_RESULTS = {
    "db": "DIAG_DEEP_HEALTH_DB_RESULT",
    "migration": "DIAG_DEEP_HEALTH_MIGRATION_RESULT",
    "audit": "DIAG_DEEP_HEALTH_AUDIT_RESULT",
    "session": "DIAG_DEEP_HEALTH_SESSION_RESULT",
}

@dataclass(frozen=True)
class HttpProbe:
    attempted: bool
    status_code: int | None
    body: str
    error: str

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
class DiagDeepHealthRuntimeStatus:
    generated_at: str
    current_commit: str
    current_branch: str
    status: str
    deep_health_url: str
    test_command: str
    http_status_code: int | None
    http_body_excerpt: str
    github_run: GitHubRunEvidence
    component_results: dict[str, str]
    inferred_component_signals: dict[str, str]
    verified_by: str
    date_verified: str
    blockers: list[str]

def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

def current_commit() -> str:
    result = _run(["git", "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"

def current_branch() -> str:
    result = _run(["git", "branch", "--show-current"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"

def _env(name: str) -> str:
    return os.getenv(name, "").strip()

def has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token.lower() in lowered for token in PLACEHOLDER_TOKENS)

def valid_https_url(value: str) -> bool:
    if not value or has_placeholder(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)

def is_deep_health_url(value: str) -> bool:
    parsed = urlparse(value)
    return "/health/deep" in parsed.path or parsed.path.rstrip("/").endswith("/deep")

def http_get(url: str, timeout_seconds: int = 20) -> HttpProbe:
    if not url:
        return HttpProbe(False, None, "", "URL missing")
    try:
        request = Request(url, headers={"User-Agent": "EduBoost-Deep-Health-Evidence/1.0"})
        with urlopen(request, timeout=timeout_seconds) as response:
            body = response.read(65536).decode("utf-8", errors="replace")
            return HttpProbe(True, int(getattr(response, "status", 0)), body, "")
    except HTTPError as exc:
        body = exc.read(65536).decode("utf-8", errors="replace")
        return HttpProbe(True, exc.code, body, f"http error {exc.code}")
    except URLError as exc:
        return HttpProbe(True, None, "", f"url error: {exc.reason}")
    except Exception as exc:  # pragma: no cover
        return HttpProbe(True, None, "", f"{type(exc).__name__}: {exc}")

def _parse_json(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return fallback

def _walk(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            items.extend(_walk(value, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            items.extend(_walk(value, f"{prefix}[{index}]"))
    else:
        items.append((prefix, obj))
    return items

def infer_component_signals(body: str) -> dict[str, str]:
    data = _parse_json(body, None)
    if data is None:
        return {}
    signals: dict[str, str] = {}
    groups = {
        "db": ("db", "database", "postgres", "postgresql"),
        "migration": ("migration", "migrations", "alembic"),
        "audit": ("audit", "audit_log", "auditlog"),
        "session": ("session", "diagnostic_session", "diagnostics_session"),
    }
    pass_values = {"ok", "pass", "passed", "healthy", "success", "true"}
    fail_values = {"fail", "failed", "unhealthy", "error", "false"}
    for path, value in _walk(data):
        p = path.lower()
        v = str(value).strip().lower()
        for component, keywords in groups.items():
            if any(keyword in p for keyword in keywords):
                if v in pass_values:
                    signals[component] = "passed"
                elif v in fail_values:
                    signals[component] = "failed"
                elif component not in signals:
                    signals[component] = v[:80]
    return signals

def _gh_available() -> bool:
    return _run(["gh", "--version"]).returncode == 0

def _view_run(run_id: str) -> dict[str, Any] | None:
    result = _run(["gh", "run", "view", run_id, "--json", "databaseId,status,conclusion,headSha,url,workflowName,createdAt"])
    if result.returncode != 0:
        return None
    data = _parse_json(result.stdout, None)
    return data if isinstance(data, dict) else None

def collect_github_run_evidence(run_id: str, expected_sha: str) -> GitHubRunEvidence:
    blockers: list[str] = []
    if not run_id:
        blockers.append("DIAG_DEEP_HEALTH_RUN_ID is required for accepted evidence")
        return GitHubRunEvidence("", "", "", "", "", "", blockers)
    if not re.fullmatch(r"[0-9]+", run_id):
        blockers.append("DIAG_DEEP_HEALTH_RUN_ID is not numeric")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)
    if not _gh_available():
        blockers.append("GitHub CLI is unavailable or not authenticated")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)
    run = _view_run(run_id)
    if run is None:
        blockers.append(f"unable to read GitHub Actions run {run_id}")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)
    run_url = str(run.get("url") or f"https://github.com/NkgoloL/Eduboost-V2/actions/runs/{run_id}").strip()
    workflow_name = str(run.get("workflowName") or "").strip()
    run_status = str(run.get("status") or "").strip()
    conclusion = str(run.get("conclusion") or "").strip()
    head_sha = str(run.get("headSha") or "").strip()
    if f"/actions/runs/{run_id}" not in run_url:
        blockers.append("run URL does not contain numeric run ID")
    if run_status != "completed":
        blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")
    if conclusion != "success":
        blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")
    if head_sha != expected_sha:
        blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {expected_sha}")
    if not workflow_name:
        blockers.append("workflow name is missing")
    if "auth refresh db proof" in workflow_name.lower():
        blockers.append("auth refresh DB proof workflow is not valid deep-health runtime evidence")
    return GitHubRunEvidence(run_id, run_url, workflow_name, run_status, conclusion, head_sha, blockers)

def collect_status(run_http: bool = True) -> DiagDeepHealthRuntimeStatus:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sha = current_commit()
    branch = current_branch()
    url = _env("DIAG_DEEP_HEALTH_URL") or _env("STAGING_DEEP_HEALTH_URL")
    test_command = _env("DIAG_DEEP_HEALTH_TEST_COMMAND")
    run_id = _env("DIAG_DEEP_HEALTH_RUN_ID")
    component_results = {component: _env(env_name) for component, env_name in REQUIRED_COMPONENT_RESULTS.items()}
    blockers: list[str] = []
    if not valid_https_url(url):
        blockers.append("deep health URL is missing, non-HTTPS, localhost/example, or placeholder")
    elif not is_deep_health_url(url):
        blockers.append("deep health URL must target /api/v2/health/deep or an equivalent /deep endpoint")
    if not test_command or has_placeholder(test_command):
        blockers.append("DIAG_DEEP_HEALTH_TEST_COMMAND is missing or placeholder")
    probe = http_get(url) if run_http and valid_https_url(url) else HttpProbe(False, None, "", "")
    if probe.attempted and probe.error:
        blockers.append(f"deep health HTTP probe error: {probe.error}")
    if probe.attempted and probe.status_code != 200:
        blockers.append(f"deep health HTTP status is {probe.status_code}, expected 200")
    if not probe.attempted:
        blockers.append("deep health HTTP probe was not attempted")
    inferred = infer_component_signals(probe.body)
    for component, result in component_results.items():
        if result != "passed":
            blockers.append(f"DIAG_DEEP_HEALTH_{component.upper()}_RESULT must be passed")
    github_run = collect_github_run_evidence(run_id, sha)
    blockers.extend(github_run.blockers)
    status = ACCEPTED_STATUS if not blockers else NOT_ACCEPTED_STATUS
    return DiagDeepHealthRuntimeStatus(
        generated_at, sha, branch, status, url, test_command, probe.status_code, probe.body[:4000],
        github_run, component_results, inferred, "github-actions" if status == ACCEPTED_STATUS else "unverified",
        datetime.now(timezone.utc).strftime("%Y-%m-%d"), blockers
    )

def write_status(run_http: bool = True) -> DiagDeepHealthRuntimeStatus:
    status = collect_status(run_http=run_http)
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# Diagnostic Deep Health Runtime Evidence Status", "",
        f"Generated at: `{status.generated_at}`", f"Commit: `{status.current_commit}`", f"Branch: `{status.current_branch}`", "",
        f"**Status:** `{status.status}`", f"**Deep health URL:** `{status.deep_health_url}`", f"**HTTP status:** `{status.http_status_code}`",
        f"**Run ID:** `{status.github_run.run_id}`", f"**Run URL:** `{status.github_run.run_url}`", f"**Workflow:** `{status.github_run.workflow_name}`",
        f"**Run status:** `{status.github_run.run_status}`", f"**Conclusion:** `{status.github_run.conclusion}`", f"**Head SHA:** `{status.github_run.head_sha}`",
        f"**Test command:** `{status.test_command}`", f"**Verified by:** `{status.verified_by}`", f"**Date verified:** `{status.date_verified}`", "",
        "## Required component results", "", "| Component | Result |", "|---|---|",
    ]
    for component, result in status.component_results.items():
        lines.append(f"| `{component}` | `{result}` |")
    lines.extend(["", "## Inferred response signals", "", "| Component | Signal |", "|---|---|"])
    if status.inferred_component_signals:
        for component, signal in status.inferred_component_signals.items():
            lines.append(f"| `{component}` | `{signal}` |")
    else:
        lines.append("| `-` | `none inferred` |")
    lines.extend(["", "## HTTP body excerpt", "", "```text", status.http_body_excerpt, "```", "", "## Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in status.blockers) if status.blockers else lines.append("- None")
    lines.extend([
        "", "## No false-closure rules", "",
        "- Lightweight staging smoke is not accepted as deep-health proof.",
        "- HTTP 503 remains a blocker and must not be classified as runtime-passing.",
        "- Required component results must explicitly be `passed`.",
        "- The GitHub Actions run must be successful and match the current commit.",
        "- This proof does not close JWT, ARQ, legal/security/content approvals, lesson auth, diagnostic scoring, or beta release.", "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status

if __name__ == "__main__":
    result = write_status(run_http=True)
    print(result.status)
    if result.blockers:
        for blocker in result.blockers:
            print(f"- {blocker}")
        raise SystemExit(1)
