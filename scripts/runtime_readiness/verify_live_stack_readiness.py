#!/usr/bin/env python3
"""Verify Phase 14 live-stack readiness evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from typing import Any

DEFAULT_RECORD = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_14_live_stack_readiness_record.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_RAW_FILES = (
    "raw/git_state.json",
    "raw/post_merge_baseline_verification.json",
    "raw/probe_health.json",
    "raw/probe_ready.json",
    "raw/probe_deep_v2.json",
    "raw/probe_deep_api_v2.json",
    "raw/probe_openapi.json",
    "raw/live_stack_readiness_result.json",
)
CRITICAL_COMPONENTS = ("secrets", "postgres", "redis", "migrations", "audit_repository")
FALSE_BOUNDARY_FIELDS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "live_learner_traffic_authorised",
    "runtime_kg_implementation_claimed",
)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha256sums(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing SHA256SUMS file: {path}"]
    seen: set[str] = set()
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected, rel = line.split(None, 1)
        except ValueError:
            errors.append(f"invalid SHA256SUMS line {idx}: {line!r}")
            continue
        rel = rel.strip().lstrip("*")
        target = pathlib.Path(rel)
        if target.name == path.name:
            errors.append("SHA256SUMS must not include itself")
            continue
        seen.add(target.as_posix())
        if not target.exists():
            errors.append(f"SHA256SUMS references missing file: {target}")
            continue
        actual = sha256_file(target)
        if actual != expected:
            errors.append(f"SHA mismatch for {target}: expected {expected}, got {actual}")
    if not seen:
        errors.append("SHA256SUMS contains no file entries")
    return errors


def probe_json(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("json")
    return value if isinstance(value, dict) else {}


def verify_deep_probe(label: str, probe: dict[str, Any], *, allow_optional_degraded: bool) -> list[str]:
    errors: list[str] = []
    if probe.get("status_code") != 200:
        errors.append(f"{label} must return HTTP 200")
        return errors
    data = probe_json(probe)
    if not data:
        errors.append(f"{label} must contain JSON")
        return errors
    if data.get("status") not in {"ok", "degraded"}:
        errors.append(f"{label} status must be ok or degraded")
    critical = data.get("critical") if isinstance(data.get("critical"), dict) else {}
    optional = data.get("optional") if isinstance(data.get("optional"), dict) else {}
    for component in CRITICAL_COMPONENTS:
        comp = critical.get(component)
        if not isinstance(comp, dict) or comp.get("status") != "ok":
            errors.append(f"{label} critical.{component}.status must be ok")
    if not allow_optional_degraded:
        for name, comp in optional.items():
            if isinstance(comp, dict) and comp.get("status") not in {"ok", "skipped"}:
                errors.append(f"{label} optional.{name}.status must be ok or skipped")
    return errors


def verify_record(record_path: pathlib.Path = DEFAULT_RECORD) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []
    raw_payloads: dict[str, Any] = {}

    if not record_path.exists():
        return {"valid": False, "record": record_path.as_posix(), "errors": [f"missing record: {record_path}"], "warnings": [], "checked": []}
    record = load_json(record_path)
    checked.append(record_path.as_posix())
    if not isinstance(record, dict):
        raise AssertionError("live-stack readiness record must be a JSON object")

    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "PHASE-14-LIVE-STACK-READINESS-AUTHORITY":
        errors.append("slice must be PHASE-14-LIVE-STACK-READINESS-AUTHORITY")
    if record.get("status") != "live_stack_readiness_recorded":
        errors.append("status must be live_stack_readiness_recorded")
    if record.get("live_stack_readiness_claimed") is not True:
        errors.append("live_stack_readiness_claimed must be true")
    if record.get("live_stack_readiness_recorded") is not True:
        errors.append("live_stack_readiness_recorded must be true")
    if record.get("post_merge_baseline_valid") is not True:
        errors.append("post_merge_baseline_valid must be true")
    for field in ["postgres_readiness_claimed", "redis_readiness_claimed", "migration_readiness_claimed", "audit_repository_readiness_claimed"]:
        if record.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in ["source_commit", "remote_target_sha"]:
        value = record.get(field)
        if not isinstance(value, str) or not SHA_RE.match(value):
            errors.append(f"{field} must be a 40-character lowercase git SHA")
    if record.get("source_commit") != record.get("remote_target_sha"):
        errors.append("source_commit must match remote_target_sha")
    if record.get("target_branch") != "master":
        errors.append("target_branch must be master")
    if not isinstance(record.get("readiness_owner"), str) or not record["readiness_owner"].strip():
        errors.append("readiness_owner is required")
    for field in FALSE_BOUNDARY_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field} must remain false")

    evidence_dir_value = record.get("evidence_dir")
    if not isinstance(evidence_dir_value, str):
        errors.append("evidence_dir is required")
        evidence_dir = pathlib.Path("missing-evidence-dir")
    else:
        evidence_dir = pathlib.Path(evidence_dir_value)
        checked.append(evidence_dir.as_posix())
        if not evidence_dir.exists():
            errors.append(f"evidence_dir missing: {evidence_dir}")

    sums_value = record.get("sha256sums")
    if not isinstance(sums_value, str):
        errors.append("sha256sums is required")
    else:
        sums_path = pathlib.Path(sums_value)
        checked.append(sums_path.as_posix())
        errors.extend(verify_sha256sums(sums_path))

    if evidence_dir.exists():
        for rel in REQUIRED_RAW_FILES:
            path = evidence_dir / rel
            checked.append(path.as_posix())
            if not path.exists():
                errors.append(f"required raw evidence file missing: {path}")
                continue
            try:
                raw_payloads[rel] = load_json(path)
            except Exception as exc:
                errors.append(f"could not read {path}: {exc}")

    post_merge = raw_payloads.get("raw/post_merge_baseline_verification.json") or {}
    if post_merge.get("valid") is not True:
        errors.append("post-merge baseline verification must be valid")

    git_state = raw_payloads.get("raw/git_state.json") or {}
    if git_state:
        if git_state.get("tracked_worktree_clean_before_capture") is not True:
            errors.append("git_state.tracked_worktree_clean_before_capture must be true")
        if git_state.get("branch") != record.get("target_branch"):
            errors.append("git_state.branch must match target_branch")
        if git_state.get("head_sha") != record.get("source_commit"):
            errors.append("git_state.head_sha must match source_commit")
        if git_state.get("remote_target_sha") != record.get("source_commit"):
            errors.append("git_state.remote_target_sha must match source_commit")

    health = raw_payloads.get("raw/probe_health.json") or {}
    if health.get("status_code") != 200:
        errors.append("/health must return HTTP 200")
    elif probe_json(health).get("status") != "ok":
        errors.append("/health JSON status must be ok")

    openapi = raw_payloads.get("raw/probe_openapi.json") or {}
    if openapi.get("status_code") != 200:
        errors.append("/openapi.json must return HTTP 200")
    elif "openapi" not in probe_json(openapi):
        errors.append("/openapi.json must contain an OpenAPI document")

    allow_optional_degraded = bool(record.get("allow_optional_degraded"))
    for rel, label in [
        ("raw/probe_ready.json", "/ready"),
        ("raw/probe_deep_v2.json", "/v2/health/deep"),
        ("raw/probe_deep_api_v2.json", "/api/v2/health/deep"),
    ]:
        payload = raw_payloads.get(rel) or {}
        errors.extend(verify_deep_probe(label, payload, allow_optional_degraded=allow_optional_degraded))

    result = raw_payloads.get("raw/live_stack_readiness_result.json") or {}
    if result:
        if result.get("valid") is not True:
            errors.append("live_stack_readiness_result.valid must be true")
        if result.get("live_stack_readiness_recorded") is not True:
            errors.append("live_stack_readiness_result.live_stack_readiness_recorded must be true")
        for field in FALSE_BOUNDARY_FIELDS:
            if result.get(field) is not False:
                errors.append(f"live_stack_readiness_result.{field} must remain false")

    index_value = record.get("evidence_index")
    if not isinstance(index_value, str):
        errors.append("evidence_index is required")
    else:
        index_path = pathlib.Path(index_value)
        checked.append(index_path.as_posix())
        if not index_path.exists():
            errors.append(f"evidence_index missing: {index_path}")
        else:
            text = index_path.read_text(encoding="utf-8")
            for phrase in [
                "Phase 14 Live-Stack Readiness Evidence",
                "Critical components required: secrets, postgres, redis, migrations, audit_repository",
                "Production release authorised: false",
                "Runtime KG implementation claimed: false",
            ]:
                if phrase not in text:
                    errors.append(f"evidence_index.md missing required phrase: {phrase}")

    return {
        "valid": len(errors) == 0,
        "record": record_path.as_posix(),
        "live_stack_readiness_recorded": bool(record.get("live_stack_readiness_recorded")),
        "post_merge_baseline_valid": bool(record.get("post_merge_baseline_valid")),
        "postgres_readiness_claimed": bool(record.get("postgres_readiness_claimed")),
        "redis_readiness_claimed": bool(record.get("redis_readiness_claimed")),
        "production_release_authorised": bool(record.get("production_release_authorised")),
        "deployment_authorised": bool(record.get("deployment_authorised")),
        "release_tag_authorised": bool(record.get("release_tag_authorised")),
        "live_learner_traffic_authorised": bool(record.get("live_learner_traffic_authorised")),
        "runtime_kg_implementation_claimed": bool(record.get("runtime_kg_implementation_claimed")),
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", default=str(DEFAULT_RECORD))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify_record(pathlib.Path(args.record))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"valid: {result['valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
