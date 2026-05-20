from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker-compose.prod.yml"
DOCKERFILE = ROOT / "docker/Dockerfile.frontend"
NGINX_CONF = ROOT / "nginx/nginx.conf"
FRONTEND_DIR = ROOT / "app/frontend"
EVIDENCE_MD = ROOT / "docs/release/production_frontend_runtime_evidence.md"
STATUS_JSON = ROOT / "docs/release/production_frontend_runtime_status.json"
STATUS_MD = ROOT / "docs/release/production_frontend_runtime_status.md"

NEXT_CONFIG_CANDIDATES = [
    FRONTEND_DIR / "next.config.js",
    FRONTEND_DIR / "next.config.mjs",
    FRONTEND_DIR / "next.config.ts",
]

REQUIRED_EVIDENCE_FIELDS = [
    "Docker compose config result",
    "Frontend image build result",
    "Runtime container result",
    "Nginx proxy smoke result",
    "Browser smoke result",
    "Evidence URL",
    "Commit SHA",
    "Verified by",
    "Date verified",
]

PASS_VALUES = {"pass", "passed", "green", "ok", "success", "successful"}
PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}


@dataclass(frozen=True)
class RuntimeCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ComposeConfigResult:
    status: str
    return_code: int | None
    detail: str


@dataclass(frozen=True)
class RuntimeEvidenceField:
    name: str
    value: str
    valid: bool
    reason: str


@dataclass(frozen=True)
class ProductionFrontendRuntimeStatus:
    generated_at: str
    current_commit: str
    status: str
    compose_config: ComposeConfigResult
    checks: list[RuntimeCheck]
    evidence_fields: list[RuntimeEvidenceField]
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def _next_config_path() -> Path | None:
    for path in NEXT_CONFIG_CANDIDATES:
        if path.exists():
            return path
    return None


def _next_config_text() -> str:
    path = _next_config_path()
    return _read(path) if path else ""


def dockerfile_has_production_stage(text: str) -> bool:
    return bool(re.search(r"(?im)^\s*FROM\s+.+\s+AS\s+production\s*$", text))


def dockerfile_has_standalone_copy(text: str) -> bool:
    return ".next/standalone" in text or "standalone" in text


def dockerfile_uses_next_port(text: str) -> bool:
    return "3050" in text and ("EXPOSE 3050" in text or "PORT=3050" in text or "ENV PORT 3050" in text)


def next_config_has_standalone_output(text: str) -> bool:
    return bool(re.search(r"output\s*:\s*['\"]standalone['\"]", text))


def nginx_proxies_to_frontend(text: str) -> bool:
    return "frontend:3050" in text


def nginx_cert_paths_use_letsencrypt(text: str) -> bool:
    return "/etc/letsencrypt/live" in text or "/etc/letsencrypt" in text


def compose_has_frontend_service(text: str) -> bool:
    return bool(re.search(r"(?m)^  frontend:\s*$", text))


def compose_targets_frontend_production(text: str) -> bool:
    if not compose_has_frontend_service(text):
        return False
    start = text.find("  frontend:")
    tail = text[start + 1 :]
    next_service = re.search(r"(?m)^  [a-zA-Z0-9_-]+:\s*$", tail)
    block = text[start:] if not next_service else text[start : start + 1 + next_service.start()]
    return "target: production" in block and "docker/Dockerfile.frontend" in block and "3050" in block


def compose_nginx_depends_on_frontend(text: str) -> bool:
    nginx_match = re.search(r"(?ms)^  nginx:\n(?P<body>.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)", text)
    if not nginx_match:
        return False
    body = nginx_match.group("body")
    return "depends_on:" in body and "- frontend" in body


def compose_cert_mount_uses_letsencrypt(text: str) -> bool:
    return "./nginx/ssl:/etc/letsencrypt" in text


def _docker_compose_cmd() -> list[str] | None:
    docker = shutil.which("docker")
    if not docker:
        return None

    plugin = subprocess.run(
        [docker, "compose", "version"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=20,
    )
    if plugin.returncode == 0:
        return [docker, "compose"]

    legacy = shutil.which("docker-compose")
    if legacy:
        return [legacy]
    return None


def run_compose_config() -> ComposeConfigResult:
    cmd = _docker_compose_cmd()
    if cmd is None:
        return ComposeConfigResult(
            status="tool-unavailable",
            return_code=None,
            detail="docker compose is not available in this environment",
        )

    try:
        result = subprocess.run(
            [*cmd, "-f", "docker-compose.prod.yml", "config"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return ComposeConfigResult(
            status="failed",
            return_code=None,
            detail="docker compose config timed out",
        )

    if result.returncode == 0:
        return ComposeConfigResult(
            status="passed",
            return_code=0,
            detail="docker compose -f docker-compose.prod.yml config succeeded",
        )
    return ComposeConfigResult(
        status="failed",
        return_code=result.returncode,
        detail=result.stdout[-1000:] if result.stdout else "docker compose config failed",
    )


def runtime_evidence_template() -> str:
    return "\n".join(
        [
            "# Production Frontend Runtime Evidence",
            "",
            "**Item:** DEPLOY-FE-RUNTIME-001",
            "",
            "**Docker compose config result:** pending",
            "",
            "**Frontend image build result:** pending",
            "",
            "**Runtime container result:** pending",
            "",
            "**Nginx proxy smoke result:** pending",
            "",
            "**Browser smoke result:** pending",
            "",
            "**Evidence URL:** pending",
            "",
            "**Commit SHA:** pending",
            "",
            "**Verified by:** pending",
            "",
            "**Date verified:** pending",
            "",
            "## Required proof",
            "",
            "- `docker compose -f docker-compose.prod.yml config` succeeds.",
            "- Frontend production image builds successfully.",
            "- Frontend container starts and serves port `3050`.",
            "- Nginx can proxy to `frontend:3050`.",
            "- Browser smoke/E2E validates the deployed frontend route.",
            "",
            "## No false-closure rule",
            "",
            "This file is not runtime proof while any required field remains pending or while any result field is not `passed`.",
            "",
        ]
    )


def write_runtime_evidence_template() -> None:
    if EVIDENCE_MD.exists() and "**Item:** DEPLOY-FE-RUNTIME-001" in EVIDENCE_MD.read_text(encoding="utf-8"):
        return
    EVIDENCE_MD.write_text(runtime_evidence_template(), encoding="utf-8")


def _is_pending(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _field(text: str, name: str) -> str:
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip().strip("`").strip() if match else ""


def _is_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def _looks_like_sha(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{7,40}", value.strip()))


def runtime_evidence_fields() -> list[RuntimeEvidenceField]:
    write_runtime_evidence_template()
    text = EVIDENCE_MD.read_text(encoding="utf-8")
    fields: list[RuntimeEvidenceField] = []
    for name in REQUIRED_EVIDENCE_FIELDS:
        value = _field(text, name)
        if _is_pending(value):
            fields.append(RuntimeEvidenceField(name, value, False, "pending"))
            continue

        if name in {
            "Docker compose config result",
            "Frontend image build result",
            "Runtime container result",
            "Nginx proxy smoke result",
            "Browser smoke result",
        } and value.strip().lower() not in PASS_VALUES:
            fields.append(RuntimeEvidenceField(name, value, False, "must be pass/passed/green/ok/success"))
            continue

        if name == "Evidence URL" and not _is_url(value):
            fields.append(RuntimeEvidenceField(name, value, False, "must be URL"))
            continue

        if name == "Commit SHA" and not _looks_like_sha(value):
            fields.append(RuntimeEvidenceField(name, value, False, "must look like git SHA"))
            continue

        fields.append(RuntimeEvidenceField(name, value, True, "ok"))

    return fields


def build_checks() -> list[RuntimeCheck]:
    compose = _read(COMPOSE)
    dockerfile = _read(DOCKERFILE)
    nginx = _read(NGINX_CONF)
    next_config = _next_config_text()
    next_config_path = _next_config_path()

    return [
        RuntimeCheck("docker-compose.prod.yml exists", COMPOSE.exists(), str(COMPOSE.relative_to(ROOT))),
        RuntimeCheck("Dockerfile.frontend exists", DOCKERFILE.exists(), str(DOCKERFILE.relative_to(ROOT))),
        RuntimeCheck("frontend service exists in production compose", compose_has_frontend_service(compose), "frontend service"),
        RuntimeCheck("frontend compose target is production", compose_targets_frontend_production(compose), "target production + port 3050"),
        RuntimeCheck("nginx depends on frontend", compose_nginx_depends_on_frontend(compose), "depends_on frontend"),
        RuntimeCheck("compose cert mount uses /etc/letsencrypt", compose_cert_mount_uses_letsencrypt(compose), "shared certbot/nginx cert path"),
        RuntimeCheck("Dockerfile has production stage", dockerfile_has_production_stage(dockerfile), "FROM ... AS production"),
        RuntimeCheck("Dockerfile contains standalone runtime copy", dockerfile_has_standalone_copy(dockerfile), ".next/standalone"),
        RuntimeCheck("Dockerfile uses port 3050", dockerfile_uses_next_port(dockerfile), "EXPOSE/PORT 3050"),
        RuntimeCheck(
            "Next config exists",
            next_config_path is not None,
            next_config_path.relative_to(ROOT).as_posix() if next_config_path else "missing",
        ),
        RuntimeCheck("Next config output standalone", next_config_has_standalone_output(next_config), "output: 'standalone'"),
        RuntimeCheck("nginx proxies to frontend:3050", nginx_proxies_to_frontend(nginx), "proxy_pass frontend:3050"),
        RuntimeCheck("nginx cert paths use /etc/letsencrypt", nginx_cert_paths_use_letsencrypt(nginx), "ssl_certificate path"),
    ]


def build_status() -> ProductionFrontendRuntimeStatus:
    write_runtime_evidence_template()
    checks = build_checks()
    compose_result = run_compose_config()
    evidence = runtime_evidence_fields()

    blockers = [check.name for check in checks if not check.passed]
    if compose_result.status == "failed":
        blockers.append("docker compose config failed")
    runtime_evidence_blockers = [
        f"runtime evidence: {field.name} {field.reason}"
        for field in evidence
        if not field.valid
    ]

    if not blockers and compose_result.status in {"passed", "tool-unavailable"}:
        local_status = (
            "runtime-preflight-passing"
            if compose_result.status == "passed"
            else "runtime-preflight-static-passing-compose-tool-unavailable"
        )
    else:
        local_status = "runtime-preflight-not-proven"

    status = "runtime-evidence-accepted" if local_status == "runtime-preflight-passing" and not runtime_evidence_blockers else local_status

    return ProductionFrontendRuntimeStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status=status,
        compose_config=compose_result,
        checks=checks,
        evidence_fields=evidence,
        blockers=blockers + runtime_evidence_blockers,
        no_false_closure_rules=[
            "Static Docker/compose checks do not prove a live deployment.",
            "docker compose config does not prove image build success.",
            "runtime evidence is required before release-mode deployment proof can pass.",
            "staging smoke and browser evidence remain separate beta blockers.",
        ],
    )


def write_status() -> ProductionFrontendRuntimeStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Production Frontend Runtime Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "## Compose config preflight",
        "",
        f"- Status: `{status.compose_config.status}`",
        f"- Return code: `{status.compose_config.return_code}`",
        f"- Detail: `{status.compose_config.detail}`",
        "",
        "## Local runtime-preflight checks",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in status.checks:
        lines.append(f"| `{check.name}` | {check.passed} | {check.detail} |")

    lines.extend(["", "## Runtime evidence fields", "", "| Field | Value | Valid | Reason |", "|---|---|---:|---|"])
    for field in status.evidence_fields:
        lines.append(f"| `{field.name}` | `{field.value}` | {field.valid} | {field.reason} |")

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in status.no_false_closure_rules)

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This status validates runtime-preflight configuration and records runtime evidence state. It does not deploy the frontend.",
            "",
        ]
    )
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


def _insert_standalone_output(source: str) -> str:
    if next_config_has_standalone_output(source):
        return source

    replacements = [
        ("const nextConfig = {", "const nextConfig = {\n  output: 'standalone',"),
        ("const config = {", "const config = {\n  output: 'standalone',"),
        ("module.exports = {", "module.exports = {\n  output: 'standalone',"),
        ("export default {", "export default {\n  output: 'standalone',"),
    ]
    for old, new in replacements:
        if old in source:
            return source.replace(old, new, 1)

    return source.rstrip() + "\n\n// Added by DEPLOY-FE-RUNTIME-001\nexport default {\n  output: 'standalone',\n};\n"


def repair_next_config() -> bool:
    path = _next_config_path()
    if path is None:
        path = FRONTEND_DIR / "next.config.js"
        path.write_text("const nextConfig = {\n  output: 'standalone',\n};\n\nmodule.exports = nextConfig;\n", encoding="utf-8")
        return True

    source = path.read_text(encoding="utf-8")
    new_source = _insert_standalone_output(source)
    if new_source != source:
        path.write_text(new_source, encoding="utf-8")
        return True
    return False


def repair() -> ProductionFrontendRuntimeStatus:
    repair_next_config()
    return write_status()


__all__ = [
    "ProductionFrontendRuntimeStatus",
    "build_status",
    "compose_has_frontend_service",
    "compose_targets_frontend_production",
    "dockerfile_has_production_stage",
    "dockerfile_has_standalone_copy",
    "dockerfile_uses_next_port",
    "next_config_has_standalone_output",
    "nginx_cert_paths_use_letsencrypt",
    "nginx_proxies_to_frontend",
    "repair",
    "runtime_evidence_fields",
    "run_compose_config",
    "write_status",
]
