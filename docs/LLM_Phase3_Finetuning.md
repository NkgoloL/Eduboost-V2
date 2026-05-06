# LLM Phase 3 Fine-Tuning Runbook

This runbook covers the current CPU-friendly Phase 3 workflow for training the EduBoost CAPS LoRA adapter while GPU provisioning is blocked. The GPU QLoRA path remains available through `--training-mode qlora` once CUDA infrastructure is ready.

## Inputs

- Training dataset: `data/caps/training_data_with_guardrails.jsonl` when available, otherwise `data/caps/training_data.jsonl`
- Expected JSONL fields: `instruction`, `output`, optional `input`
- Default base model: `HuggingFaceTB/SmolLM2-360M-Instruct`
- Default adapter output: `artifacts/llm/smollm2-caps-adapter`

## 1. Complete Phase 2 Data Assets

Build the pedagogical guardrails dataset and append it to the CAPS training records:

```bash
python scripts/build_guardrails_dataset.py --combine
```

Dry-run the R2 upload plan for local curated CAPS assets:

```bash
python scripts/sync_caps_r2.py --direction upload --dry-run
```

Upload when R2 credentials are present in the environment:

```bash
python scripts/sync_caps_r2.py --direction upload
```

## 2. Validate The CPU Training Dataset

```bash
python scripts/train_qlora.py \
  --training-mode cpu-lora \
  --dataset data/caps/training_data_with_guardrails.jsonl \
  --dry-run
```

This validates JSONL, creates `training_config.json`, splits train/validation data, and prints a prompt preview without loading the model.

## 3. Train The CPU LoRA Adapter

```bash
pip install -r requirements-ml.txt
huggingface-cli login
python scripts/train_qlora.py \
  --training-mode cpu-lora \
  --model-id HuggingFaceTB/SmolLM2-360M-Instruct \
  --dataset data/caps/training_data_with_guardrails.jsonl \
  --output-dir artifacts/llm/smollm2-caps-adapter \
  --epochs 1 \
  --batch-size 1 \
  --gradient-accumulation-steps 8 \
  --max-seq-length 1024
```

This path uses standard PEFT LoRA on CPU with `adamw_torch`, no CUDA, and no 4-bit `bitsandbytes` dependency at runtime. It is intended to validate EduBoost data and pedagogy behavior, not to replace the later larger GPU model.

Latest local smoke result:

- Base model: `HuggingFaceTB/SmolLM2-360M-Instruct`
- Training mode: `cpu-lora`
- Dataset: `data/caps/training_data_with_guardrails.jsonl`
- Train/eval split: 27 / 2 examples
- Smoke run: 4 optimizer steps, `max_seq_length=512`
- Final train loss: `3.9698`
- Eval loss: `4.1111`
- Adapter output: `artifacts/llm/smollm2-caps-adapter`

## 4. Optional GPU QLoRA Later

```bash
python scripts/train_qlora.py \
  --training-mode qlora \
  --model-id deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
  --dataset data/caps/training_data_with_guardrails.jsonl \
  --output-dir artifacts/llm/qlora-caps-adapter
```

## 5. Evaluate Pedagogical Accuracy

Score saved predictions without loading a model:

```bash
python scripts/evaluate_pedagogy.py \
  --predictions artifacts/llm/pedagogy_predictions.jsonl \
  --report artifacts/llm/pedagogy_eval_report.json
```

Run model-backed evaluation after the adapter exists:

```bash
python scripts/evaluate_pedagogy.py \
  --model-id HuggingFaceTB/SmolLM2-360M-Instruct \
  --adapter-dir artifacts/llm/smollm2-caps-adapter \
  --report artifacts/llm/pedagogy_eval_report.json
```

Current smoke adapter result: `1/3` benchmark cases passed. This confirms the evaluation path works, but the adapter needs a longer run and more CAPS examples before it should be treated as production-quality.

Focused adapter evaluation after the 9-epoch CAPS run:

```bash
python scripts/validate_focused_adapter.py --skip-merge
```

This checks that the focused adapter is complete, writes
`artifacts/llm/focused_adapter_validation_manifest.json`, and runs the richer
benchmark file at `tests/fixtures/llm/focused_caps_eval.jsonl`.

To evaluate and merge in one pass for local app testing:

```bash
python scripts/validate_focused_adapter.py
```

## 6. Merge And Export

Dry-run the export metadata:

```bash
python scripts/merge_lora.py --dry-run --quantization gguf
```

Merge adapter weights into the base model:

```bash
python scripts/merge_lora.py \
  --model-id HuggingFaceTB/SmolLM2-360M-Instruct \
  --adapter-dir artifacts/llm/smollm2-caps-adapter \
  --output-dir artifacts/llm/merged-smollm2-caps-model
```

The merge helper writes Hugging Face format weights and `export_metadata.json`. GGUF/AWQ quantization should be performed in a dedicated export image with `llama.cpp` or AWQ tooling after the merged weights are produced.

Latest local smoke merge output: `artifacts/llm/merged-smollm2-caps-model`.

Focused merge output for app-level testing:

```bash
python scripts/merge_lora.py \
  --model-id HuggingFaceTB/SmolLM2-360M-Instruct \
  --adapter-dir artifacts/llm/smollm2-caps-focused-9epoch-adapter \
  --output-dir artifacts/llm/merged-smollm2-caps-focused-model \
  --torch-dtype float32
```

## 7. Wire The Focused Adapter Into The App For Testing

The FastAPI lesson `ExecutiveService` supports a development-only local Hugging
Face provider. Use it to test the focused adapter through the real lesson
generation path, including CAPS validation, Judiciary validation, caching, and
persistence.

For adapter loading:

```env
LLM_PROVIDER=local_hf
LOCAL_BASE_MODEL_ID=HuggingFaceTB/SmolLM2-360M-Instruct
LOCAL_ADAPTER_PATH=artifacts/llm/smollm2-caps-focused-9epoch-adapter
```

For merged-model loading:

```env
LLM_PROVIDER=local_hf
LOCAL_MERGED_MODEL_PATH=artifacts/llm/merged-smollm2-caps-focused-model
```

Then run the normal lesson generation route:

```text
POST /api/v2/lessons/generate
POST /api/v2/lessons/generate/stream
```

Keep `LLM_PROVIDER=auto` for normal provider fallback behavior.
