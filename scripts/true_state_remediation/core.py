from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
from scripts._subprocess import run
from subprocess import TimeoutExpired
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

FALSE_BOUNDARY_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
)

class BundleError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def root_from(start: Path | str | None = None) -> Path:
    candidate = Path(start or Path.cwd()).resolve()
    for current in (candidate, *candidate.parents):
        if all((current / p).exists() for p in ("app", "docs", "scripts", "pyproject.toml")):
            return current
    raise BundleError(f"Could not locate EduBoost repository root from {candidate}")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temp = Path(handle.name)
    os.replace(temp, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def command_version(command: list[str]) -> dict[str, Any]:
    try:
        proc = run(command, text=True, capture_output=True, timeout=20, check=False)
        output = (proc.stdout or proc.stderr).strip().splitlines()
        return {"available": proc.returncode == 0, "exit_code": proc.returncode, "version": output[0] if output else ""}
    except (OSError, TimeoutExpired) as exc:
        return {"available": False, "error": str(exc)}


def git_state(root: Path) -> dict[str, Any]:
    if not (root / ".git").exists():
        return {"available": False, "reason": ".git metadata absent"}
    def _run_git(*args: str) -> str:
        proc = run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
        return proc.stdout.strip() if proc.returncode == 0 else ""
    status = _run_git("status", "--porcelain")
    return {
        "available": True,
        "commit": _run_git("rev-parse", "HEAD"),
        "branch": _run_git("branch", "--show-current"),
        "status_porcelain": status,
        "clean": not bool(status),
        "submodules": _run_git("submodule", "status"),
    }


def environment_manifest(root: Path) -> dict[str, Any]:
    files = [
        "requirements/base.txt", "requirements/dev.txt", "requirements/docs.txt", "requirements/ml.txt",
        "pnpm-lock.yaml", "package.json", "app/frontend/package.json", "pyproject.toml", ".python-version",
    ]
    digests = {name: sha256_file(root / name) for name in files if (root / name).is_file()}
    return {
        "captured_at": utc_now(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "pip": command_version([sys.executable, "-m", "pip", "--version"]),
        "node": command_version(["node", "--version"]),
        "pnpm": command_version(["pnpm", "--version"]),
        "docker": command_version(["docker", "--version"]),
        "docker_compose": command_version(["docker", "compose", "version"]),
        "postgres_client": command_version(["psql", "--version"]),
        "redis_client": command_version(["redis-cli", "--version"]),
        "git": git_state(root),
        "input_digests": digests,
    }

@dataclass(frozen=True)
class CommandSpec:
    name: str
    command: tuple[str, ...]
    timeout: int = 900
    cwd: str = "."
    required: bool = True
    env: dict[str, str] | None = None


def run_command(root: Path, spec: CommandSpec, evidence_dir: Path) -> dict[str, Any]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    workdir = (root / spec.cwd).resolve()
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(root) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    if spec.env:
        env.update(spec.env)
    try:
        proc = run(
            list(spec.command), cwd=workdir, env=env, text=True, capture_output=True,
            timeout=spec.timeout, check=False,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        result = {
            "name": spec.name,
            "command": list(spec.command),
            "cwd": str(workdir.relative_to(root)) if workdir.is_relative_to(root) else str(workdir),
            "started_at": started,
            "finished_at": utc_now(),
            "exit_code": proc.returncode,
            "required": spec.required,
            "passed": proc.returncode == 0,
            "stdout_sha256": sha256_text(stdout),
            "stderr_sha256": sha256_text(stderr),
        }
    except TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes): stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode(errors="replace")
        result = {
            "name": spec.name, "command": list(spec.command), "cwd": str(workdir),
            "started_at": started, "finished_at": utc_now(), "exit_code": 124,
            "required": spec.required, "passed": False, "timed_out": True,
            "stdout_sha256": sha256_text(stdout), "stderr_sha256": sha256_text(stderr),
        }
    except OSError as exc:
        stdout = ""
        stderr = str(exc)
        result = {
            "name": spec.name, "command": list(spec.command), "cwd": str(workdir),
            "started_at": started, "finished_at": utc_now(), "exit_code": 127,
            "required": spec.required, "passed": False, "error": str(exc),
            "stdout_sha256": sha256_text(stdout), "stderr_sha256": sha256_text(stderr),
        }
    (evidence_dir / f"{spec.name}.stdout.log").write_text(stdout, encoding="utf-8")
    (evidence_dir / f"{spec.name}.stderr.log").write_text(stderr, encoding="utf-8")
    atomic_write_json(evidence_dir / f"{spec.name}.json", result)
    return result


def run_commands(root: Path, specs: Iterable[CommandSpec], evidence_dir: Path, *, stop_on_failure: bool = False) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in specs:
        result = run_command(root, spec, evidence_dir)
        results.append(result)
        if stop_on_failure and spec.required and not result["passed"]:
            break
    atomic_write_json(evidence_dir / "command_summary.json", {
        "captured_at": utc_now(),
        "all_required_green": all(r["passed"] or not r["required"] for r in results),
        "commands": results,
    })
    return results


def release_register_paths(root: Path) -> list[Path]:
    return [
        root / "docs/roadmap/production_readiness/production_readiness_register.json",
        root / "docs/roadmap/production_readiness/prd11_production_release_register.json",
        root / "docs/roadmap/production_readiness/true_state_remediation_register.json",
    ]


def verify_false_release_boundaries(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    inspected: list[str] = []
    for path in release_register_paths(root):
        if not path.exists():
            continue
        data = load_json(path, {})
        inspected.append(str(path.relative_to(root)))
        containers = [data]
        if isinstance(data.get("authority_boundaries"), dict):
            containers.append(data["authority_boundaries"])
        for container in containers:
            for key in FALSE_BOUNDARY_KEYS:
                if key in container and container[key] is not False:
                    failures.append(f"{path.relative_to(root)}:{key}={container[key]!r}")
    return {"valid": not failures, "inspected": inspected, "failures": failures}


def evidence_root(root: Path, bundle_id: str) -> Path:
    return root / "docs/release-evidence/true-state-remediation" / bundle_id.lower()


def manual_evidence_path(root: Path, bundle_id: str, control_id: str) -> Path:
    safe = control_id.lower().replace(".", "-")
    return evidence_root(root, bundle_id) / "manual" / f"{safe}.json"


def require_manual_evidence(root: Path, bundle_id: str, controls: Iterable[str]) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for control in controls:
        path = manual_evidence_path(root, bundle_id, control)
        if not path.exists():
            missing.append(control)
            continue
        data = load_json(path, {})
        artifact_value = data.get("artifact_path")
        artifact = Path(artifact_value) if artifact_value else None
        if artifact is not None and not artifact.is_absolute():
            artifact = root / artifact
        if not data.get("reviewer") or not data.get("reviewer_role") or not data.get("recorded_at"):
            invalid.append(f"{control}: reviewer metadata missing")
        elif artifact is None or not artifact.is_file():
            invalid.append(f"{control}: evidence artifact missing or not a file")
        elif data.get("artifact_sha256") != sha256_file(artifact):
            invalid.append(f"{control}: artifact digest mismatch")
        elif data.get("decision") not in {"approved", "accepted_with_expiry", "completed"}:
            invalid.append(f"{control}: decision is not approval/completion")
    return {"valid": not missing and not invalid, "missing": missing, "invalid": invalid}


def record_manual_evidence(root: Path, bundle_id: str, control_id: str, *, reviewer: str, reviewer_role: str, decision: str, artifact_path: str, notes: str = "", expiry: str | None = None) -> Path:
    artifact = Path(artifact_path)
    if not artifact.is_absolute():
        artifact = (root / artifact).resolve()
    if not artifact.exists() or not artifact.is_file():
        raise BundleError(f"Manual evidence artifact does not exist: {artifact}")
    payload = {
        "schema_version": "eduboost/true-state-remediation/manual-evidence/v1",
        "bundle_id": bundle_id,
        "control_id": control_id,
        "reviewer": reviewer,
        "reviewer_role": reviewer_role,
        "decision": decision,
        "artifact_path": str(artifact.relative_to(root)) if artifact.is_relative_to(root) else str(artifact),
        "artifact_sha256": sha256_file(artifact),
        "notes": notes,
        "expiry": expiry,
        "recorded_at": utc_now(),
    }
    path = manual_evidence_path(root, bundle_id, control_id)
    atomic_write_json(path, payload)
    return path


def register_path(root: Path) -> Path:
    return root / "docs/roadmap/production_readiness/true_state_remediation_register.json"


def update_task_status(root: Path, task_ids: Iterable[str], status: str, evidence: list[str] | None = None) -> None:
    path = register_path(root)
    data = load_json(path, {})
    tasks = data.get("tasks", [])
    ids = set(task_ids)
    found: set[str] = set()
    for task in tasks:
        if task.get("id") in ids:
            task["status"] = status
            task["updated_at"] = utc_now()
            if evidence:
                task.setdefault("evidence", [])
                for item in evidence:
                    if item not in task["evidence"]:
                        task["evidence"].append(item)
            found.add(task["id"])
    missing = ids - found
    if missing:
        raise BundleError(f"Task ids missing from remediation register: {sorted(missing)}")
    data["updated_at"] = utc_now()
    atomic_write_json(path, data)


def verify_register(root: Path) -> dict[str, Any]:
    path = register_path(root)
    if not path.exists():
        return {"valid": False, "errors": ["register missing"]}
    data = load_json(path, {})
    errors: list[str] = []
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty list")
        tasks = []
    ids = [t.get("id") for t in tasks]
    if len(ids) != len(set(ids)):
        errors.append("duplicate task ids")
    required_fields = {"id", "priority", "title", "deliverable", "acceptance_criteria", "owner_role", "status", "evidence"}
    allowed_status = {"identified", "authorised", "in_progress", "implementation_complete", "evidence_pending", "verified", "closed", "blocked", "accepted_risk", "superseded"}
    for task in tasks:
        missing = required_fields - set(task)
        if missing:
            errors.append(f"{task.get('id')}: missing {sorted(missing)}")
        if task.get("status") not in allowed_status:
            errors.append(f"{task.get('id')}: invalid status {task.get('status')!r}")
    boundaries = verify_false_release_boundaries(root)
    if not boundaries["valid"]:
        errors.extend(boundaries["failures"])
    return {"valid": not errors, "task_count": len(tasks), "errors": errors, "release_boundaries": boundaries}


def bundle_marker(root: Path, bundle_id: str) -> Path:
    return evidence_root(root, bundle_id) / "implementation_state.json"


def previous_bundle_id(bundle_id: str) -> str | None:
    number = int(bundle_id[1:])
    return None if number <= 1 else f"B{number-1:02d}"


def verify_previous_bundle(root: Path, bundle_id: str) -> dict[str, Any]:
    previous = previous_bundle_id(bundle_id)
    if previous is None:
        return {"valid": True, "previous": None}
    path = bundle_marker(root, previous)
    data = load_json(path, {})
    return {"valid": path.exists() and data.get("valid") is True, "previous": previous, "path": str(path), "state": data}


def write_bundle_state(root: Path, bundle_id: str, payload: dict[str, Any]) -> Path:
    path = bundle_marker(root, bundle_id)
    document = {
        "schema_version": "eduboost/true-state-remediation/bundle-state/v1",
        "bundle_id": bundle_id,
        "recorded_at": utc_now(),
        **payload,
    }
    atomic_write_json(path, document)
    return path
