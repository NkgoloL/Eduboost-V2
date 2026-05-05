#!/usr/bin/env python3
"""Evaluate a CAPS-tuned adapter against lightweight pedagogical benchmarks."""
from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("evaluate_pedagogy")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ADAPTER_DIR = PROJECT_ROOT / "artifacts" / "llm" / "smollm2-caps-adapter"
DEFAULT_REPORT = PROJECT_ROOT / "artifacts" / "llm" / "pedagogy_eval_report.json"
DEFAULT_MODEL_ID = "HuggingFaceTB/SmolLM2-360M-Instruct"


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    prompt: str
    required_terms: list[str]
    forbidden_terms: list[str] = field(default_factory=list)
    min_words: int = 40


DEFAULT_BENCHMARKS = [
    BenchmarkCase(
        id="grade4-fractions-caps",
        prompt="Generate a Grade 4 Mathematics mini lesson on equivalent fractions aligned to CAPS.",
        required_terms=["grade 4", "fractions", "caps", "assessment"],
        forbidden_terms=["calculus", "university"],
    ),
    BenchmarkCase(
        id="grade2-life-skills-age-appropriate",
        prompt="Explain a Grade 2 Life Skills activity about healthy habits using age-appropriate language.",
        required_terms=["grade 2", "life skills", "healthy", "activity"],
        forbidden_terms=["adolescent", "tertiary"],
    ),
    BenchmarkCase(
        id="grade7-natural-sciences-term-map",
        prompt="Map a Grade 7 Natural Sciences topic on ecosystems to a CAPS-style lesson objective and assessment evidence.",
        required_terms=["grade 7", "natural sciences", "ecosystem", "objective", "assessment"],
        forbidden_terms=["personal data", "phone number"],
    ),
]


def normalise_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def score_response(response: str, case: BenchmarkCase) -> dict[str, Any]:
    text = normalise_text(response)
    words = re.findall(r"\b\w+\b", text)
    matched_terms = [term for term in case.required_terms if term.lower() in text]
    forbidden_hits = [term for term in case.forbidden_terms if term.lower() in text]
    coverage = len(matched_terms) / len(case.required_terms) if case.required_terms else 1.0
    length_ok = len(words) >= case.min_words
    passed = coverage >= 0.75 and not forbidden_hits and length_ok
    return {
        "id": case.id,
        "passed": passed,
        "score": round((coverage * 0.8) + (0.2 if length_ok else 0.0), 3),
        "matched_terms": matched_terms,
        "missing_terms": [term for term in case.required_terms if term not in matched_terms],
        "forbidden_hits": forbidden_hits,
        "word_count": len(words),
    }


def load_benchmarks(path: Path | None) -> list[BenchmarkCase]:
    if path is None:
        return DEFAULT_BENCHMARKS
    cases: list[BenchmarkCase] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            try:
                cases.append(BenchmarkCase(**record))
            except TypeError as exc:
                raise ValueError(f"Invalid benchmark case on {path}:{line_number}: {exc}") from exc
    return cases


def load_predictions(path: Path) -> dict[str, str]:
    predictions: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            case_id = str(record.get("id", "")).strip()
            response = str(record.get("response", record.get("output", ""))).strip()
            if not case_id or not response:
                raise ValueError(f"Prediction on {path}:{line_number} needs id and response/output")
            predictions[case_id] = response
    return predictions


def generate_responses(args: argparse.Namespace, cases: list[BenchmarkCase]) -> dict[str, str]:
    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:  # pragma: no cover - depends on GPU/image deps
        raise RuntimeError("Install ML dependencies before model-backed evaluation") from exc

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        device_map="auto",
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, args.adapter_dir)
    model.eval()

    responses: dict[str, str] = {}
    for case in cases:
        prompt = (
            "You are EduBoost Brain. Answer in CAPS-aligned South African classroom language.\n\n"
            f"Instruction: {case.prompt}\nResponse:"
        )
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                do_sample=args.temperature > 0,
                pad_token_id=tokenizer.eos_token_id,
            )
        decoded = tokenizer.decode(output[0], skip_special_tokens=True)
        responses[case.id] = decoded.split("Response:", 1)[-1].strip()
    return responses


def evaluate(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    cases = load_benchmarks(Path(args.benchmark_file) if args.benchmark_file else None)
    if args.dry_run:
        print(json.dumps([asdict(case) for case in cases], indent=2))
        return 0

    if args.predictions:
        responses = load_predictions(Path(args.predictions))
    else:
        responses = generate_responses(args, cases)

    case_results = []
    for case in cases:
        response = responses.get(case.id, "")
        result = score_response(response, case)
        result["prompt"] = case.prompt
        result["response_preview"] = response[:500]
        case_results.append(result)

    passed = sum(1 for result in case_results if result["passed"])
    report = {
        "passed": passed,
        "total": len(case_results),
        "pass_rate": round(passed / len(case_results), 3) if case_results else 0.0,
        "cases": case_results,
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["pass_rate"] >= args.min_pass_rate else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate CAPS pedagogy quality for a LoRA adapter.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--adapter-dir", default=str(DEFAULT_ADAPTER_DIR))
    parser.add_argument("--benchmark-file", help="Optional JSONL benchmark cases.")
    parser.add_argument("--predictions", help="JSONL with id + response/output to score without loading a model.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--min-pass-rate", type=float, default=0.8)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    return evaluate(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
