#!/usr/bin/env python3
"""Run CAPS source ingestion stages 1–4 (see scripts/ingestion/README.md)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "data" / "caps" / "reports"
DEFAULT_STORAGE_ACCOUNT = "eduboostcaps06022047"
PYTHON = ROOT / ".venv" / "bin" / "python"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_cmd(label: str, args: list[str], *, capture_json: bool = False) -> dict[str, Any]:
    print(f"\n=== {label} ===")
    print(" ".join(str(part) for part in args))
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    payload: dict[str, Any] = {
        "label": label,
        "command": args,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if capture_json and result.stdout.strip():
        try:
            payload["json"] = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload["json_error"] = "stdout was not valid JSON"
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")
    return payload


def validate_text_extracts(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for record in payload.get("records") or []:
        doc_id = record.get("document_id", "unknown")
        pages = int(record.get("page_count") or 0)
        chars = int(record.get("char_count") or 0)
        if pages < 1:
            errors.append(f"{doc_id}: page_count={pages}")
        if chars < 1000:
            errors.append(f"{doc_id}: char_count={chars}")
        text_path = ROOT / str(record.get("text_extract_path") or "")
        if not text_path.exists():
            errors.append(f"{doc_id}: missing text file {text_path}")
    return errors


def stage_1_inventory(*, strict: bool) -> dict[str, Any]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "inventory_report.json"
    args = [str(PYTHON), "scripts/curriculum/source_inventory.py", "--json"]
    if strict:
        args.append("--strict")
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if result.stdout.strip():
        report_path.write_text(result.stdout.strip() + "\n", encoding="utf-8")
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Stage 1 failed with exit code {result.returncode}")
    return {
        "label": "Stage 1 — Inventory Audit",
        "exit_code": 0,
        "report_path": str(report_path.relative_to(ROOT)),
        "json": json.loads(result.stdout) if result.stdout.strip() else {},
    }


def stage_2_download(*, commit: bool, refresh: bool) -> dict[str, Any]:
    args = [str(PYTHON), "scripts/curriculum/download_caps_sources.py", "--json"]
    if commit:
        args.append("--commit")
    if refresh:
        args.append("--refresh")
    return run_cmd("Stage 2 — Download & Hash", args, capture_json=True)


def stage_3_publish(*, commit: bool, storage_account: str, container: str, auth_mode: str) -> dict[str, Any]:
    args = [
        str(PYTHON),
        "scripts/curriculum/upload_caps_sources_to_azure.py",
        "--storage-account",
        storage_account,
        "--container",
        container,
        "--auth-mode",
        auth_mode,
        "--json",
    ]
    if commit:
        args.append("--commit")
    return run_cmd("Stage 3 — Object Store Publish", args, capture_json=True)


def stage_4_extract(*, commit: bool) -> dict[str, Any]:
    result = run_cmd("Stage 4 — Source Text Extraction", [
        str(PYTHON),
        "scripts/curriculum/extract_caps_source_text.py",
        "--json",
        *(["--commit"] if commit else []),
    ], capture_json=True)
    quality_errors = validate_text_extracts(result.get("json") or {})
    if quality_errors:
        raise RuntimeError("Stage 4 quality gate failed: " + "; ".join(quality_errors))
    result["quality_passed"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, choices=[1, 2, 3, 4], help="Run one stage only.")
    parser.add_argument("--commit", action="store_true", help="Apply mutations for stages 2–4.")
    parser.add_argument("--refresh", action="store_true", help="Re-download PDFs in stage 2.")
    parser.add_argument("--strict", action="store_true", help="Fail stage 1 on blocking gaps.")
    parser.add_argument("--storage-account", default=DEFAULT_STORAGE_ACCOUNT)
    parser.add_argument("--container", default="caps-sources")
    parser.add_argument("--auth-mode", choices=["login", "key"], default="login")
    args = parser.parse_args()

    stages = [args.stage] if args.stage else [1, 2, 3, 4]
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "started_at": now_utc(),
        "stages_requested": stages,
        "commit": args.commit,
        "results": [],
    }
    try:
        for stage in stages:
            if stage == 1:
                report["results"].append(stage_1_inventory(strict=args.strict))
            elif stage == 2:
                report["results"].append(stage_2_download(commit=args.commit, refresh=args.refresh))
            elif stage == 3:
                report["results"].append(
                    stage_3_publish(
                        commit=args.commit,
                        storage_account=args.storage_account,
                        container=args.container,
                        auth_mode=args.auth_mode,
                    )
                )
            elif stage == 4:
                report["results"].append(stage_4_extract(commit=args.commit))
    except RuntimeError as exc:
        report["finished_at"] = now_utc()
        report["passed"] = False
        report["error"] = str(exc)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        out = REPORTS_DIR / "ingestion_pipeline_report.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nPipeline FAILED: {exc}", file=sys.stderr)
        print(f"Report: {out.relative_to(ROOT)}", file=sys.stderr)
        return 1

    report["finished_at"] = now_utc()
    report["passed"] = True
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / "ingestion_pipeline_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nPipeline passed. Report: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
