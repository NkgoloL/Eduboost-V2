# EduBoost V2: LLM Brain Integration Roadmap

This roadmap outlines the systematic integration of **DeepSeek v4 (via Hugging Face)** into the EduBoost V2 platform. The goal is to replace the current static fallback data with a fine-tuned, intelligent LLM that acts as the core "brain" of the application, specifically trained on the South African CAPS (Curriculum and Assessment Policy Statement) scope.

## Phase 1: Infrastructure & Inference Setup

1. **[ ] Provision GPU Infrastructure**
   - Identify and provision suitable GPU infrastructure (AWS EC2) capable of handling the VRAM requirements for DeepSeek v4 (either quantized or full-precision).
2. **[ ] Set Up Hugging Face Ecosystem**
   - Authenticate with Hugging Face (`huggingface-cli login`).
   - Install required dependencies: `transformers`, `accelerate`, `peft`, `bitsandbytes` (for quantization), and `trl`.
3. **[ ] Deploy Inference Server**
   - Set up an optimized inference engine like **vLLM** or **Text Generation Inference (TGI)** to serve the base DeepSeek v4 model.
   - Expose the model via an OpenAI-compatible REST API.
4. **[ ] Initial EduBoost Connection**
   - Update `app/core/config.py` and `.env` to point the `INFERENCE_SERVICE_URL` to the new local/hosted DeepSeek v4 endpoint.
   - Verify basic connectivity between the EduBoost FastAPI backend and the model.

## Phase 2: CAPS Dataset Curation & Preparation

5. **[ ] Scrape Department of Education Website**
   - Write a scraping pipeline using `Playwright` and `BeautifulSoup`.
   - Target `education.gov.za` to systematically download all official PDF/text documents for the South African CAPS curriculum, focusing on Primary Education (Grade R-7) subjects.
6. **[ ] Data Storage Strategy**
   - Store the raw scraped PDFs in the existing Cloudflare R2 bucket (`eduboost-assets`) to minimize costs.
   - During fine-tuning, sync these files to the EC2 instance's local high-speed EBS volume (200GB+).
7. **[ ] Extract and Clean Data**
   - Process the curriculum documents to extract learning outcomes, topics, assessment criteria, and pedagogical guidelines.
7. **[ ] Construct Instruction-Tuning Dataset**
   - Format the extracted data into an instruction-response JSONL format suitable for LLM fine-tuning.
   - Example format: `{"instruction": "Generate a Grade 4 Mathematics lesson on fractions according to CAPS guidelines.", "output": "..."}`
8. **[ ] Create Pedagogical Guardrails Dataset**
   - Add examples of *incorrect* pedagogical approaches with corrections to teach the model what *not* to do (e.g., avoiding high-school level vocabulary for a Grade 3 lesson).

## Phase 3: Fine-Tuning DeepSeek v4

9. **[ ] Configure QLoRA Training Pipeline**
   - Set up a Parameter-Efficient Fine-Tuning (PEFT) pipeline using QLoRA to reduce VRAM usage while retaining the model's reasoning capabilities.
10. **[ ] Execute Fine-Tuning**
    - Train the DeepSeek v4 model on the CAPS instruction dataset.
    - Monitor training loss and validate against a held-out set of CAPS test questions.
11. **[ ] Evaluate Pedagogical Accuracy**
    - Run the fine-tuned adapter through a suite of domain-specific benchmarks (e.g., asking it to map a topic to a CAPS term and grade).
12. **[ ] Merge and Quantize**
    - Merge the LoRA weights back into the base model.
    - Export the finalized model (optionally quantized to AWQ or GGUF for faster, cheaper inference).

## Phase 4: Application Integration ("The Brain")

13. **[ ] Update the EduBoost V2 Orchestrator**
    - Modify the V2 service layer (`app/services/lesson_service.py`, `study_plan_service.py`) to fully route through the fine-tuned DeepSeek model.
    - Remove hardcoded fallbacks and mock data.
14. **[ ] Implement Streaming Responses**
    - Update the backend to support Server-Sent Events (SSE) streaming for LLM responses so the frontend UI feels responsive while generating lessons.
15. **[ ] Context Injection (RAG Setup)**
    - Implement a lightweight Retrieval-Augmented Generation (RAG) pipeline to inject specific Learner Profile context (mastery level, past scores) into the prompt alongside the CAPS instructions.
16. **[ ] Judiciary Pillar Validation**
    - Ensure all outputs from the fine-tuned DeepSeek model pass through the `JudiciaryStamp` compliance gates (checking for appropriate language, POPIA compliance, and content safety).

## Phase 5: Testing and Deployment

17. **[ ] End-to-End Brain Testing**
    - Run the Playwright E2E tests (`study_plan_and_lesson.spec.ts`, `diagnostic.spec.ts`) against the live LLM to ensure the model generates properly formatted JSON responses matching the API contracts.
18. **[ ] Performance & Latency Optimization**
    - Benchmark the Time-To-First-Token (TTFT) and overall token generation speed.
    - Adjust vLLM batching parameters or quantization levels if latency exceeds UX budgets (target: < 2 seconds TTFT).
19. **[ ] Production Rollout**
    - Deploy the final inference container alongside the EduBoost Docker stack.
    - Update `docker-compose.yml` to include the LLM service natively if running on a single heavy node, or document the external endpoint configuration.
