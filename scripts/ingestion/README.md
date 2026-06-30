# EduBoost SA — Web Ingestion System

> **Curriculum data pipeline** for Grades 1–12, CAPS-aligned.  
> Scrapes global educational platforms and South African government resources, normalises content, maps it to the CAPS framework, and produces fine-tuning-ready JSONL training records.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Directory Structure](#directory-structure)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Scraper Sources](#scraper-sources)
6. [Pipeline Stages](#pipeline-stages)
7. [API Reference](#api-reference)
8. [CLI Reference](#cli-reference)
9. [Queue System](#queue-system)
10. [Database Schema](#database-schema)
11. [Training Data Formats](#training-data-formats)
12. [Adding a New Source](#adding-a-new-source)
13. [Import Map & Bug Fixes](#import-map--bug-fixes)
14. [Legal & Licensing](#legal--licensing)
15. [Deployment Notes](#deployment-notes)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EduBoost SA Ingestion System                 │
├───────────────┬─────────────────────────────────────────────────────┤
│  HTTP / CLI   │  POST /api/ingestion/jobs  OR  python -m main run   │
├───────────────┴──────────────┬──────────────────────────────────────┤
│         Queue Manager        │  Redis FIFO list  (ingestion:queue)  │
│         (queue_manager.py)   │  Progress hashes  (ingestion:prog:*) │
├──────────────────────────────┴──────────────────────────────────────┤
│                        run_ingestion()  (main.py)                   │
│                        ▼ for each source_id                         │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    sources/  (scrapers)                        │ │
│  │  KhanAcademy  OpenStax  CK-12  BBCBitesize  CommonLit          │ │
│  │  LibreTexts   Siyavula  DBE    WCED   HuggingFace              │ │
│  │  All extend BaseScraper — robots-compliant, rate-limited       │ │
│  └────────────────────────────┬───────────────────────────────────┘ │
│                               │  RawContent (Pydantic)               │
│  ┌────────────────────────────▼───────────────────────────────────┐ │
│  │               pipeline/  (processing stages)                   │ │
│  │  Stage 1: normaliser.py      → NormalisedContent               │ │
│  │  Stage 2: caps_aligner.py    → (CAPS fields enriched)          │ │
│  │  Stage 3: training_formatter → TrainingRecord (system/user/ass)│ │
│  │  Stage 4: storage.py         → PostgreSQL  +  JSONL export     │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Data flow

```
Source website / API
       │
       │ HTTP (aiohttp / Playwright)
       ▼
  RawContent           ← raw HTML, JSON, or plain text; one record per content item
       │
       │ normalise()
       ▼
  NormalisedContent    ← clean text, subject/grade inferred, content-type classified
       │
       │ align()
       ▼
  NormalisedContent    ← CAPS phase/subject/topic_code/learning_outcome enriched
       │
       │ format_record()
       ▼
  TrainingRecord       ← system / user / assistant triplet
       │
       ├─ PostgreSQL (all three tables)
       └─ JSONL export (OpenAI or Anthropic format)
```

---

## Directory Structure

```
scripts/ingestion/
├── __init__.py               Package root; imports & version
├── config.py                 Source registry, CAPS taxonomy, KA→CAPS maps
├── models.py                 Pydantic schemas: RawContent, NormalisedContent,
│                             TrainingRecord, IngestionJob, CurriculumStandard
├── main.py                   ★ CLI entry point + run_ingestion() coroutine
├── api.py                    ★ FastAPI router — mount in your main app
├── queue_manager.py          ★ Redis FIFO queue + progress tracking
│
├── utils/
│   ├── __init__.py
│   ├── rate_limiter.py       Async token-bucket rate limiter (shared global)
│   └── robots_checker.py     robots.txt compliance checker (cached per domain)
│
├── sources/
│   ├── __init__.py           ★ SCRAPER_REGISTRY + get_scraper() factory
│   ├── base.py               Abstract BaseScraper (session, retry, Playwright)
│   ├── khan_academy.py       KA topic-tree API scraper
│   ├── openstax.py           OpenStax books API scraper
│   ├── ck12.py               CK-12 subject/concept scraper
│   ├── bbc_bitesize.py       BBC Bitesize (Playwright, UK curriculum)
│   ├── commonlit.py          CommonLit ELA passage scraper
│   ├── libretexts.py         LibreTexts STEM textbook scraper
│   ├── siyavula.py           Siyavula ZA open textbooks (Gr 7–12)
│   ├── dbe_south_africa.py   DBE Mind the Gap + CAPS documents
│   ├── wced.py               Western Cape Education Department
│   └── huggingface_datasets.py  HF dataset loader (ARC, MMLU, GSM8K …)
│
└── pipeline/
    ├── __init__.py           ★ Pipeline class + stage re-exports
    ├── normaliser.py         Stage 1: HTML strip, Unicode, dedup, classify
    ├── caps_aligner.py       Stage 2: CAPS taxonomy enrichment cascade
    ├── training_formatter.py Stage 3: system/user/assistant template engine
    └── storage.py            Stage 4: async SQLAlchemy 2.0 persistence
```

★ = new file created in this PR

---

## Quick Start

### 1. Install dependencies

```bash
# Core
pip install aiohttp aiofiles pydantic sqlalchemy asyncpg aiosqlite \
            beautifulsoup4 lxml redis typer langdetect

# For BBC Bitesize (JS-heavy)
pip install playwright && playwright install chromium

# For HuggingFace datasets
pip install datasets huggingface_hub
```

### 2. Set environment variables

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/eduboost"
export REDIS_URL="redis://localhost:6379/0"
export EXPORT_DIR="data/exports"         # optional JSONL export path
```

### 3. Run from CLI

```bash
# Scrape all CAPS-aligned ZA sources, grades 10–12
python -m scripts.ingestion.main run --sources za --grades 10-12

# Scrape Khan Academy maths, grades 7–9, cap at 500 items
python -m scripts.ingestion.main run --sources khan_academy --grades 7-9 --limit 500

# Dry-run (no DB writes)
python -m scripts.ingestion.main run --sources siyavula --dry-run

# List all sources
python -m scripts.ingestion.main sources

# Show queue depth
python -m scripts.ingestion.main status
```

### 4. Use the Python API

```python
import asyncio
from scripts.ingestion.main import run_ingestion

async def main():
    stats = await run_ingestion(
        source_ids=["siyavula", "dbe", "khan_academy"],
        grade_range=(4, 9),
        limit=1000,
        db_url="postgresql+asyncpg://localhost/eduboost",
        export_dir="data/exports",
    )
    print(stats)

asyncio.run(main())
```

### 5. Mount the FastAPI router

```python
# In your main FastAPI app (e.g. app/main.py)
from fastapi import FastAPI
from scripts.ingestion.api import router as ingestion_router

app = FastAPI()
app.include_router(ingestion_router)
# → endpoints available at /api/ingestion/*
```

---

## Configuration

### `config.py` — Key constants

| Symbol | Description |
|---|---|
| `SOURCES` | `dict[str, SourceConfig]` — all scraper source definitions |
| `HF_DATASETS` | `list[dict]` — HuggingFace open dataset catalogue |
| `KA_TOPIC_TO_CAPS` | Khan Academy slug → CAPS mapping |
| `CC_TO_CAPS` | Common Core standard prefix → CAPS mapping |
| `SUBJECT_NORMALISATION` | International subject name → CAPS canonical name |
| `CAPS_MATHS_TOPICS` | CAPS Maths topic codes by phase |
| `CAPS_SCIENCE_TOPICS` | CAPS Science topic codes by phase |
| `GRADE_TO_PHASE` | `{grade: CAPSPhase}` lookup |
| `REDIS_QUEUE_KEY` | Redis list key for the job queue |
| `REDIS_PROGRESS_KEY` | Redis hash key template for job progress |
| `RAW_TABLE` | PostgreSQL table for raw content |
| `CONTENT_TABLE` | PostgreSQL table for normalised content |

### `SourceConfig` fields

```python
SourceConfig(
    id             = "siyavula",
    name           = "Siyavula Open Textbooks",
    base_url       = "https://www.siyavula.com",
    rate_limit_rps = 0.5,            # requests per second
    robots_txt_url = "...",
    license        = "CC BY 4.0",
    jurisdiction   = "za",           # "global" | "za" | "uk" | "us"
    grade_range    = (7, 12),
    requires_playwright = False,
    enabled        = True,
    extra          = { ... }         # source-specific extras
)
```

---

## Scraper Sources

| Source ID | Name | Jurisdiction | Grades | License | Playwright |
|---|---|---|---|---|---|
| `khan_academy` | Khan Academy | Global | 1–12 | CC BY-NC-SA 4.0 | No |
| `openstax` | OpenStax | Global | 6–12 | CC BY 4.0 | No |
| `ck12` | CK-12 Foundation | Global | 1–12 | CC BY-NC 3.0 | No |
| `bbc_bitesize` | BBC Bitesize | UK | 1–12 | BBC Educational | **Yes** |
| `commonlit` | CommonLit | US | 3–12 | CC BY-NC-SA 4.0 | No |
| `libretexts` | LibreTexts | Global | 9–12 | CC BY 4.0 | No |
| `siyavula` | Siyavula Open Textbooks | ZA | 7–12 | CC BY 4.0 | No |
| `dbe` | DBE South Africa | ZA | 1–12 | Gov Open License | No |
| `wced` | Western Cape Education Dept. | ZA | 1–12 | Gov Open License | No |
| `huggingface` | HuggingFace Datasets | Global | 1–12 | Various | No |

### HuggingFace Datasets Included

| Dataset | HF ID | Grades | Subjects |
|---|---|---|---|
| ARC | `allenai/ai2_arc` | 3–9 | Natural Sciences |
| MMLU | `cais/mmlu` | 9–12 | Multi |
| SciQ | `sciq` | 4–9 | Natural Sciences |
| OpenBookQA | `allenai/openbookqa` | 4–8 | Natural Sciences |
| GSM8K | `openai/gsm8k` | 3–8 | Mathematics |
| MATH | `lighteval/MATH` | 7–12 | Mathematics |
| RACE | `ehovy/race` | 6–12 | English |
| SQuAD | `rajpurkar/squad` | 6–12 | English |
| AfriQA | `masakhane/afriqa` | 4–12 | Multi (ZUL/XHO/AFR) |
| NCHLT | `nchlt` | 1–12 | SA Languages |

---

## Pipeline Stages

### Stage 1 — Normaliser (`pipeline/normaliser.py`)

- Strips HTML tags (BeautifulSoup)
- Unicode NFKC normalisation
- SHA-256 deduplication (in-memory per run, cross-run via DB)
- Subject normalisation via `SUBJECT_NORMALISATION` lookup
- Grade inference from metadata / title keywords
- Content-type classification (MCQ, article, textbook, etc.)
- Difficulty inference from grade and content markers
- Language detection (langdetect)

### Stage 2 — CAPS Aligner (`pipeline/caps_aligner.py`)

Alignment cascade (first match wins):

1. Source-declared `caps_*` fields already present → validate and pass through
2. KA topic slug → `KA_TOPIC_TO_CAPS` lookup
3. Common Core standard prefix → `CC_TO_CAPS` lookup
4. Subject + grade → `CAPS_MATHS_TOPICS` / `CAPS_SCIENCE_TOPICS`
5. Keyword heuristics on title / body text
6. Default: mark phase only, no topic code

Output fields enriched: `caps_phase`, `caps_subject`, `caps_topic_code`, `caps_learning_outcome`, `caps_content_item_code`.

### Stage 3 — Training Formatter (`pipeline/training_formatter.py`)

Converts `NormalisedContent` → `TrainingRecord` using content-type templates:

| Content Type | Template Strategy |
|---|---|
| `assessment_item` | MCQ with options → answer with justification |
| `worked_example` | Step-by-step solution walkthrough |
| `textbook_section` | Conceptual explanation / Socratic tutoring |
| `reading_passage` | Comprehension and inference |
| `curriculum_standard` | Learning-goal articulation |
| `lesson` / default | Socratic teaching dialogue |

System prompt is always the CAPS-aligned EduBoostAI persona.

Output formats: `to_openai_format()` and `to_anthropic_format()`.

### Stage 4 — Storage (`pipeline/storage.py`)

- Async SQLAlchemy 2.0 with `asyncpg` (PostgreSQL) or `aiosqlite` (dev)
- Upsert via `ON CONFLICT DO UPDATE` — idempotent re-runs
- Batch writes (configurable chunk size, default 200)
- JSONB columns for variable metadata
- Tables: `ingestion_raw`, `curriculum_content`, `training_records`, `ingestion_jobs`, `curriculum_standards`

---

## API Reference

Base path: `/api/ingestion`

### Sources

| Method | Path | Description |
|---|---|---|
| `GET` | `/sources` | List all available scraper sources with metadata |
| `GET` | `/datasets` | List HuggingFace dataset catalogue |

### Jobs

| Method | Path | Description |
|---|---|---|
| `POST` | `/jobs` | Create and enqueue an ingestion job → 202 |
| `GET` | `/jobs?n=20` | List queued jobs (head of queue) |
| `GET` | `/jobs/{id}` | Get job metadata by ID |
| `POST` | `/jobs/{id}/cancel` | Request cooperative cancellation |
| `GET` | `/jobs/{id}/progress` | Live progress snapshot (pct, scraped, ETA) |

### Pipeline

| Method | Path | Description |
|---|---|---|
| `POST` | `/pipeline/run` | Run pipeline in background (dev/small batches) |

### System

| Method | Path | Description |
|---|---|---|
| `GET` | `/stats` | Queue depth, source counts, dataset counts |
| `GET` | `/health` | Health check (Redis connectivity) |

### Example: Create a job

```bash
curl -X POST http://localhost:8000/api/ingestion/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "siyavula",
    "grade_min": 10,
    "grade_max": 12,
    "limit": 500,
    "dry_run": false
  }'
```

```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "source_id": "siyavula",
  "status": "pending",
  "queued_at": "2026-06-05T09:00:00Z",
  "message": "Job queued. Monitor at /api/ingestion/jobs/3fa85f64.../progress"
}
```

---

## CLI Reference

```
python -m scripts.ingestion.main [COMMAND] [OPTIONS]
```

### `run` — execute the pipeline

| Option | Default | Description |
|---|---|---|
| `--sources`, `-s` | `all` | Comma-separated source IDs, or aliases `za`, `open`, `all` |
| `--grades`, `-g` | `1-12` | Grade range as `min-max` |
| `--limit`, `-l` | `0` (∞) | Max items per source |
| `--db` | `$DATABASE_URL` | SQLAlchemy async DB URL |
| `--redis` | `redis://localhost:6379` | Redis URL |
| `--export` | (none) | Directory to write training JSONL files |
| `--dry-run` | false | Parse but skip writes |
| `--verbose`, `-v` | false | Debug logging |

### `sources` — list sources

```bash
python -m scripts.ingestion.main sources
# khan_academy                   global   grades 1-12  CC BY-NC-SA 4.0
# siyavula                       za       grades 7-12  CC BY 4.0
# ...
```

### `status` — queue info

```bash
python -m scripts.ingestion.main status --redis redis://localhost:6379
# Queue depth: 3
# Next jobs:
#   a1b2c3d4 — source=siyavula
```

### `datasets` — HuggingFace catalogue

```bash
python -m scripts.ingestion.main datasets
```

---

## Queue System

The `QueueManager` uses two Redis data structures:

```
ingestion:queue           → Redis LIST (RPUSH to enqueue, BLPOP to dequeue)
ingestion:job:<id>        → Redis HASH (job payload + status metadata)
ingestion:prog:<id>       → Redis HASH (live progress: pct, scraped, eta_secs)
ingestion:cancelled       → Redis SET  (job IDs flagged for cancellation)
```

### Worker pattern

```python
from scripts.ingestion.queue_manager import QueueManager
from scripts.ingestion.main import run_ingestion

async def worker(redis_url: str) -> None:
    async with QueueManager(redis_url) as qm:
        while True:
            job = await qm.dequeue(timeout=5)
            if not job:
                continue

            cfg = job.config
            try:
                stats = await run_ingestion(
                    source_ids=[job.source_id],
                    grade_range=tuple(cfg.get("grade_range", [1, 12])),
                    limit=cfg.get("limit", 0),
                    dry_run=cfg.get("dry_run", False),
                    redis_url=redis_url,
                    job_id=job.id,
                )
                await qm.complete_job(job.id, stats=stats)
            except Exception as exc:
                await qm.complete_job(job.id, status=JobStatus.FAILED)
```

---

## Database Schema

```sql
-- Stage 1: raw scrape output
CREATE TABLE ingestion_raw (
    id                  VARCHAR(36) PRIMARY KEY,
    source_id           VARCHAR(64) NOT NULL,
    source_url          TEXT,
    source_internal_id  VARCHAR(256),
    raw_text            TEXT NOT NULL,
    raw_html            TEXT,
    raw_json            JSONB,
    metadata            JSONB,
    scraped_at          TIMESTAMP,
    license             VARCHAR(128),
    language            VARCHAR(8),
    processed           BOOLEAN DEFAULT FALSE
);

-- Stage 2–3: normalised + CAPS-aligned content
CREATE TABLE curriculum_content (
    id                      VARCHAR(36) PRIMARY KEY,
    source_id               VARCHAR(64) NOT NULL,
    subject                 VARCHAR(64),
    grade                   SMALLINT,
    topic                   VARCHAR(256),
    content_type            VARCHAR(32),
    title                   TEXT,
    body                    TEXT,
    caps_phase              VARCHAR(16),
    caps_subject            VARCHAR(64),
    caps_topic_code         VARCHAR(8),
    caps_learning_outcome   TEXT,
    caps_content_item_code  VARCHAR(32),
    language                VARCHAR(8),
    jurisdiction            VARCHAR(16),
    license                 VARCHAR(128),
    confidence_score        FLOAT,
    ingested_at             TIMESTAMP
);

-- Stage 4: training records
CREATE TABLE training_records (
    id              VARCHAR(36) PRIMARY KEY,
    source_id       VARCHAR(64),
    caps_code       VARCHAR(32),
    grade           SMALLINT,
    subject         VARCHAR(64),
    content_type    VARCHAR(32),
    system          TEXT,
    user            TEXT,
    assistant       TEXT,
    difficulty      VARCHAR(32),
    jurisdiction    VARCHAR(16),
    language        VARCHAR(8),
    license         VARCHAR(128),
    tags            JSONB
);
```

---

## Training Data Formats

### OpenAI fine-tuning JSONL

```json
{
  "messages": [
    {"role": "system",    "content": "You are EduBoostAI, an expert South African tutor..."},
    {"role": "user",      "content": "Grade 10 Mathematics: Solve for x: 2x² + 5x - 3 = 0"},
    {"role": "assistant", "content": "Step 1: Use the quadratic formula..."}
  ]
}
```

### Anthropic fine-tuning JSONL

```json
{
  "system": "You are EduBoostAI...",
  "messages": [
    {"role": "user",      "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

---

## Adding a New Source

1. **Add the source config** to `config.py`:

```python
SOURCES["my_source"] = SourceConfig(
    id             = "my_source",
    name           = "My Educational Source",
    base_url       = "https://example.com",
    rate_limit_rps = 0.5,
    robots_txt_url = "https://example.com/robots.txt",
    license        = "CC BY 4.0",
    grade_range    = (1, 12),
)
```

2. **Create the scraper** at `sources/my_source.py`:

```python
from __future__ import annotations
from typing import AsyncIterator
from scripts.ingestion.config import SOURCES
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

class MySourceScraper(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(config=SOURCES["my_source"], **kwargs)

    async def scrape(self) -> AsyncIterator[RawContent]:
        data = await self._get("https://example.com/api/content")
        for item in data.get("items", []):
            yield RawContent(
                source_id  = "my_source",
                source_url = item["url"],
                raw_text   = item["text"],
                metadata   = {"grade": item.get("grade"), "subject": item.get("subject")},
                license    = "CC BY 4.0",
            )
```

3. **Register it** in `sources/__init__.py`:

```python
from scripts.ingestion.sources.my_source import MySourceScraper

SCRAPER_REGISTRY["my_source"] = MySourceScraper
```

That's it — the scraper is now available in the CLI, API, and `run_ingestion()`.

---

## Import Map & Bug Fixes

### Import structure (correct)

```
scripts.ingestion
  ├── .config          → SOURCES, KA_TOPIC_TO_CAPS, CC_TO_CAPS, ...
  ├── .models          → RawContent, NormalisedContent, TrainingRecord, ...
  ├── .main            → run_ingestion()
  ├── .api             → FastAPI router
  ├── .queue_manager   → QueueManager
  ├── .utils.rate_limiter    → throttle()
  ├── .utils.robots_checker  → can_fetch()
  ├── .sources.base          → BaseScraper
  ├── .sources.khan_academy  → KhanAcademyScraper
  │   ... (all other scrapers)
  ├── .pipeline.normaliser   → normalise()
  ├── .pipeline.caps_aligner → align()
  ├── .pipeline.training_formatter → format_record()
  └── .pipeline.storage      → StorageLayer
```

### Bug fixed: `khan_academy.py`

```python
# ❌ WRONG (original)
from scripts.ingestion.config import SOURCES, KA_TO_CAPS_MATHS

# ✅ FIXED
from scripts.ingestion.config import SOURCES, KA_TOPIC_TO_CAPS
```

The mapping table in `config.py` is named `KA_TOPIC_TO_CAPS`. The scraper body has also been updated so all three occurrences use the correct name.

### Relocated files

The flat structure has been reorganised into subpackages:

| Original location | New location |
|---|---|
| `base.py` | `sources/base.py` |
| `rate_limiter.py` | `utils/rate_limiter.py` |
| `robots_checker.py` | `utils/robots_checker.py` |
| `normaliser.py` | `pipeline/normaliser.py` |
| `caps_aligner.py` | `pipeline/caps_aligner.py` |
| `training_formatter.py` | `pipeline/training_formatter.py` |
| `storage.py` | `pipeline/storage.py` |
| `bbc_bitesize.py`, `ck12.py`, etc. | `sources/` |

All existing imports in those files already use the fully-qualified `scripts.ingestion.*` paths, so they work without modification after relocation.

---

## Legal & Licensing

| Source | License | Commercial use | Training data use |
|---|---|---|---|
| Khan Academy | CC BY-NC-SA 4.0 | ✗ | ✓ (non-commercial) |
| OpenStax | CC BY 4.0 | ✓ | ✓ |
| CK-12 | CC BY-NC 3.0 | ✗ | ✓ (non-commercial) |
| BBC Bitesize | BBC Educational | ✗ | Check per-item |
| CommonLit | CC BY-NC-SA 4.0 | ✗ | ✓ (non-commercial) |
| LibreTexts | CC BY 4.0 | ✓ | ✓ |
| Siyavula | CC BY 4.0 | ✓ | ✓ |
| DBE / WCED | Gov Open License (ZA) | ✓ (ZA govt) | ✓ |
| ARC, GSM8K, MATH | MIT / Apache 2.0 | ✓ | ✓ |
| AfriQA | Apache 2.0 | ✓ | ✓ |

**Always respect `robots.txt`** — the `RobotsChecker` utility enforces this automatically. The scraper's `User-Agent` is set to identify EduBoost SA and provide a contact URL.

---

## Deployment Notes

### Docker Compose snippet

```yaml
services:
  ingestion-worker:
    build: .
    command: python -m scripts.ingestion.main run --sources all --grades 1-12
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:pass@db:5432/eduboost
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: eduboost
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7-alpine
```

### Scaling

- Run multiple `ingestion-worker` containers — each blocks on `BRPOP` and picks up the next job
- Each worker runs one source at a time (sequential within source, concurrent within scrape)
- The global `RateLimiter` singleton is **per-process** — if you run multiple workers on the same source simultaneously, multiply the effective RPS accordingly

### Monitoring

```bash
# Queue depth
redis-cli llen ingestion:queue

# Progress for a specific job
redis-cli hgetall "ingestion:prog:<job_id>"

# API health check
curl http://localhost:8000/api/ingestion/health
```
