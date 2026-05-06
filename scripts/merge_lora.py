#!/usr/bin/env python3
"""Merge a trained LoRA adapter into its base model and emit export metadata."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("merge_lora")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ADAPTER_DIR = PROJECT_ROOT / "artifacts" / "llm" / "smollm2-caps-adapter"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "llm" / "merged-caps-model"
DEFAULT_MODEL_ID = "HuggingFaceTB/SmolLM2-360M-Instruct"


def build_export_metadata(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "base_model_id": args.model_id,
        "adapter_dir": str(Path(args.adapter_dir).resolve()),
        "merged_output_dir": str(Path(args.output_dir).resolve()),
        "torch_dtype": args.torch_dtype,
        "quantization": args.quantization,
        "quantization_note": (
            "Merged weights are saved in Hugging Face format. Use llama.cpp conversion for GGUF "
            "or autoawq/llm-awq in a dedicated export environment when quantization is requested."
            if args.quantization != "none"
            else "No post-merge quantization requested."
        ),
    }


def require_merge_dependencies() -> dict[str, Any]:
    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:  # pragma: no cover - depends on model export image
        raise RuntimeError("Install ML dependencies before merging LoRA weights") from exc
    return {
        "torch": torch,
        "PeftModel": PeftModel,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
    }


def resolve_dtype(torch: Any, dtype_name: str) -> Any:
    if dtype_name == "bfloat16":
        return torch.bfloat16
    if dtype_name == "float16":
        return torch.float16
    if dtype_name == "float32":
        return torch.float32
    raise ValueError(f"Unsupported dtype: {dtype_name}")


def merge(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = build_export_metadata(args)
    (output_dir / "export_metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

    if args.dry_run:
        print(json.dumps(metadata, indent=2))
        return 0

    deps = require_merge_dependencies()
    torch = deps["torch"]
    PeftModel = deps["PeftModel"]
    AutoModelForCausalLM = deps["AutoModelForCausalLM"]
    AutoTokenizer = deps["AutoTokenizer"]

    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        torch_dtype=resolve_dtype(torch, args.torch_dtype),
        device_map=args.device_map,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, args.adapter_dir)
    merged = model.merge_and_unload()
    tokenizer = AutoTokenizer.from_pretrained(args.adapter_dir, trust_remote_code=True)
    merged.save_pretrained(output_dir, safe_serialization=True, max_shard_size=args.max_shard_size)
    tokenizer.save_pretrained(output_dir)
    LOGGER.info("Merged model saved to %s", output_dir)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge EduBoost LoRA adapter into the base model.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--adapter-dir", default=str(DEFAULT_ADAPTER_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--torch-dtype", choices=["bfloat16", "float16", "float32"], default="bfloat16")
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--max-shard-size", default="4GB")
    parser.add_argument("--quantization", choices=["none", "awq", "gguf"], default="none")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    return merge(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
