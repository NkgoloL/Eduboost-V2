#!/usr/bin/env python3
"""LoRA/QLoRA fine-tuning entry point for the EduBoost CAPS LLM adapter."""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("train_lora")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = PROJECT_ROOT / "data" / "caps" / "training_data.jsonl"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "llm" / "smollm2-caps-adapter"
DEFAULT_MODEL_ID = os.getenv("EDUBOOST_BASE_MODEL_ID", "HuggingFaceTB/SmolLM2-360M-Instruct")
SYSTEM_PROMPT = (
    "You are EduBoost Brain, a South African CAPS-aligned teaching assistant. "
    "Respond with age-appropriate pedagogy, clear structure, and POPIA-safe language. "
    "When generating lessons, use these sections: Title, Grade, Subject, CAPS alignment, "
    "Lesson objective, Teaching activity, Worked example, Assessment evidence, and Support and extension."
)


@dataclass(frozen=True)
class TrainingExample:
    instruction: str
    output: str
    input: str = ""


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
    return records


def normalise_example(record: dict[str, Any], line_number: int) -> TrainingExample:
    instruction = str(record.get("instruction", "")).strip()
    output = str(record.get("output", record.get("response", ""))).strip()
    input_text = str(record.get("input", "")).strip()
    if not instruction:
        raise ValueError(f"Training record {line_number} is missing 'instruction'")
    if not output:
        raise ValueError(f"Training record {line_number} is missing 'output'")
    return TrainingExample(instruction=instruction, input=input_text, output=output)


def load_training_examples(path: Path) -> list[TrainingExample]:
    return [normalise_example(record, idx) for idx, record in enumerate(load_jsonl(path), start=1)]


def format_chat_prompt(example: TrainingExample, eos_token: str = "") -> str:
    user_content = example.instruction
    if example.input:
        user_content = f"{user_content}\n\nContext:\n{example.input}"
    return (
        "<|system|>\n"
        f"{SYSTEM_PROMPT}\n"
        "<|user|>\n"
        f"{user_content}\n"
        "<|assistant|>\n"
        f"{example.output}{eos_token}"
    )


def split_examples(
    examples: list[TrainingExample], validation_ratio: float, seed: int
) -> tuple[list[TrainingExample], list[TrainingExample]]:
    if not examples:
        raise ValueError("Training dataset is empty")
    shuffled = examples[:]
    random.Random(seed).shuffle(shuffled)
    validation_size = max(1, int(len(shuffled) * validation_ratio)) if len(shuffled) > 1 else 0
    if validation_size >= len(shuffled):
        validation_size = len(shuffled) - 1
    return shuffled[validation_size:], shuffled[:validation_size]


def write_training_config(path: Path, args: argparse.Namespace, train_size: int, eval_size: int) -> None:
    path.mkdir(parents=True, exist_ok=True)
    config = {
        "model_id": args.model_id,
        "training_mode": args.training_mode,
        "dataset": str(Path(args.dataset).resolve()),
        "output_dir": str(path.resolve()),
        "train_size": train_size,
        "eval_size": eval_size,
        "max_seq_length": args.max_seq_length,
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "target_modules": args.target_modules,
        "seed": args.seed,
    }
    (path / "training_config.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")


def require_training_dependencies() -> dict[str, Any]:
    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
        from trl import SFTTrainer
    except ImportError as exc:  # pragma: no cover - depends on training image
        raise RuntimeError("Missing LoRA dependencies. Install with: pip install -r requirements-ml.txt") from exc
    return {
        "torch": torch,
        "Dataset": Dataset,
        "LoraConfig": LoraConfig,
        "prepare_model_for_kbit_training": prepare_model_for_kbit_training,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
        "BitsAndBytesConfig": BitsAndBytesConfig,
        "TrainingArguments": TrainingArguments,
        "SFTTrainer": SFTTrainer,
    }


def build_datasets(Dataset: Any, tokenizer: Any, train_examples: list[TrainingExample], eval_examples: list[TrainingExample]) -> tuple[Any, Any | None]:
    eos_token = tokenizer.eos_token or ""
    train_dataset = Dataset.from_dict({"text": [format_chat_prompt(example, eos_token) for example in train_examples]})
    eval_dataset = None
    if eval_examples:
        eval_dataset = Dataset.from_dict({"text": [format_chat_prompt(example, eos_token) for example in eval_examples]})
    return train_dataset, eval_dataset


def load_model_for_mode(args: argparse.Namespace, deps: dict[str, Any]) -> Any:
    torch = deps["torch"]
    AutoModelForCausalLM = deps["AutoModelForCausalLM"]
    BitsAndBytesConfig = deps["BitsAndBytesConfig"]
    prepare_model_for_kbit_training = deps["prepare_model_for_kbit_training"]

    if args.training_mode == "qlora":
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            args.model_id,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True,
        )
        model = prepare_model_for_kbit_training(model)
    else:
        dtype = torch.float32 if args.cpu_dtype == "float32" else torch.bfloat16
        model = AutoModelForCausalLM.from_pretrained(
            args.model_id,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
        if args.gradient_checkpointing:
            model.gradient_checkpointing_enable()

    model.config.use_cache = False
    return model


def run_training(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    dataset_path = Path(args.dataset).resolve()
    output_dir = Path(args.output_dir).resolve()
    examples = load_training_examples(dataset_path)
    train_examples, eval_examples = split_examples(examples, args.validation_ratio, args.seed)
    write_training_config(output_dir, args, len(train_examples), len(eval_examples))

    LOGGER.info("Loaded %s training and %s validation examples", len(train_examples), len(eval_examples))
    if args.dry_run:
        preview = format_chat_prompt(train_examples[0], eos_token="<eos>")
        print(json.dumps({"train_size": len(train_examples), "eval_size": len(eval_examples), "model_id": args.model_id, "training_mode": args.training_mode, "preview": preview[:800]}, indent=2))
        return 0

    deps = require_training_dependencies()
    torch = deps["torch"]
    Dataset = deps["Dataset"]
    LoraConfig = deps["LoraConfig"]
    AutoTokenizer = deps["AutoTokenizer"]
    TrainingArguments = deps["TrainingArguments"]
    SFTTrainer = deps["SFTTrainer"]

    if args.training_mode == "qlora" and not torch.cuda.is_available():
        raise RuntimeError("--training-mode qlora requires CUDA. Use --training-mode cpu-lora on this machine.")

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_dataset, eval_dataset = build_datasets(Dataset, tokenizer, train_examples, eval_examples)
    model = load_model_for_mode(args, deps)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[module.strip() for module in args.target_modules.split(",") if module.strip()],
    )
    use_cuda = args.training_mode == "qlora"
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps if args.max_steps else -1,
        warmup_ratio=args.warmup_ratio,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        eval_steps=args.eval_steps,
        evaluation_strategy="steps" if eval_dataset is not None else "no",
        save_strategy="steps",
        bf16=use_cuda and torch.cuda.is_bf16_supported(),
        fp16=use_cuda and not torch.cuda.is_bf16_supported(),
        optim="paged_adamw_8bit" if use_cuda else "adamw_torch",
        gradient_checkpointing=args.gradient_checkpointing,
        report_to=args.report_to,
        seed=args.seed,
        no_cuda=not use_cuda,
    )
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        peft_config=lora_config,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        args=training_args,
        packing=args.packing,
    )
    trainer.train(resume_from_checkpoint=args.resume_from_checkpoint or None)
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    LOGGER.info("Saved LoRA adapter to %s", output_dir)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fine-tune the EduBoost CAPS adapter with CPU LoRA or GPU QLoRA.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="Instruction JSONL with instruction/output fields.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Base Hugging Face model id.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="LoRA adapter output directory.")
    parser.add_argument("--training-mode", choices=["cpu-lora", "qlora"], default="cpu-lora")
    parser.add_argument("--validation-ratio", type=float, default=0.1)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--max-steps", type=int, default=0, help="Override epochs when non-zero.")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--warmup-ratio", type=float, default=0.03)
    parser.add_argument("--logging-steps", type=int, default=5)
    parser.add_argument("--save-steps", type=int, default=50)
    parser.add_argument("--eval-steps", type=int, default=50)
    parser.add_argument("--lora-r", type=int, default=8)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--target-modules", default="q_proj,k_proj,v_proj,o_proj", help="Comma-separated LoRA target module names.")
    parser.add_argument("--cpu-dtype", choices=["float32", "bfloat16"], default="float32")
    parser.add_argument("--report-to", default="none", help="Trainer reporting target, e.g. none, tensorboard, wandb.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--packing", action="store_true", help="Enable TRL sequence packing.")
    parser.add_argument("--gradient-checkpointing", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--resume-from-checkpoint", default="", help="Resume Trainer state from a checkpoint directory.")
    parser.add_argument("--dry-run", action="store_true", help="Validate dataset and print a prompt preview without loading the model.")
    return parser


def main() -> int:
    return run_training(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
