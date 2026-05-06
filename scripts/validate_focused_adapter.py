#!/usr/bin/env python3
"""Validate and prepare the focused SmolLM2 CAPS adapter for app-level testing."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_ID = "HuggingFaceTB/SmolLM2-360M-Instruct"
DEFAULT_ADAPTER_DIR = PROJECT_ROOT / "artifacts" / "llm" / "smollm2-caps-focused-9epoch-adapter"
DEFAULT_MERGED_DIR = PROJECT_ROOT / "artifacts" / "llm" / "merged-smollm2-caps-focused-model"
DEFAULT_BENCHMARK = PROJECT_ROOT / "tests" / "fixtures" / "llm" / "focused_caps_eval.jsonl"
DEFAULT_REPORT = PROJECT_ROOT / "artifacts" / "llm" / "pedagogy_eval_report_focused_9epoch.json"


def run_step(command: list[str], *, dry_run: bool) -> None:
    print("+", " ".join(command))
    if dry_run:
        return
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def run_quality_gate(command: list[str], *, dry_run: bool, continue_on_failure: bool) -> None:
    print("+", " ".join(command))
    if dry_run:
        return
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if result.returncode and not continue_on_failure:
        raise subprocess.CalledProcessError(result.returncode, command)
    if result.returncode:
        print(f"Quality gate failed with exit code {result.returncode}; continuing for sandbox export.")


def ensure_adapter_ready(adapter_dir: Path) -> None:
    required = ["adapter_config.json", "adapter_model.safetensors", "tokenizer_config.json"]
    missing = [name for name in required if not (adapter_dir / name).exists()]
    if missing:
        raise SystemExit(f"Adapter is incomplete at {adapter_dir}: missing {', '.join(missing)}")


def write_manifest(path: Path, args: argparse.Namespace) -> None:
    manifest = {
        "adapter_dir": str(Path(args.adapter_dir).resolve()),
        "benchmark_file": str(Path(args.benchmark_file).resolve()),
        "merged_output_dir": str(Path(args.merged_output_dir).resolve()),
        "model_id": args.model_id,
        "pedagogy_report": str(Path(args.report).resolve()),
        "steps": {
            "evaluate": not args.skip_eval,
            "merge": not args.skip_merge,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def validate(args: argparse.Namespace) -> int:
    adapter_dir = Path(args.adapter_dir).resolve()
    ensure_adapter_ready(adapter_dir)
    write_manifest(Path(args.manifest).resolve(), args)

    if not args.skip_eval:
        run_quality_gate(
            [
                sys.executable,
                "scripts/evaluate_pedagogy.py",
                "--model-id",
                args.model_id,
                "--adapter-dir",
                str(adapter_dir),
                "--benchmark-file",
                args.benchmark_file,
                "--report",
                args.report,
                "--min-pass-rate",
                str(args.min_pass_rate),
                "--max-new-tokens",
                str(args.max_new_tokens),
                "--temperature",
                str(args.temperature),
            ],
            dry_run=args.dry_run,
            continue_on_failure=args.continue_on_eval_failure,
        )

    if not args.skip_merge:
        run_step(
            [
                sys.executable,
                "scripts/merge_lora.py",
                "--model-id",
                args.model_id,
                "--adapter-dir",
                str(adapter_dir),
                "--output-dir",
                args.merged_output_dir,
                "--torch-dtype",
                args.torch_dtype,
            ],
            dry_run=args.dry_run,
        )

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate and merge the focused CAPS LoRA adapter.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--adapter-dir", default=str(DEFAULT_ADAPTER_DIR))
    parser.add_argument("--benchmark-file", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--merged-output-dir", default=str(DEFAULT_MERGED_DIR))
    parser.add_argument("--manifest", default=str(PROJECT_ROOT / "artifacts" / "llm" / "focused_adapter_validation_manifest.json"))
    parser.add_argument("--min-pass-rate", type=float, default=0.8)
    parser.add_argument("--max-new-tokens", type=int, default=700)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--torch-dtype", choices=["bfloat16", "float16", "float32"], default="float32")
    parser.add_argument("--skip-eval", action="store_true")
    parser.add_argument("--skip-merge", action="store_true")
    parser.add_argument(
        "--continue-on-eval-failure",
        action="store_true",
        help="Continue to merge/export even when the pedagogy pass-rate gate fails.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    return validate(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
