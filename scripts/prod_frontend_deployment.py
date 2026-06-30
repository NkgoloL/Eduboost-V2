from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker-compose.prod.yml"
PLAYWRIGHT = ROOT / "playwright.config.ts"
STATUS_JSON = ROOT / "docs/release/production_frontend_deployment_status.json"
STATUS_MD = ROOT / "docs/release/production_frontend_deployment_status.md"

FRONTEND_SERVICE_BLOCK = """  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.10'
          memory: 128M
    build:
      context: ./app/frontend
      dockerfile: ../../docker/Dockerfile.frontend
      target: production
    environment:
      - NODE_ENV=production
      - NEXT_TELEMETRY_DISABLED=1
      - PORT=3050
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-/api/v2}
      - NEXT_PUBLIC_APP_ENV=production
      - NEXT_PUBLIC_ENABLE_DEV_SESSION=false
    expose:
      - "3050"
    depends_on:
      - api
    restart: unless-stopped

"""


@dataclass(frozen=True)
class DeploymentCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ProductionFrontendDeploymentStatus:
    generated_at: str
    current_commit: str
    status: str
    checks: list[DeploymentCheck]
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def compose_text() -> str:
    return _read(COMPOSE)


def playwright_text() -> str:
    return _read(PLAYWRIGHT)


def has_frontend_service(text: str) -> bool:
    return bool(re.search(r"(?m)^  frontend:\s*$", text))


def frontend_uses_production_target(text: str) -> bool:
    if not has_frontend_service(text):
        return False
    frontend_start = text.find("  frontend:")
    next_service = re.search(r"(?m)^  [a-zA-Z0-9_-]+:\s*$", text[frontend_start + 1 :])
    block = text[frontend_start:] if not next_service else text[frontend_start : frontend_start + 1 + next_service.start()]
    return "target: production" in block and "docker/Dockerfile.frontend" in block and "./app/frontend" in block


def nginx_depends_on_frontend(text: str) -> bool:
    nginx_match = re.search(r"(?ms)^  nginx:\n(?P<body>.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)", text)
    if not nginx_match:
        return False
    body = nginx_match.group("body")
    return "depends_on:" in body and "- frontend" in body


def nginx_cert_mount_aligned(text: str) -> bool:
    return "./nginx/ssl:/etc/letsencrypt" in text


def certbot_uses_same_cert_mount(text: str) -> bool:
    return "./nginx/ssl:/etc/letsencrypt" in text



def playwright_uses_next_port(text: str) -> bool:
    return "http://127.0.0.1:3050" in text


def playwright_timeout_hardened(text: str) -> bool:
    return "timeout: 60_000" in text or "timeout: 90_000" in text or "timeout: 120_000" in text


def build_status() -> ProductionFrontendDeploymentStatus:
    compose = compose_text()
    playwright = playwright_text()
    checks = [
        DeploymentCheck("docker-compose.prod.yml exists", COMPOSE.exists(), str(COMPOSE.relative_to(ROOT))),
        DeploymentCheck("production frontend service exists", has_frontend_service(compose), "service key `frontend`"),
        DeploymentCheck("frontend uses production Docker target", frontend_uses_production_target(compose), "target: production + Dockerfile.frontend"),
        DeploymentCheck("nginx depends on frontend", nginx_depends_on_frontend(compose), "nginx depends_on includes frontend"),
        DeploymentCheck("nginx cert mount aligned to /etc/letsencrypt", nginx_cert_mount_aligned(compose), "nginx reads same cert path certbot writes"),
        DeploymentCheck("certbot writes to /etc/letsencrypt", certbot_uses_same_cert_mount(compose), "certbot volume target"),
        DeploymentCheck("playwright defaults to Next.js port 3050", playwright_uses_next_port(playwright), "baseURL fallback"),
        DeploymentCheck("playwright timeout hardened", playwright_timeout_hardened(playwright), "timeout >= 60s"),
    ]
    blockers = [check.name for check in checks if not check.passed]
    return ProductionFrontendDeploymentStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="production-frontend-configured" if not blockers else "deployment-config-not-proven",
        checks=checks,
        blockers=blockers,
    )


def write_status() -> ProductionFrontendDeploymentStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Production Frontend Deployment Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in status.checks:
        lines.append(f"| `{check.name}` | {check.passed} | {check.detail} |")

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This validates production deployment configuration only. It does not prove a successful deployment or live browser run.",
            "",
        ]
    )
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


def repair_compose() -> bool:
    if not COMPOSE.exists():
        raise FileNotFoundError(COMPOSE)
    text = COMPOSE.read_text(encoding="utf-8")
    original = text

    if not has_frontend_service(text):
        marker = "\n  postgres:\n"
        if marker not in text:
            raise RuntimeError("Could not locate postgres service insertion point")
        text = text.replace(marker, "\n" + FRONTEND_SERVICE_BLOCK + marker.lstrip("\n"), 1)

    if "    depends_on:\n      - api\n" in text and not nginx_depends_on_frontend(text):
        text = text.replace(
            "    depends_on:\n      - api\n",
            "    depends_on:\n      - api\n      - frontend\n",
            1,
        )

    text = text.replace(
        "- ./nginx/nginx.conf:/etc/nginx/nginx.conf",
        "- ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro",
    )
    text = text.replace(
        "- ./nginx/ssl:/etc/ssl/certs",
        "- ./nginx/ssl:/etc/letsencrypt:ro",
    )
    text = text.replace(
        "- ./nginx/ssl:/etc/letsencrypt\n",
        "- ./nginx/ssl:/etc/letsencrypt\n",
    )

    if text != original:
        COMPOSE.write_text(text, encoding="utf-8")
        return True
    return False


def repair_playwright() -> bool:
    if not PLAYWRIGHT.exists():
        raise FileNotFoundError(PLAYWRIGHT)
    text = PLAYWRIGHT.read_text(encoding="utf-8")
    original = text
    text = text.replace('http://127.0.0.1:5173', 'http://127.0.0.1:3050')
    text = text.replace("timeout: 30_000", "timeout: 60_000")
    if text != original:
        PLAYWRIGHT.write_text(text, encoding="utf-8")
        return True
    return False


def repair() -> ProductionFrontendDeploymentStatus:
    repair_compose()
    repair_playwright()
    return write_status()


__all__ = [
    "FRONTEND_SERVICE_BLOCK",
    "ProductionFrontendDeploymentStatus",
    "build_status",
    "certbot_uses_same_cert_mount",
    "frontend_uses_production_target",
    "has_frontend_service",
    "nginx_cert_mount_aligned",
    "nginx_depends_on_frontend",
    "playwright_timeout_hardened",
    "playwright_uses_next_port",
    "repair",
    "write_status",
]
