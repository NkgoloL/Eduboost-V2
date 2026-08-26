# Eduboost ETL MCP Server Architecture: Document Pipeline Exposed as AI-Callable Tools

This codemap covers the Eduboost ETL MCP server architecture, which exposes a 13-phase document processing pipeline (ingestion, extraction, normalization, chunking, quality validation, search, training data generation) as 20+ AI-callable tools via the Model Context Protocol. The system has three layers: MCP server wrappers (tools/etl/), core ETL pipeline (app/services/etl/), and FastAPI integration (app/api_v2_routers/). Key entry points: server startup [1c], document ingestion [2c], full pipeline execution [3b], training data generation [4b], full-text search [5b], and bulk operations [7c].

## Trace ID: 1
**Title:** MCP Server Startup and Pipeline Initialization

**Description:** Entry point for the MCP server that exposes ETL pipeline as tools; shows lazy singleton pattern for pipeline creation

**Trace text diagram:**
```
MCP Server Startup & Initialization
├── __main__ entry point <-- 1a
│   ├── argparse setup <-- 1b
│   │   └── transport: stdio | streamable-http <-- etl_mcp_server_v2.py:880
│   └── mcp.run(transport) <-- 1c
│       └── FastMCP server starts
│           └── waits for tool calls
│
└── First tool call triggers lazy init
    └── pipeline() singleton factory <-- 1d
        ├── EduboostETLv2 instantiation <-- 1e
        │   ├── db_url from ETL_DB_URL env <-- etl_mcp_server_v2.py:68
        │   └── storage_root from ETL_STORAGE env <-- etl_mcp_server_v2.py:69
        ├── init_db() <-- 1f
        │   └── CREATE TABLE IF NOT EXISTS... <-- etl_pipeline.py:494
        │       └── phases 0-12 schema <-- etl_pipeline_v2.py:78
        └── init_fts() <-- 1g
            └── CREATE VIRTUAL TABLE chunks_fts <-- etl_pipeline_v2.py:404
                └── FTS5 full-text search index
```

**Location ID: 1a**
**Title:** MCP Server Entry Point
**Description:** Main entry point for v2 server with 21 tools covering phases 1-12
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:878

**Location ID: 1b**
**Title:** Transport Configuration
**Description:** Supports stdio (Claude Desktop) or HTTP (remote clients)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:880

**Location ID: 1c**
**Title:** Server Execution
**Description:** Starts FastMCP server with configured transport
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:894

**Location ID: 1d**
**Title:** Lazy Pipeline Singleton
**Description:** Factory function that creates pipeline on first tool call
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:76

**Location ID: 1e**
**Title:** Pipeline Instantiation
**Description:** Creates v2 pipeline with SQLite database and file storage
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:80

**Location ID: 1f**
**Title:** Database Initialization
**Description:** Creates all tables for phases 0-12 in SQLite
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:81

**Location ID: 1g**
**Title:** FTS5 Index Setup
**Description:** Initializes full-text search virtual tables for phase 9
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:83

### AI Guide: MCP Server Startup and Pipeline Initialization

**Motivation:**
The MCP server startup and initialization pattern implements lazy singleton creation to defer expensive pipeline setup until the first tool call. This reduces startup time and memory usage when the server is idle. The server supports two transport modes: stdio for Claude Desktop integration and streamable-http for remote clients. The lazy initialization pattern ensures the SQLite database, file storage, and FTS5 full-text search index are only created when needed, improving resource efficiency during development and testing.

**Details:**

**Server Entry Point and Transport Configuration**
The __main__ entry point configures argument parsing for transport selection [1a]. Transport can be stdio (for Claude Desktop) or streamable-http (for remote clients) [1b]. The mcp.run(transport) call starts the FastMCP server which waits for tool calls from AI agents [1c]. This dual-transport support enables both local development (stdio) and remote deployment (HTTP) scenarios.

**Lazy Pipeline Singleton**
The pipeline() factory function implements lazy singleton pattern [1d]. The global _pipeline variable is None initially. On first tool call, the factory creates the EduboostETLv2 instance with db_url from ETL_DB_URL environment variable and storage_root from ETL_STORAGE environment variable [1e]. This defers expensive initialization until the first actual use, reducing startup overhead.

**Database and FTS5 Initialization**
Pipeline initialization calls init_db() to create all tables for phases 0-12 in SQLite [1f]. The schema includes tables for documents, chunks, quality checks, training examples, and audit trails. The init_fts() call creates FTS5 virtual tables for full-text search [1g]. FTS5 provides fast keyword search across document chunks. The try/except around init_fts() handles SQLite builds without FTS5 support gracefully.

## Trace ID: 2
**Title:** Document Ingestion via MCP Tool

**Description:** Phase 1 workflow: AI agent calls etl_ingest_document tool to register a new document in the pipeline

**Trace text diagram:**
```
MCP Tool: etl_ingest_document
├── FastMCP tool registration <-- 2a
├── async tool handler <-- 2b
│   ├── Pydantic input validation <-- etl_mcp_server_v2.py:286
│   └── pipeline().ingest() call <-- 2c
│       └── EduboostETL.ingest() in core pipeline <-- etl_pipeline.py:710
│           ├── SHA-256 checksum computation <-- 2d
│           ├── Duplicate detection check <-- etl_pipeline.py:726
│           ├── Copy to raw storage <-- 2e
│           ├── Create source record <-- etl_pipeline.py:752
│           └── Insert document record <-- 2f
└── JSON response to AI agent <-- 2g
```

**Location ID: 2a**
**Title:** MCP Tool Registration
**Description:** Decorator registers tool with FastMCP server
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:281

**Location ID: 2b**
**Title:** Tool Handler with Pydantic Validation
**Description:** Async function receives validated input from AI agent
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:286

**Location ID: 2c**
**Title:** Pipeline Ingest Call
**Description:** Delegates to core pipeline's ingest method
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:295

**Location ID: 2d**
**Title:** SHA-256 Duplicate Detection
**Description:** Computes file hash to prevent duplicate ingestion
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline.py:723

**Location ID: 2e**
**Title:** Immutable Raw Storage
**Description:** Copies file to phase 2 raw document storage
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline.py:745

**Location ID: 2f**
**Title:** Document Record Creation
**Description:** Inserts canonical document record with 'acquired' status
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline.py:780

**Location ID: 2g**
**Title:** JSON Response to Agent
**Description:** Returns document_id and next steps to AI agent
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:302

### AI Guide: Document Ingestion via MCP Tool

**Motivation:**
The etl_ingest_document tool enables AI agents to register new documents in the ETL pipeline. The tool uses Pydantic validation to ensure input correctness before processing. The core pipeline implements SHA-256 checksum computation for duplicate detection, preventing reprocessing of identical files. Documents are copied to immutable raw storage for provenance. The canonical document record is inserted with 'acquired' status, initiating the pipeline lifecycle. This phase establishes the foundation for all subsequent ETL processing.

**Details:**

**Tool Registration and Validation**
The @mcp.tool decorator registers etl_ingest_document with the FastMCP server [2a]. The async tool handler receives Pydantic-validated input from the AI agent [2b]. Pydantic validation ensures file_path exists, source_type is valid, and required fields are present. This prevents invalid data from reaching the core pipeline.

**Duplicate Detection and Raw Storage**
The pipeline().ingest() call delegates to the core pipeline's ingest method [2c]. SHA-256 checksum computation identifies duplicate files [2d]. If a document with the same checksum exists, ingestion is skipped. The file is copied to immutable raw storage (phase 2) to preserve the original [2e]. This ensures provenance and enables reprocessing if needed.

**Document Record Creation**
The canonical document record is inserted with document_id, checksum, source_type, and 'acquired' status [2f]. Source metadata (title, language, document_type) is stored for downstream processing. The JSON response returns document_id and next steps to the AI agent [2g]. This enables the agent to track document progress and trigger subsequent pipeline phases.

## Trace ID: 3
**Title:** Full Pipeline Execution: Extract → Normalize → Chunk → Validate

**Description:** Phases 3-7 workflow: AI agent runs complete ETL pipeline on an acquired document via etl_run_pipeline tool

**Trace text diagram:**
```
MCP Tool: etl_run_pipeline
├── Tool handler receives request <-- 3a
├── Delegate to core pipeline <-- 3b
│   └── EduboostETL.run_full_pipeline() <-- etl_pipeline.py:1384
│       ├── Phase 3: Extract text/structure <-- 3c
│       │   └── PyMuPDF/python-docx extraction <-- etl_pipeline.py:882
│       ├── Phase 4: Normalize text <-- 3d
│       │   └── Clean OCR artifacts, detect lang <-- etl_pipeline.py:1024
│       ├── Phase 5: Enrich metadata <-- etl_pipeline.py:1393
│       │   └── Infer grade/subject/curriculum <-- etl_pipeline.py:1087
│       ├── Phase 6: Chunk document <-- 3e
│       │   └── Type-aware segmentation <-- etl_pipeline.py:1165
│       └── Phase 7: Validate quality <-- 3f
│           ├── Compute 6-dimension scores <-- 3g
│           │   ├── metadata_score (20%) <-- etl_pipeline.py:1286
│           │   ├── extraction_score (20%) <-- etl_pipeline.py:1287
│           │   ├── structure_score (20%) <-- etl_pipeline.py:1288
│           │   ├── completeness_score (20%) <-- etl_pipeline.py:1289
│           │   ├── provenance_score (10%) <-- etl_pipeline.py:1290
│           │   └── training_suitability (10%) <-- etl_pipeline.py:1291
│           └── Determine status <-- etl_pipeline.py:1303
└── Return JSON response to agent <-- 3h
```

**Location ID: 3a**
**Title:** Pipeline Execution Tool
**Description:** MCP tool that runs all ETL stages sequentially
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:349

**Location ID: 3b**
**Title:** Delegate to Core Pipeline
**Description:** Calls v2 pipeline's orchestration method
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:356

**Location ID: 3c**
**Title:** Phase 3: Text Extraction
**Description:** Extracts text from PDF/DOCX/HTML using PyMuPDF or python-docx
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline.py:1387

**Location ID: 3d**
**Title:** Phase 4: Text Normalization
**Description:** Cleans OCR artifacts, normalizes whitespace, detects language
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline.py:1391

**Location ID: 3e**
**Title:** Phase 6: Document Chunking
**Description:** Segments document into retrieval-ready chunks by type
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline.py:1395

**Location ID: 3f**
**Title:** Phase 7: Quality Validation
**Description:** Computes 6-dimension quality score and flags issues
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline.py:1399

**Location ID: 3g**
**Title:** Quality Score Computation
**Description:** Weighted composite: metadata(20%) + extraction(20%) + structure(20%) + completeness(20%) + provenance(10%) + training(10%)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline.py:1310

**Location ID: 3h**
**Title:** Quality Report Response
**Description:** Returns quality check result and next steps to agent
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:357

### AI Guide: Full Pipeline Execution

**Motivation:**
The etl_run_pipeline tool enables AI agents to execute the complete ETL pipeline (phases 3-7) on an acquired document. This orchestration tool runs text extraction, normalization, metadata enrichment, chunking, and quality validation sequentially. The quality validation phase computes a 6-dimension composite score to determine document suitability for training data generation. This tool provides a one-call interface for end-to-end document processing, simplifying AI agent workflows.

**Details:**

**Pipeline Orchestration**
The tool handler receives the document_id and delegates to the core pipeline's run_full_pipeline method [3a, 3b]. This method orchestrates phases 3-7 sequentially, ensuring each phase completes before the next begins. The orchestration pattern provides error handling and status tracking across all phases.

**Text Extraction and Normalization**
Phase 3 extracts text and structure from PDF/DOCX/HTML using PyMuPDF or python-docx [3c]. Extraction preserves headings, tables, and document structure. Phase 4 normalizes text by cleaning OCR artifacts, normalizing whitespace, and detecting language [3d]. Normalization improves downstream processing quality and enables language-specific handling.

**Metadata Enrichment and Chunking**
Phase 5 enriches metadata by inferring grade, subject, and curriculum from document content [3e]. This enables curriculum-aligned content organization. Phase 6 chunks the document into retrieval-ready segments using type-aware segmentation [3f]. Chunking respects document structure (headings, sections) for better semantic coherence.

**Quality Validation**
Phase 7 computes a 6-dimension quality score: metadata_score (20%), extraction_score (20%), structure_score (20%), completeness_score (20%), provenance_score (10%), and training_suitability (10%) [3g]. The weighted composite determines document status (approved, needs_review, rejected). The JSON response returns the quality report and next steps to the agent [3h].

## Trace ID: 4
**Title:** Training Dataset Generation and Export

**Description:** Phase 10 workflow: AI agent generates QA pairs from approved documents and exports to JSONL/CSV/Parquet

**Trace text diagram:**
```
Training Dataset Generation & Export Flow
├── MCP Tool Layer (tools/etl/)
│   ├── etl_generate_training_data() <-- 4a
│   │   └── pipeline().generate_training_dataset() <-- 4b
│   └── etl_export_dataset() <-- 4e
│       └── pipeline().export_dataset() <-- 4f
│
└── Core Pipeline Layer (app/services/etl/)
    ├── generate_training_dataset() <-- etl_pipeline_v2.py:540
    │   ├── Load approved documents <-- etl_pipeline_v2.py:556
    │   ├── for chunk in chunks <-- 4c
    │   │   ├── Generate QA/summary/concept examples <-- etl_pipeline_v2.py:570
    │   │   └── INSERT INTO training_examples <-- 4d
    │   └── Return TrainingDataset object <-- etl_pipeline_v2.py:605
    │
    └── export_dataset() <-- etl_pipeline_v2.py:612
        ├── SELECT examples FROM training_examples <-- etl_pipeline_v2.py:640
        ├── Format conversion logic <-- etl_pipeline_v2.py:655
        └── with open(out_path, "w") as f <-- 4g
            └── Write JSONL/CSV/Parquet to disk <-- etl_pipeline_v2.py:675
```

**Location ID: 4a**
**Title:** Training Data Generation Tool
**Description:** MCP tool for creating synthetic training examples
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:666

**Location ID: 4b**
**Title:** Dataset Generation Call
**Description:** Creates dataset with specified example_type (qa/summary/concept/rubric)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:683

**Location ID: 4c**
**Title:** Chunk Iteration
**Description:** Iterates over approved document chunks to generate examples
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline_v2.py:565

**Location ID: 4d**
**Title:** Example Record Creation
**Description:** Stores input/output pairs with provenance metadata
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline_v2.py:590

**Location ID: 4e**
**Title:** Dataset Export Tool
**Description:** Exports training dataset to disk in specified format
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:728

**Location ID: 4f**
**Title:** Export Execution
**Description:** Writes JSONL/CSV/Parquet file to exports directory
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:740

**Location ID: 4g**
**Title:** JSONL File Writing
**Description:** Writes one JSON object per line for training frameworks
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline_v2.py:673

### AI Guide: Training Dataset Generation and Export

**Motivation:**
The training dataset generation and export tools enable AI agents to create synthetic training examples from approved documents. The etl_generate_training_data tool generates QA pairs, summaries, concepts, or rubrics from document chunks. The etl_export_dataset tool exports datasets to JSONL, CSV, or Parquet formats for use with ML training frameworks. This phase transforms curated documents into training-ready datasets with provenance metadata, enabling reproducible model training.

**Details:**

**Dataset Generation**
The etl_generate_training_data tool receives document_ids and example_type parameters [4a]. It delegates to pipeline().generate_training_dataset() which loads approved documents [4b]. The pipeline iterates over chunks from approved documents [4c]. For each chunk, it generates synthetic examples based on example_type (qa/summary/concept/rubric). Examples are inserted into the training_examples table with provenance metadata [4d]. The function returns a TrainingDataset object with dataset_id and metadata.

**Dataset Export**
The etl_export_dataset tool receives dataset_id and format parameters [4e]. It delegates to pipeline().export_dataset() which selects examples from the training_examples table [4f]. Format conversion logic transforms the data into JSONL, CSV, or Parquet format [4g]. The file is written to the exports directory. JSONL format writes one JSON object per line for compatibility with training frameworks like Hugging Face.

**Provenance and Reproducibility**
Training examples include provenance metadata (document_id, chunk_id, generated_at, model_version). This enables reproducibility and audit trails. The dataset_id serves as a unique identifier for the generated dataset. Export format selection provides flexibility for different training frameworks and workflows.

## Trace ID: 5
**Title:** Full-Text Search with FTS5 and Citation Building

**Description:** Phase 9 workflow: AI agent searches approved document chunks using FTS5 keyword search with citation metadata

**Trace text diagram:**
```
Full-Text Search with FTS5 and Citations
├── MCP Tool Layer (tools/etl/)
│   ├── @mcp.tool decorator registration <-- etl_mcp_server_v2.py:621
│   ├── etl_search_fulltext() handler <-- 5a
│   │   ├── Pydantic input validation <-- etl_mcp_server_v2.py:625
│   │   ├── pipeline().search_fulltext() call <-- 5b
│   │   ├── Content preview truncation <-- 5e
│   │   └── JSON response to agent <-- 5f
│   └── FastMCP server <-- etl_mcp_server_v2.py:72
└── ETL Pipeline Core (app/services/etl/)
    └── EduboostETLv2.search_fulltext() <-- etl_pipeline_v2.py:424
        ├── FTS5 query execution <-- 5c
        │   └── SELECT FROM chunks_fts MATCH <-- etl_pipeline_v2.py:437
        ├── Result iteration & ranking <-- etl_pipeline_v2.py:448
        ├── Citation object building <-- 5d
        │   ├── document_id <-- etl_pipeline_v2.py:455
        │   ├── title <-- etl_pipeline_v2.py:455
        │   ├── section_path <-- etl_pipeline_v2.py:455
        │   └── page numbers <-- etl_pipeline_v2.py:455
        └── Return hits with metadata <-- etl_pipeline_v2.py:461
```

**Location ID: 5a**
**Title:** Full-Text Search Tool
**Description:** MCP tool supporting FTS5 operators (AND, OR, NOT, phrase, prefix)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:625

**Location ID: 5b**
**Title:** Search Execution
**Description:** Delegates to pipeline's FTS5 search implementation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:641

**Location ID: 5c**
**Title:** FTS5 Query Execution
**Description:** Runs full-text search against virtual table with ranking
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline_v2.py:437

**Location ID: 5d**
**Title:** Citation Object Construction
**Description:** Builds citation metadata for AI response attribution
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/etl_pipeline_v2.py:455

**Location ID: 5e**
**Title:** Content Preview Truncation
**Description:** Limits response size by truncating full content
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:647

**Location ID: 5f**
**Title:** Search Results Response
**Description:** Returns ranked results with citations to AI agent
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v2.py:649

### AI Guide: Full-Text Search with FTS5 and Citations

**Motivation:**
The etl_search_fulltext tool enables AI agents to search approved document chunks using SQLite FTS5 full-text search. FTS5 provides fast keyword search with support for Boolean operators (AND, OR, NOT), phrase queries, and prefix searches. The tool builds citation metadata for each result, enabling AI response attribution. Content preview truncation limits response size for efficient transmission. This phase enables AI agents to retrieve relevant curriculum content for lesson generation and Q&A.

**Details:**

**FTS5 Search Execution**
The tool handler receives query parameters (query, grade, subject, document_type, limit) [5a]. It delegates to pipeline().search_fulltext() which executes FTS5 queries against the chunks_fts virtual table [5b, 5c]. FTS5 MATCH syntax supports Boolean operators, phrase queries, and prefix searches. Results are ranked by relevance using FTS5's built-in ranking algorithm.

**Citation Object Construction**
For each search result, the pipeline builds a citation object with document_id, title, section_path, and page numbers [5d]. This metadata enables AI agents to attribute responses to specific source documents. Citations support regulatory compliance and transparency requirements for AI-generated content.

**Response Optimization**
Content preview truncation limits the full content field to 300 characters to reduce response size [5e]. The JSON response returns ranked results with citations, query metadata, and result count to the AI agent [5f]. This optimization balances information richness with transmission efficiency.

## Trace ID: 6
**Title:** FastAPI Integration: Admin ETL Visibility Routes

**Description:** Separate system: FastAPI app provides read-only ETL visibility without importing MCP runtime dependencies

**Trace text diagram:**
```
FastAPI Admin ETL Integration
├── API Router Setup
│   ├── APIRouter registration <-- 6a
│   │   ├── /admin/etl/status endpoint <-- 6b
│   │   ├── /admin/etl/documents endpoint <-- 6c
│   │   └── Other read-only endpoints <-- admin_etl.py:37
│   └── EnvelopedRoute wrapper <-- admin_etl.py:6
│       └── require_admin() dependency <-- admin_etl.py:7
└── ETL Pipeline Factory
    ├── create_etl_pipeline() <-- 6d
    │   ├── Version selection dict <-- 6e
    │   └── Pipeline instantiation <-- 6f
    └── Pipeline classes
        ├── EduboostETL (v1) <-- factory.py:10
        ├── EduboostETLv2 (v2) <-- factory.py:11
        └── EduboostETLv3 (v3) <-- factory.py:12
```

**Location ID: 6a**
**Title:** Admin ETL Router Registration
**Description:** FastAPI router for read-only ETL visibility endpoints
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/admin_etl.py:9

**Location ID: 6b**
**Title:** ETL Status Endpoint
**Description:** Returns pipeline availability and document count
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/admin_etl.py:27

**Location ID: 6c**
**Title:** Document Registry Endpoint
**Description:** Lists all ETL documents with metadata
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/admin_etl.py:32

**Location ID: 6d**
**Title:** ETL Factory Function
**Description:** Factory pattern for creating pipeline instances without MCP dependencies
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/factory.py:17

**Location ID: 6e**
**Title:** Version Selection
**Description:** Selects pipeline class based on version parameter
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/factory.py:23

**Location ID: 6f**
**Title:** Pipeline Instantiation
**Description:** Creates pipeline instance for FastAPI integration
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/etl/factory.py:28

### AI Guide: FastAPI Admin ETL Integration

**Motivation:**
The FastAPI admin ETL integration provides read-only visibility into the ETL pipeline without importing MCP runtime dependencies. This separation prevents the FastAPI application from depending on MCP server libraries, reducing deployment complexity. The factory pattern enables version selection (v1, v2, v3) for backward compatibility. Admin-only routes with require_admin() dependency ensure secure access to ETL visibility endpoints.

**Details:**

**API Router Setup**
The APIRouter is registered with the FastAPI app using the /admin/etl prefix [6a]. Endpoints include /status (pipeline availability and document count) [6b], /documents (document registry with metadata) [6c], and other read-only endpoints. The EnvelopedRoute wrapper ensures consistent response formatting. The require_admin() dependency restricts access to admin users only.

**ETL Pipeline Factory**
The create_etl_pipeline() factory function creates pipeline instances without MCP dependencies [6d]. Version selection uses a dictionary mapping version strings to pipeline classes [6e]. Supported versions include EduboostETL (v1), EduboostETLv2 (v2), and EduboostETLv3 (v3). The factory instantiates the selected pipeline with db_url and storage_root parameters [6f].

**Separation of Concerns**
This FastAPI integration is a separate system from the MCP server. It provides HTTP-based visibility for admin dashboards and monitoring without requiring MCP runtime. The factory pattern enables version selection for backward compatibility and A/B testing. Admin-only security ensures ETL visibility is restricted to authorized users.

## Trace ID: 7
**Title:** V3 Additions: Bulk Operations and Advanced Dataset Management

**Description:** Extended MCP tools in v3: bulk review, dataset splitting, contamination checks, and audit trails

**Trace text diagram:**
```
V3 MCP Server Extensions
├── etl_mcp_server_v3_additions.py module
│   ├── Import v2 server singleton <-- 7a
│   ├── Bulk Review Operations
│   │   ├── @mcp.tool decorator <-- etl_mcp_server_v3_additions.py:216
│   │   ├── etl_bulk_review() handler <-- 7b
│   │   └── pipeline().bulk_review() call <-- 7c
│   ├── Dataset Management
│   │   ├── Split Dataset Tool
│   │   │   ├── etl_split_dataset() handler <-- 7d
│   │   │   └── pipeline().split_dataset() <-- 7e
│   │   └── Contamination Check Tool
│   │       ├── etl_check_contamination() <-- 7f
│   │       └── pipeline().check_contamination() <-- 7g
│   └── Audit Trail Tool
│       ├── etl_get_audit_trail() handler <-- 7h
│       └── pipeline().get_audit_trail() call <-- etl_mcp_server_v3_additions.py:181
└── EduboostETLv3 (etl_pipeline_v3_additions.py) <-- etl_pipeline_v3_additions.py:120
    ├── bulk_review() implementation <-- etl_pipeline_v3_additions.py:154
    ├── split_dataset() implementation <-- etl_pipeline_v3_additions.py:234
    ├── check_contamination() implementation <-- etl_pipeline_v3_additions.py:333
    └── get_audit_trail() implementation <-- etl_pipeline_v3_additions.py:126
```

**Location ID: 7a**
**Title:** V3 Extensions Import
**Description:** Reuses v2 server singleton to add 8 new tools
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v3_additions.py:49

**Location ID: 7b**
**Title:** Bulk Review Tool
**Description:** Approve or reject up to 200 documents in one call
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v3_additions.py:221

**Location ID: 7c**
**Title:** Bulk Operation Execution
**Description:** Processes multiple documents with partial failure handling
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v3_additions.py:232

**Location ID: 7d**
**Title:** Dataset Split Tool
**Description:** Splits training dataset into train/val/test subsets
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v3_additions.py:295

**Location ID: 7e**
**Title:** Deterministic Split Execution
**Description:** Uses hash-based shuffling for reproducible splits
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v3_additions.py:309

**Location ID: 7f**
**Title:** Contamination Check Tool
**Description:** Detects input_text overlap between train and test datasets
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v3_additions.py:324

**Location ID: 7g**
**Title:** SHA-256 Overlap Detection
**Description:** Uses hashing for exact-match contamination detection
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v3_additions.py:337

**Location ID: 7h**
**Title:** Audit Trail Tool
**Description:** Returns chronological history of all document changes
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tools/etl/etl_mcp_server_v3_additions.py:170

### AI Guide: V3 Additions - Bulk Operations and Advanced Dataset Management

**Motivation:**
The V3 extensions add 8 new MCP tools for bulk operations and advanced dataset management. Bulk review enables approving or rejecting up to 200 documents in one call, improving efficiency for large-scale content curation. Dataset splitting creates train/val/test subsets with deterministic shuffling for reproducible ML workflows. Contamination checking detects input_text overlap between train and test datasets to prevent data leakage. Audit trails provide chronological history of document changes for compliance and debugging.

**Details:**

**Bulk Review Operations**
The etl_bulk_review tool receives document_ids and action (approve/reject) parameters [7b]. It delegates to pipeline().bulk_review() which processes multiple documents with partial failure handling [7c]. Up to 200 documents can be processed in one call. Partial failures are reported in the response, enabling error recovery. This tool significantly improves efficiency for large-scale content curation workflows.

**Dataset Management**
The etl_split_dataset tool splits a training dataset into train/val/test subsets [7d]. It uses hash-based shuffling for deterministic, reproducible splits [7e]. The train/val/test ratios must sum to 1.0. The etl_check_contamination tool detects input_text overlap between train and test datasets using SHA-256 hashing [7f, 7g]. This prevents data leakage that would invalidate ML model evaluation.

**Audit Trail Tool**
The etl_get_audit_trail tool returns the chronological history of all document changes [7h]. The audit trail includes timestamps, actions, and user identifiers for each change. This enables compliance auditing, debugging, and reproducibility tracking. The EduboostETLv3 class implements these methods in etl_pipeline_v3_additions.py, extending the v2 pipeline with advanced capabilities.
