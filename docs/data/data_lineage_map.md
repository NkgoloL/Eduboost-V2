# Data Lineage Map across Derived Stores (TSR-7.2)

## Architectural Data Flow
```
[Client / API Gateway]
        │
        ├── Auth / Session Context ──> [PostgreSQL: secure_tokens, guardians]
        │
        ├── Learner Diagnostics ──────> [PostgreSQL: diagnostic_sessions, topic_mastery]
        │                                      │
        │                                      ▼
        │                              [Runtime KG: learner_kg_node_states]
        │
        ├── Content Generation ───────> [Content Factory: runs, tasks, artifacts]
        │                                      │
        │                                      ▼
        │                              [Vector Retrieval: retrieval_source_chunks]
        │
        └── Audit Events ─────────────> [PostgreSQL: audit_events (Chained Hash HMAC)]
```

## Derived Data Stores & Lifecycle
1. **PostgreSQL Primary Database:** Authoritative state for all domain entities.
2. **Vector Chunks (pgvector):** Derived semantic embeddings for CAPS grounding.
3. **Runtime Knowledge Graph:** Graph projections of curriculum masteries.
4. **Audit Chain:** Append-only cryptographic trail of all security and consent events.
