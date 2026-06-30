# Phase 2R Gate 2R.3 Implementation Note

**Gate:** 2R.3  
**Scope:** Extraction, page/section provenance, structure-aware chunk proposals, and extraction quality warnings.  
**Status after package application:** Implementation present; closure not established.

## Implemented controls

- Deterministic text-fixture extraction for fast tests.
- Native PDF extraction adapter using `pypdf` where installed.
- Page-level text hashes, language, confidence, warnings, and provenance metadata.
- Section records derived from chunk structure with page ranges.
- Chunk proposals with text hashes, page ranges, language, quality score, warnings, and paragraph metadata.
- Detection warnings for low-density pages, arithmetic/formula-like text, table-like aligned rows, and source-embedded prompt-injection phrases.
- Real-source extraction CLI for the controlled Grade 4-6 Mathematics CAPS source.
- Gate 2R.3 verifier with optional real-source extraction.

## Boundaries

This implementation does **not**:

- approve extraction review decisions;
- create curriculum mappings;
- build or freeze corpus manifests;
- update retrieval projections;
- activate production retrieval;
- authorise Gate 2R.4.

Gate 2R.4 remains blocked until Gate 2R.3 candidate evidence, approval, and a separate transition commit exist.
