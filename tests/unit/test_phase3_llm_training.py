import argparse
import json
from pathlib import Path

from scripts.evaluate_pedagogy import BenchmarkCase, score_response
from scripts.merge_lora import build_export_metadata
from scripts.train_qlora import TrainingExample, format_chat_prompt, load_training_examples, split_examples


def test_format_chat_prompt_includes_caps_system_and_context():
    prompt = format_chat_prompt(
        TrainingExample(
            instruction="Plan a Grade 4 fractions lesson.",
            input="Learners are beginning equivalent fractions.",
            output="Use concrete fraction strips.",
        ),
        eos_token="<eos>",
    )

    assert "CAPS-aligned" in prompt
    assert "Context:" in prompt
    assert "fraction strips.<eos>" in prompt


def test_load_training_examples_accepts_instruction_output_jsonl(tmp_path: Path):
    dataset = tmp_path / "training.jsonl"
    dataset.write_text(
        json.dumps({"instruction": "Teach Grade 2 Life Skills", "output": "Use a short activity."}) + "\n",
        encoding="utf-8",
    )

    examples = load_training_examples(dataset)

    assert examples == [TrainingExample(instruction="Teach Grade 2 Life Skills", output="Use a short activity.")]


def test_split_examples_keeps_validation_set_deterministic():
    examples = [TrainingExample(instruction=f"i{idx}", output="o") for idx in range(10)]

    train_a, eval_a = split_examples(examples, validation_ratio=0.2, seed=7)
    train_b, eval_b = split_examples(examples, validation_ratio=0.2, seed=7)

    assert train_a == train_b
    assert eval_a == eval_b
    assert len(eval_a) == 2


def test_score_response_checks_required_and_forbidden_terms():
    case = BenchmarkCase(
        id="caps-grade4",
        prompt="Prompt",
        required_terms=["grade 4", "fractions", "assessment", "caps"],
        forbidden_terms=["calculus"],
        min_words=5,
    )

    result = score_response(
        "This Grade 4 CAPS fractions activity includes assessment evidence for learners.",
        case,
    )

    assert result["passed"] is True
    assert result["score"] == 1.0


def test_build_export_metadata_records_quantization_plan(tmp_path: Path):
    args = argparse.Namespace(
        model_id="base-model",
        adapter_dir=str(tmp_path / "adapter"),
        output_dir=str(tmp_path / "merged"),
        torch_dtype="bfloat16",
        quantization="gguf",
    )

    metadata = build_export_metadata(args)

    assert metadata["base_model_id"] == "base-model"
    assert metadata["quantization"] == "gguf"
    assert "GGUF" in metadata["quantization_note"]


def test_training_parser_defaults_to_cpu_smollm2():
    from scripts.train_qlora import build_parser

    args = build_parser().parse_args([])

    assert args.training_mode == "cpu-lora"
    assert args.model_id == "HuggingFaceTB/SmolLM2-360M-Instruct"
