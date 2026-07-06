---
title: docs/DOC/* Documentation Suite vs. Actual EduBoost V2 Implementation
status: reference-record
owner: architecture
reviewers: [architecture, engineering, documentation-governance]
audience: architecture-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/codemaps, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# docs/DOC/* Documentation Suite vs. Actual EduBoost V2 Implementation

The docs/DOC/ directory contains a 37-document MIL-STD-498 suite describing a 'DBE AI Expert System' (Azure-based policy advisory with Gremlin knowledge graphs), which is architecturally distinct from the actual EduBoost V2 codebase (a South African learning platform with PostgreSQL, IRT diagnostics, and lesson generation). Key documentation entry points: [1a] tier structure, [2a] documented system requirements, [3a] actual system description, [4a] architectural mismatch.

## Trace ID: 1
**Title:** Documentation Suite Structure - 7-Tier MIL-STD-498 Organization

**Description:** Maps the hierarchical organization of the 37 documentation files across 7 tiers, from requirements through project management

**Trace text diagram:**
```
docs/DOC/ Documentation Suite Structure
├── Tier 1 - Requirements & Concept/ <-- DOC-01_System-Requirements-Specification_(SRS).md:1
│   └── DOC-01_SRS.md <-- 1a
│       └── System Requirements Specification
├── Tier 2 - Architecture & Design/ <-- DOC-08_Software-Architecture-Document_(SAD).md:1
│   └── DOC-08_SAD.md <-- 1b
│       └── C4 Model + Azure Infrastructure <-- DOC-08_Software-Architecture-Document_(SAD).md:9
├── Tier 3 - Implementation & Code/ <-- DOC-13_API-Reference.md:1
│   └── DOC-13_API-Reference.md <-- 1c
│       └── /ask and /feedback endpoints <-- DOC-13_API-Reference.md:27
├── Tier 4 - Testing & Quality Assurance/ <-- DOC-21_Software-Quality-Assurance-Plan_(SQAP).md:1
│   └── DOC-21_SQAP.md <-- 1d
│       └── QA processes + EduBoost V2 metrics <-- DOC-21_Software-Quality-Assurance-Plan_(SQAP).md:63
├── Tier 5 - Deployment & Operations/ <-- DOC-24_Deployment-Guide.md:1
│   └── (5 deployment documents)
├── Tier 6 - Security & Compliance/ <-- DOC-29_Security-Plan_(SecPlan).md:1
│   └── DOC-29_SecPlan.md <-- 1e
│       └── Azure Key Vault + APIM security <-- DOC-29_Security-Plan_(SecPlan).md:30
└── Tier 7 - Project Management/ <-- DOC-35_Project-Management-Plan_(PMP).md:1
    └── DOC-35_PMP.md <-- 1f
        └── 83 TODO items + 5 delivery phases <-- DOC-35_Project-Management-Plan_(PMP).md:39
```

**Location ID: 1a**
**Title:** Tier 1: Requirements & Concept - Entry Point
**Description:** Top-level requirements document defining the 'DBE AI Expert System' scope
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 1 - Requirements & Concept/DOC-01_System-Requirements-Specification_(SRS).md:1

**Location ID: 1b**
**Title:** Tier 2: Architecture & Design - System Structure
**Description:** Defines C4 model views and Azure-based deployment architecture
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 2 - Architecture & Design/DOC-08_Software-Architecture-Document_(SAD).md:1

**Location ID: 1c**
**Title:** Tier 3: Implementation & Code - API Contracts
**Description:** Documents /ask and /feedback endpoints for policy queries
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 3 - Implementation & Code/DOC-13_API-Reference.md:1

**Location ID: 1d**
**Title:** Tier 4: Testing & QA - Quality Standards
**Description:** Defines QA processes, but references EduBoost V2 metrics (82% coverage)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-21_Software-Quality-Assurance-Plan_(SQAP).md:1

**Location ID: 1e**
**Title:** Tier 6: Security & Compliance - POPIA Controls
**Description:** Security controls for Azure deployment with Key Vault and APIM
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 6 - Security & Compliance/DOC-29_Security-Plan_(SecPlan).md:1

**Location ID: 1f**
**Title:** Tier 7: Project Management - Scope Definition
**Description:** References 83 TODO items and 5 delivery phases for the documented system
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 7 - Project Management/DOC-35_Project-Management-Plan_(PMP).md:23

### AI Guide: Documentation Suite Structure - 7-Tier MIL-STD-498 Organization

**Motivation:**
The docs/DOC/ directory represents a comprehensive MIL-STD-498 documentation suite with 37 documents organized in 7 tiers. This structure follows military standard documentation practices with formal requirements, architecture, implementation, testing, deployment, security, and project management tiers. However, this documentation describes a completely different system than the actual EduBoost V2 codebase, creating a fundamental documentation-reality mismatch.

**Details:**

**Tier Organization Structure**
The documentation follows a hierarchical 7-tier structure [1a-1f]. Tier 1 contains requirements specifications (SRS, SSS, ConOps). Tier 2 covers architecture and design (SAD, SDD, IDD). Tier 3 details implementation and code (API Reference, Database Design). Tier 4 addresses testing and quality assurance (TP, TSR, SQAP). Tier 5 covers deployment and operations. Tier 6 handles security and compliance. Tier 7 manages project planning and processes.

**Formal Documentation Standards**
Each document follows MIL-STD-498 formatting with document IDs, version numbers, and formal section structure. The suite includes 37 documents covering all aspects of system development lifecycle. This comprehensive documentation approach suggests formal project management requirements, but the content doesn't match the actual implementation.

**Documentation Completeness**
The suite appears complete with documents covering all major development phases. However, the completeness masks the fundamental mismatch with reality. The documents reference components and architectures that don't exist in the codebase, creating a documentation facade.

**Project Management Integration**
Tier 7 documents reference actual EduBoost V2 TODO items and test results [1f]. This creates confusion by mixing real project artifacts with fictional system documentation. The project management documents appear to bridge the gap between documented and actual systems, but this creates inconsistent documentation.

## Trace ID: 2
**Title:** Documented DBE AI Expert System - Azure Knowledge Graph Architecture

**Description:** Traces the documented system architecture: a policy advisory platform using Cosmos DB Gremlin, Azure ML, and APIM gateway - components not present in actual codebase

**Trace text diagram:**
```
DBE AI Expert System Documentation
├── System Requirements (Tier 1)
│   ├── SRS defines DBE AI platform <-- 2a
│   ├── Knowledge graph requirement <-- 2b
│   └── Use case: policy queries <-- 2f
├── Architecture Design (Tier 2)
│   ├── Component: KnowledgeGraphManager <-- 2c
│   └── Infrastructure: Cosmos DB + Gremlin <-- 2e
└── API Specification (Tier 3)
    └── POST /ask endpoint for queries <-- 2d

Documented System Flow (not implemented):
Policy Analyst <-- DOC-01_System-Requirements-Specification_(SRS).md:116
└── submits query to /ask endpoint <-- 2d
    ├── KnowledgeGraphManager retrieves <-- 2c
    │   └── from Cosmos DB Gremlin API <-- 2e
    └── Expert Model generates response <-- DOC-01_System-Requirements-Specification_(SRS).md:160
        └── returns policy recommendation <-- 2f
```

**Location ID: 2a**
**Title:** System Purpose - Policy Advisory Platform
**Description:** Defines a system for educational policy queries, not learner education
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 1 - Requirements & Concept/DOC-01_System-Requirements-Specification_(SRS).md:47

**Location ID: 2b**
**Title:** Core Requirement - Gremlin Knowledge Graph
**Description:** Requires Cosmos DB Gremlin API for graph traversal
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 1 - Requirements & Concept/DOC-01_System-Requirements-Specification_(SRS).md:150

**Location ID: 2c**
**Title:** Key Component - KnowledgeGraphManager Class
**Description:** Documents a Gremlin client that doesn't exist in the codebase
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 2 - Architecture & Design/DOC-07_Software-Design-Document_(SDD).md:88

**Location ID: 2d**
**Title:** Primary Endpoint - Policy Query Interface
**Description:** Documents /ask endpoint for policy questions with expert model inference
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 3 - Implementation & Code/DOC-13_API-Reference.md:56

**Location ID: 2e**
**Title:** Infrastructure - Azure Cosmos DB Requirement
**Description:** Specifies Cosmos DB with Gremlin API, not PostgreSQL
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 2 - Architecture & Design/DOC-08_Software-Architecture-Document_(SAD).md:121

**Location ID: 2f**
**Title:** Use Case - Policy Query Scenario
**Description:** Example query about school infrastructure policy, not learner diagnostics
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 1 - Requirements & Concept/DOC-03_Concept-of-Operations_(ConOps).md:24

### AI Guide: Documented DBE AI Expert System - Azure Knowledge Graph Architecture

**Motivation:**
The documentation suite describes a "DBE AI Expert System" for educational policy advisory, completely different from the actual EduBoost V2 learning platform. This documented system uses Azure Cosmos DB with Gremlin API for knowledge graph management, Azure ML for expert models, and APIM for API gateway functionality. None of these components exist in the actual codebase, creating a complete architectural disconnect between documentation and reality.

**Details:**

**System Purpose Mismatch**
The documented system serves educational policy analysts, not learners [2a]. It processes natural language policy queries and returns expert recommendations. The actual EduBoost V2 system serves learners with diagnostic assessments and lesson generation. This represents a fundamental purpose mismatch between documented and actual systems.

**Knowledge Graph Architecture**
Documentation requires Cosmos DB with Gremlin API for graph traversal [2b, 2e]. The KnowledgeGraphManager component handles graph operations [2c]. The actual system uses PostgreSQL with relational schema, not graph databases. This represents a complete data architecture mismatch.

**API Interface Differences**
Documented system provides /ask endpoint for policy queries [2d]. The API reference shows Gremlin client usage for graph operations. Actual system provides FastAPI endpoints for learner management, diagnostics, and content generation. This represents completely different API contracts.

**Infrastructure Stack Contrast**
Documentation specifies Azure infrastructure: Cosmos DB, Azure ML, AKS, APIM [2e]. Actual system uses PostgreSQL, Redis, and containerized FastAPI. This represents completely different technology stacks and deployment patterns.

**Use Case Scenarios**
Documentation describes policy analyst querying school infrastructure requirements [2f]. Actual system supports learners taking diagnostic assessments and receiving personalized lessons. This represents completely different user workflows and value propositions.

## Trace ID: 3
**Title:** Actual EduBoost V2 Implementation - Learning Platform Architecture

**Description:** Contrasts the actual codebase: a FastAPI learning platform with PostgreSQL, IRT diagnostics, lesson generation, and POPIA compliance - completely different from documented system

**Trace text diagram:**
```
EduBoost V2 Actual Implementation
├── Project Root
│   ├── README.md
│   │   ├── System description <-- 3a
│   │   ├── Active entrypoint declaration <-- 3b
│   │   └── Launch content status <-- 3d
│   └── docs/
│       ├── current_state.md
│       │   └── Architecture summary <-- 3c
│       └── TODO.md
│           └── Test baseline status <-- 3e
└── app/
    └── api_v2.py (FastAPI entrypoint) <-- api_v2.py:1
        ├── PostgreSQL + Redis stack <-- docker-compose.yml:15
        ├── IRT diagnostic engine <-- irt_engine.py:1
        ├── Lesson generation modules <-- lesson_generator.py:1
        └── POPIA compliance layer <-- popia.py:1
```

**Location ID: 3a**
**Title:** Actual System Purpose - Learning Platform
**Description:** Real system is for learner education, not policy advisory
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/README.md:8

**Location ID: 3b**
**Title:** Actual Entrypoint - FastAPI V2 Runtime
**Description:** Real implementation uses FastAPI, not Azure APIM gateway
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/README.md:15

**Location ID: 3c**
**Title:** Architecture Summary - PostgreSQL + Redis Stack
**Description:** Uses PostgreSQL and Redis, not Cosmos DB or Gremlin
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/current_state.md:68

**Location ID: 3d**
**Title:** Actual Features - IRT Diagnostics & Lessons
**Description:** Real system generates lessons and diagnostics, not policy recommendations
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/README.md:31

**Location ID: 3e**
**Title:** Actual Test Status - 1702 Passing Tests
**Description:** Real codebase has extensive test coverage for learning platform features
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/TODO.md:26

### AI Guide: Actual EduBoost V2 Implementation - Learning Platform Architecture

**Motivation:**
The actual EduBoost V2 implementation is a comprehensive learning platform for South African primary education. It uses FastAPI with PostgreSQL and Redis, implements IRT diagnostic assessments, generates CAPS-aligned lessons, and includes POPIA compliance features. This represents a complete, working system that is entirely different from the documented "DBE AI Expert System" in the docs/DOC/ directory.

**Details:**

**Learning Platform Purpose**
The actual system serves South African primary education with diagnostic assessments and personalized learning [3a]. It focuses on learner progress through CAPS-aligned curriculum. This contrasts sharply with the documented policy advisory system for educational administrators.

**FastAPI Architecture**
The system uses FastAPI as the primary web framework [3b]. The active entrypoint is app/api_v2.py with comprehensive API endpoints. This represents a modern Python web architecture, completely different from the documented Azure-based system.

**PostgreSQL + Redis Stack**
The actual system uses PostgreSQL for relational data and Redis for caching [3c]. This represents a traditional web application stack. The documented system requires Cosmos DB with Gremlin API, which doesn't exist in the actual implementation.

**IRT Diagnostic Engine**
The system implements Item Response Theory for adaptive diagnostics [3d]. This provides personalized assessment capabilities. The documented system focuses on policy query processing, completely different functionality.

**Lesson Generation System**
The actual system includes CAPS-aligned lesson generation capabilities [3d]. This supports personalized learning content delivery. The documented system has no equivalent functionality, focusing instead on policy document retrieval.

**Comprehensive Test Coverage**
The actual system has 1702 passing tests covering all major functionality [3e]. This represents a well-tested, production-ready system. The documented system references test results but doesn't have corresponding implementation.

## Trace ID: 4
**Title:** Documentation-Reality Mismatch - Architectural Disconnect

**Description:** Highlights the fundamental disconnect: DOC/ describes Azure ML + Gremlin system while codebase implements PostgreSQL + IRT learning platform

**Trace text diagram:**
```
docs/DOC/ Documentation Suite
├── Tier 1-7 Structure (37 documents)
│   ├── SSS references graph_manager.py <-- 4a
│   ├── API docs show Gremlin usage <-- 4b
│   └── Deployment guide runs graph_manager <-- 4f
│
├── Naming Confusion Layer
│   ├── Test Plan mentions "EduBoost V2" <-- 4c
│   └── Test Summary reports EduBoost tests <-- 4d
│
├── POPIA Assessment for DBE system <-- 4e
│
└── Reality: Actual Codebase <-- README.md:8
    ├── No src/ingestion/ directory exists
    ├── No graph_manager.py exists
    ├── No Cosmos DB / Gremlin implementation
    ├── No Azure ML integration
    └── Instead: PostgreSQL + FastAPI + IRT <-- current_state.md:68
        └── 1702 passing tests for learning <-- TODO.md:26
```

**Location ID: 4a**
**Title:** Documented Component - KnowledgeGraphManager
**Description:** References src/ingestion/graph_manager.py which doesn't exist
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 1 - Requirements & Concept/DOC-02_System-Subsystem-Specification_(SSS).md:82

**Location ID: 4b**
**Title:** Documented API - Gremlin Client Usage
**Description:** Shows API for component that has zero implementation in codebase
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 3 - Implementation & Code/DOC-13_API-Reference.md:164

**Location ID: 4c**
**Title:** Naming Confusion - EduBoost V2 Reference
**Description:** Test plan mentions EduBoost V2 but in context of DBE system docs
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-15_Test-Plan_(TP).md:5

**Location ID: 4d**
**Title:** Mixed References - EduBoost Tests in DBE Docs
**Description:** References actual EduBoost test results within DBE system documentation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-20_Test-Summary-Report_(TSR).md:5

**Location ID: 4e**
**Title:** POPIA Compliance - For Documented System
**Description:** POPIA assessment for DBE system, while actual EduBoost has separate POPIA implementation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 6 - Security & Compliance/DOC-31_Privacy-Impact-Assessment_(PIA).md:12

**Location ID: 4f**
**Title:** Deployment Instructions - For Non-existent Code
**Description:** Deployment guide references Python modules that don't exist in repository
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/DOC/Tier 5 - Deployment & Operations/DOC-24_Deployment-Guide.md:73

### AI Guide: Documentation-Reality Mismatch - Architectural Disconnect

**Motivation:**
The fundamental issue is a complete architectural disconnect between the documented system and actual implementation. The docs/DOC/ directory describes a "DBE AI Expert System" with Azure components and Gremlin knowledge graphs, while the actual codebase implements a PostgreSQL-based learning platform. This creates confusion, maintenance challenges, and potential misalignment of project goals.

**Details:**

**Non-Existent Components**
Documentation references components that don't exist in the codebase [4a]. The src/ingestion/graph_manager.py file is documented but completely absent. API documentation shows Gremlin client usage for non-existent components [4b]. This represents a complete documentation-reality disconnect.

**Naming and Identity Confusion**
Test documents reference "EduBoost V2" but in the context of the DBE system [4c]. Test summary reports include actual EduBoost test results within DBE system documentation [4d]. This creates confusion about which system is being documented and tested.

**POPIA Compliance Mismatch**
POPIA assessment documents cover the documented DBE system [4e]. However, the actual EduBoost V2 implementation has its own separate POPIA compliance layer. This creates duplicate and potentially conflicting compliance documentation.

**Deployment Guide Disconnect**
Deployment instructions reference Python modules and Azure components that don't exist [4f]. The actual deployment uses Docker Compose with PostgreSQL and Redis. This creates completely different deployment patterns and operational procedures.

**Architectural Implications**
The documented Azure-based architecture (Cosmos DB, Gremlin, Azure ML) has zero implementation in the actual codebase. The actual PostgreSQL + FastAPI + IRT architecture has no corresponding documentation. This represents a complete architectural documentation failure that could impact project understanding, maintenance, and future development.
