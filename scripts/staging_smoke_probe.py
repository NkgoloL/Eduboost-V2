from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


PLACEHOLDER_TOKENS = (
    "example.com",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "<",
    ">",
    "REAL_",
    "TODO",
    "TBD",
    "...",
)


@dataclass(frozen=True)
class ProbeResult:
    name: str
    url: str
    status_code: int | None
    passed: bool
    detail: str


@dataclass(frozen=True)
class StagingSmokeProbeReport:
    generated_at: str
    base_url: str
    health_path: str
    api_path: str
    frontend_path: str
    healthcheck_result: str
    api_result: str
    frontend_result: str
    smoke_result: str
    probes: list[ProbeResult]
    blockers: list[str]


def has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token.lower() in lowered for token in PLACEHOLDER_TOKENS)


def valid_https_url(value: str) -> bool:
    if not value or has_placeholder(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def normalize_path(path: str) -> str:
    path = (path or "").strip()
    if not path:
        return ""
    return path if path.startswith("/") else f"/{path}"


def build_url(base_url: str, path: str) -> str:
    return urljoin(base_url.rstrip("/") + "/", normalize_path(path).lstrip("/"))


def smoke_get(name: str, url: str, timeout_seconds: int = 15) -> ProbeResult:
    try:
        request = Request(url, headers={"User-Agent": "EduBoost-Staging-Smoke/1.0"})
        with urlopen(request, timeout=timeout_seconds) as response:
            status_code = int(getattr(response, "status", 0))
            passed = 200 <= status_code < 400
            return ProbeResult(
                name=name,
                url=url,
                status_code=status_code,
                passed=passed,
                detail="ok" if passed else f"unexpected status {status_code}",
            )
    except HTTPError as exc:
        return ProbeResult(
            name=name,
            url=url,
            status_code=exc.code,
            passed=False,
            detail=f"http error {exc.code}",
        )
    except URLError as exc:
        return ProbeResult(
            name=name,
            url=url,
            status_code=None,
            passed=False,
            detail=f"url error: {exc.reason}",
        )
    except Exception as exc:  # pragma: no cover - defensive CI diagnostics
        return ProbeResult(
            name=name,
            url=url,
            status_code=None,
            passed=False,
            detail=f"{type(exc).__name__}: {exc}",
        )


def result_label(passed: bool) -> str:
    return "passed" if passed else "failed"


def build_report(
    base_url: str,
    health_path: str,
    api_path: str,
    frontend_path: str,
    *,
    run_network: bool = True,
) -> StagingSmokeProbeReport:
    blockers: list[str] = []
    probes: list[ProbeResult] = []

    if not valid_https_url(base_url):
        blockers.append("staging base URL must be real, HTTPS, and non-placeholder")

    health_path = normalize_path(health_path or "/health")
    api_path = normalize_path(api_path or "/api/v2/health")
    frontend_path = normalize_path(frontend_path)

    if not blockers and run_network:
        probes.append(smoke_get("healthcheck", build_url(base_url, health_path)))
        probes.append(smoke_get("api", build_url(base_url, api_path)))
        if frontend_path:
            probes.append(smoke_get("frontend", build_url(base_url, frontend_path)))

    for probe in probes:
        if not probe.passed:
            blockers.append(f"{probe.name} probe failed: {probe.detail}")

    by_name = {probe.name: probe for probe in probes}
    health_passed = by_name.get("healthcheck").passed if "healthcheck" in by_name else False
    api_passed = by_name.get("api").passed if "api" in by_name else False
    frontend_recorded = "frontend" in by_name
    frontend_passed = by_name["frontend"].passed if frontend_recorded else None

    healthcheck_result = result_label(health_passed)
    api_result = result_label(api_passed)
    frontend_result = result_label(frontend_passed) if frontend_passed is not None else "not-recorded"
    smoke_result = "passed" if not blockers and health_passed and api_passed else "failed"

    return StagingSmokeProbeReport(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        base_url=base_url,
        health_path=health_path,
        api_path=api_path,
        frontend_path=frontend_path,
        healthcheck_result=healthcheck_result,
        api_result=api_result,
        frontend_result=frontend_result,
        smoke_result=smoke_result,
        probes=probes,
        blockers=blockers,
    )


def write_report(report: StagingSmokeProbeReport, json_path: Path, md_path: Path) -> None:
    json_path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    lines = [
        "# Staging Smoke Probe Result",
        "",
        f"Generated at: `{report.generated_at}`",
        f"Base URL: `{report.base_url}`",
        f"Health path: `{report.health_path}`",
        f"API path: `{report.api_path}`",
        f"Frontend path: `{report.frontend_path}`",
        "",
        f"STAGING_SMOKE_RESULT=`{report.smoke_result}`",
        f"STAGING_SMOKE_HEALTHCHECK_RESULT=`{report.healthcheck_result}`",
        f"STAGING_SMOKE_API_RESULT=`{report.api_result}`",
        f"STAGING_SMOKE_FRONTEND_RESULT=`{report.frontend_result}`",
        "",
        "## Probes",
        "",
        "| Name | URL | Status | Passed | Detail |",
        "|---|---|---:|---:|---|",
    ]

    for probe in report.probes:
        lines.append(
            f"| `{probe.name}` | `{probe.url}` | {probe.status_code} | {probe.passed} | {probe.detail} |"
        )

    lines.extend(["", "## Blockers", ""])
    if report.blockers:
        lines.extend(f"- {blocker}" for blocker in report.blockers)
    else:
        lines.append("- None")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    base_url = os.getenv("STAGING_SMOKE_BASE_URL", "").strip()
    health_path = os.getenv("STAGING_SMOKE_HEALTH_PATH", "/health")
    api_path = os.getenv("STAGING_SMOKE_API_PATH", "/api/v2/health")
    frontend_path = os.getenv("STAGING_SMOKE_FRONTEND_PATH", "/")
    output_json = Path(os.getenv("STAGING_SMOKE_OUTPUT_JSON", "staging_smoke_probe_result.json"))
    output_md = Path(os.getenv("STAGING_SMOKE_OUTPUT_MD", "staging_smoke_probe_result.md"))

    report = build_report(
        base_url=base_url,
        health_path=health_path,
        api_path=api_path,
        frontend_path=frontend_path,
        run_network=True,
    )
    write_report(report, output_json, output_md)

    print(f"STAGING_SMOKE_RESULT={report.smoke_result}")
    print(f"STAGING_SMOKE_HEALTHCHECK_RESULT={report.healthcheck_result}")
    print(f"STAGING_SMOKE_API_RESULT={report.api_result}")
    print(f"STAGING_SMOKE_FRONTEND_RESULT={report.frontend_result}")

    if report.blockers:
        for blocker in report.blockers:
            print(f"- {blocker}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
