"""
EduBoost SA — Web Ingestion System  v2.0
=========================================
Curriculum data ingestion pipeline for Grades 1–12, CAPS-aligned.

Package layout::

    scripts/ingestion/
    ├── config.py           — source registry, CAPS taxonomy, HF catalogue
    ├── models.py           — Pydantic data models (Raw → Normalised → Training)
    ├── main.py             — CLI entry point + run_ingestion() coroutine
    ├── api.py              — FastAPI router (mount in the main app)
    ├── queue_manager.py    — Redis-backed async job queue
    ├── utils/
    │   ├── rate_limiter.py — async token-bucket rate limiter
    │   └── robots_checker.py — robots.txt compliance
    ├── sources/
    │   ├── base.py             — abstract BaseScraper
    │   ├── khan_academy.py
    │   ├── openstax.py
    │   ├── ck12.py
    │   ├── bbc_bitesize.py
    │   ├── commonlit.py
    │   ├── libretexts.py
    │   ├── siyavula.py
    │   ├── dbe_south_africa.py
    │   ├── wced.py
    │   └── huggingface_datasets.py
    └── pipeline/
        ├── normaliser.py       — Stage 1: clean + classify
        ├── caps_aligner.py     — Stage 2: CAPS taxonomy enrichment
        ├── training_formatter.py — Stage 3: → TrainingRecord JSONL
        └── storage.py          — Stage 4: async PostgreSQL persistence

Quickstart (Python API)::

    from scripts.ingestion.main import run_ingestion
    stats = await run_ingestion(source_ids=["siyavula", "dbe"], grade_range=(10, 12))

Quickstart (CLI)::

    python -m scripts.ingestion.main run --sources siyavula,dbe --grades 10-12
    python -m scripts.ingestion.main sources    # list all sources
    python -m scripts.ingestion.main status     # queue depth

Mount the API in FastAPI::

    from scripts.ingestion.api import router as ingestion_router
    app.include_router(ingestion_router)
"""
from scripts.ingestion.config import CAPSPhase, CAPSSubject, HF_DATASETS, SOURCES
from scripts.ingestion.models import (
    IngestionJob,
    JobStatus,
    NormalisedContent,
    RawContent,
    TrainingRecord,
)

__all__ = [
    # Config
    "SOURCES",
    "HF_DATASETS",
    "CAPSPhase",
    "CAPSSubject",
    # Models
    "RawContent",
    "NormalisedContent",
    "TrainingRecord",
    "IngestionJob",
    "JobStatus",
]

__version__ = "2.0.0"
