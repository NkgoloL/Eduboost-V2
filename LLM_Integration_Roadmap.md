# EduBoost V2: LLM Brain Integration Roadmap

This roadmap outlines the systematic integration of **DeepSeek v4 (via Hugging Face)** into the EduBoost V2 platform. The goal is to replace the current static fallback data with a fine-tuned, intelligent LLM that acts as the core "brain" of the application, specifically trained on the South African CAPS (Curriculum and Assessment Policy Statement) scope.

## Phase 1: Infrastructure & Inference Setup

1. **[blocked] Provision GPU Infrastructure** [ACCOUNT RESTRICTED TO FREE TIER]
   - Identify and provision suitable GPU infrastructure (AWS EC2) capable of handling the VRAM requirements for DeepSeek v4.
2. **[x] Set Up Hugging Face Ecosystem**
   - Authenticate with Hugging Face (`huggingface-cli login`). [DONE]
   - Install required dependencies: `transformers`, `accelerate`, `peft`, `bitsandbytes`, and `trl`. [DONE]
3. **[blocked] Deploy Inference Server**
   - Set up an optimized inference engine like **vLLM** or **Text Generation Inference (TGI)** to serve the base DeepSeek v4 model.
   - Expose the model via an OpenAI-compatible REST API.
4. **[/] Initial EduBoost Connection**
   - Update `app/core/config.py` and `.env` to point the `INFERENCE_SERVICE_URL` to the new endpoint. [DONE]
   - Verify basic connectivity between the EduBoost FastAPI backend and the model. [PENDING INFRASTRUCTURE]

## Phase 2: CAPS Dataset Curation & Preparation

5. **[x] Scrape Department of Education Website** [DONE]
   - Write a scraping pipeline using `Playwright` and `BeautifulSoup`.
   - Target `education.gov.za` to systematically download all official PDF/text documents for the South African CAPS curriculum, focusing on Primary Education (Grade R-7) subjects.
6. **[x] Data Storage Strategy** [DONE]
   - Store the raw scraped PDFs in the existing Cloudflare R2 bucket (`eduboost-assets`) to minimize costs.
   - During fine-tuning, sync these files to the EC2 instance's local high-speed EBS volume (200GB+).
7. **[x] Extract and Clean Data** [DONE]
   - Process the curriculum documents to extract learning outcomes, topics, assessment criteria, and pedagogical guidelines.
8. **[x] Construct Instruction-Tuning Dataset** [DONE]
   - Format the extracted data into an instruction-response JSONL format suitable for LLM fine-tuning.
   - Example format: `{"instruction": "Generate a Grade 4 Mathematics lesson on fractions according to CAPS guidelines.", "output": "..."}`
8. **[x] Create Pedagogical Guardrails Dataset** [DONE]
   - Add examples of *incorrect* pedagogical approaches with corrections to teach the model what *not* to do (e.g., avoiding high-school level vocabulary for a Grade 3 lesson).

## Phase 3: Fine-Tuning SmolLM2 Now, DeepSeek v4 Later

9. **[x] Configure CPU LoRA / GPU QLoRA Training Pipeline** [DONE]
   - Set up a Parameter-Efficient Fine-Tuning (PEFT) pipeline using QLoRA to reduce VRAM usage while retaining the model's reasoning capabilities.
10. **[/] Execute Fine-Tuning** [CPU SMOLLM2 SMOKE RUN DONE; GPU DEEPSEEK BLOCKED]
    - Trained a CPU LoRA proof adapter for SmolLM2-360M-Instruct and saved local artifacts under `artifacts/llm/smollm2-caps-adapter`.
    - Train DeepSeek v4 on GPU later when infrastructure is available.
    - Monitor training loss and validate against a held-out set of CAPS test questions.
11. **[/] Evaluate Pedagogical Accuracy** [HARNESS DONE; QUALITY NEEDS LONGER TRAINING]
    - Run the fine-tuned adapter through a suite of domain-specific benchmarks (e.g., asking it to map a topic to a CAPS term and grade).
    - Current CPU smoke adapter passes 1/3 lightweight benchmark cases; it proves the pipeline, not final pedagogy quality.
12. **[x] Merge and Quantize** [MERGE/EXPORT HELPER DONE]
    - Merge the LoRA weights back into the base model.
    - Export the finalized model (optionally quantized to AWQ or GGUF for faster, cheaper inference).
    - CPU smoke adapter was merged locally to `artifacts/llm/merged-smollm2-caps-model`; GGUF/AWQ conversion still belongs in a dedicated export image.

## Phase 4: Application Integration ("The Brain")

13. **[x] Update the EduBoost V2 Orchestrator**
    - Lesson generation routes through `ExecutiveService`, provider fallback, cache, and the local SmolLM2/DeepSeek-compatible prompt path.
    - Hardcoded local lesson content remains only as a non-production provider-failure fallback.
14. **[x] Implement Streaming Responses**
    - Added `POST /api/v2/lessons/generate/stream` with Server-Sent Events for accepted/result/done/error updates.
15. **[x] Context Injection (RAG Setup)**
    - Lesson generation now injects lightweight learner context from unresolved knowledge gaps and recent lessons into the LLM prompt.
16. **[x] Judiciary Pillar Validation**
    - Lesson outputs continue through `JudiciaryService.stamp_lesson(...)` schema and policy validation before persistence.

## Phase 5: Testing and Deployment

17. **[x] End-to-End Brain Testing**
    - Run the Playwright E2E tests (`study_plan_and_lesson.spec.ts`, `diagnostic.spec.ts`) against the live LLM to ensure the model generates properly formatted JSON responses matching the API contracts.
    - Added a critical learner smoke test that covers the V2 frontend/backend journey against the configured LLM/fallback path.
18. **[/] Performance & Latency Optimization**
    - Benchmark the Time-To-First-Token (TTFT) and overall token generation speed.
    - Adjust vLLM batching parameters or quantization levels if latency exceeds UX budgets (target: < 2 seconds TTFT).
    - CPU smoke training and merge are complete; production TTFT tuning remains blocked until GPU inference infrastructure exists.
19. **[blocked] Production Rollout**
    - Deploy the final inference container alongside the EduBoost Docker stack.
    - Update `docker-compose.yml` to include the LLM service natively if running on a single heavy node, or document the external endpoint configuration.
    - Blocked by GPU/provider infrastructure and production model quality.
