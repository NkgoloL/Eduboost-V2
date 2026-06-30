from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app/api_v2_routers/popia.py"
ADAPTER = ROOT / "app/services/popia_consent_lifecycle_adapter.py"
OUT_JSON = ROOT / "docs/release/popia_response_contract_no_skip_status.json"
OUT_MD = ROOT / "docs/release/popia_response_contract_no_skip_status.md"

REQUIRED_ROUTES = {
    "grant": "/consent/grant",
    "deny": "/consent/deny",
    "withdraw": "/consent/withdraw",
    "renew": "/consent/renew",
}


@dataclass(frozen=True)
class RouteContract:
    name: str
    path: str
    exists: bool
    response_model_is_consent_record: bool
    passed: bool


@dataclass(frozen=True)
class Status:
    generated_at: str
    current_commit: str
    status: str
    route_contracts: list[RouteContract]
    adapter_contracts: dict[str, bool]
    pytest_return_code: int | None
    pytest_output: str
    skipped_detected: bool
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _string_value(node: ast.AST) -> str:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else ""


def _kw_name_value(call: ast.Call, key: str) -> str:
    for keyword in call.keywords:
        if keyword.arg == key:
            return _call_name(keyword.value)
    return ""


def route_contracts() -> list[RouteContract]:
    if not ROUTER.exists():
        return [
            RouteContract(name=name, path=path, exists=False, response_model_is_consent_record=False, passed=False)
            for name, path in REQUIRED_ROUTES.items()
        ]

    tree = ast.parse(read(ROUTER))
    contracts: list[RouteContract] = []

    for name, path in REQUIRED_ROUTES.items():
        exists = False
        response_ok = False

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                if _call_name(decorator.func) != "router.post":
                    continue
                dec_path = _string_value(decorator.args[0]) if decorator.args else ""
                if dec_path != path:
                    continue

                exists = True
                response_ok = _kw_name_value(decorator, "response_model") == "ConsentRecord"

        contracts.append(
            RouteContract(
                name=name,
                path=path,
                exists=exists,
                response_model_is_consent_record=response_ok,
                passed=exists and response_ok,
            )
        )

    return contracts


def adapter_contracts() -> dict[str, bool]:
    source = read(ADAPTER)
    return {
        "adapter_exists": ADAPTER.exists(),
        "contains_consent_record": "ConsentRecord" in source,
        "contains_coerce_consent_record": "_coerce_consent_record" in source,
        "contains_denied_fallback": "ConsentState.DENIED" in source,
        "contains_withdrawn_fallback": "ConsentState.WITHDRAWN" in source,
    }


def has_skip(output: str) -> bool:
    lowered = output.lower()
    return bool(
        re.search(r"\b\d+\s+skipped\b", lowered)
        or re.search(r"\bskipped\b", lowered)
        or re.search(r"(^|\s)s+\s+\[", lowered)
        or re.search(r"\s+s+\s*$", lowered)
    )


def run_pytest() -> tuple[int, str, bool]:
    env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
    venv_py = str((ROOT / ".venv" / "bin" / "python")) if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
    result = subprocess.run(
        [
            venv_py,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_popia_lifecycle_response_no_skip_proof.py",
            "-q",
            "--no-cov",
            "--tb=short",
            "-rs",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        check=False,
    )
    return result.returncode, result.stdout, has_skip(result.stdout)


def build_status(run_tests: bool = True) -> Status:
    routes = route_contracts()
    adapter = adapter_contracts()

    pytest_return_code: int | None = None
    pytest_output = "pytest not requested"
    skipped = False

    if run_tests:
        pytest_return_code, pytest_output, skipped = run_pytest()

    blockers: list[str] = []

    for route in routes:
        if not route.passed:
            blockers.append(f"{route.name} route missing response_model=ConsentRecord for {route.path}")

    for name, passed in adapter.items():
        if not passed:
            blockers.append(f"adapter contract missing: {name}")

    if run_tests and pytest_return_code != 0:
        blockers.append("POPIA no-skip response-contract pytest failed")

    if skipped:
        blockers.append("pytest output contains skipped tests; skipped tests are not proof")

    return Status(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="popia-response-contract-no-skip-passing" if not blockers else "popia-response-contract-no-skip-not-proven",
        route_contracts=routes,
        adapter_contracts=adapter,
        pytest_return_code=pytest_return_code,
        pytest_output=pytest_output[-4000:],
        skipped_detected=skipped,
        blockers=blockers,
    )


def write_status(run_tests: bool = True) -> Status:
    status = build_status(run_tests=run_tests)
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# POPIA Response Contract No-Skip Proof Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**Pytest return code:** `{status.pytest_return_code}`",
        f"**Skipped detected:** `{status.skipped_detected}`",
        "",
        "## Route contracts",
        "",
        "| Contract | Path | Route exists | ConsentRecord response_model | Passed |",
        "|---|---|---:|---:|---:|",
    ]
    for route in status.route_contracts:
        lines.append(
            f"| `{route.name}` | `{route.path}` | {route.exists} | "
            f"{route.response_model_is_consent_record} | {route.passed} |"
        )

    lines.extend(["", "## Adapter contracts", "", "| Contract | Passed |", "|---|---:|"])
    for name, passed in status.adapter_contracts.items():
        lines.append(f"| `{name}` | {passed} |")

    lines.extend(["", "## Pytest output", "", "```text", status.pytest_output, "```", "", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- Skipped tests are not accepted as proof.",
            "- This response-contract proof does not prove live DB transaction behavior.",
            "- This proof does not satisfy external POPIA legal approval.",
            "- This proof does not approve beta release.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
