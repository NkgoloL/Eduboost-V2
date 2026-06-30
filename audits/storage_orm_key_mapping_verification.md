# Storage Layer: ORM Key Mapping Verification
**Date:** 2026-06-05  
**Status:** ✓ FIXED - All serializers use ORM attribute names (SQLAlchemy contract)

## Problem Summary
The ingestion pipeline had a mismatch between Pydantic models (API domain), ORM models (SQLAlchemy), and database column names. Serializers must use ORM attribute names, not database column names.

## Resolution
Updated all serializer functions to use ORM attribute names, which SQLAlchemy correctly maps to database column names via the `Column("db_name")` declarations.

---

## 1. RawContent → RawContentRow

| **Pydantic Model** | **ORM Attribute** | **DB Column** | **Serializer** |
|---|---|---|---|
| `metadata` | `metadata_` | `metadata` | `"metadata_": r.metadata` ✓ |
| All others | Same name | Same name | Mapped correctly ✓ |

**Serializer:** `_raw_to_row(r: RawContent) → dict[str, Any]`
```python
def _raw_to_row(r: RawContent) -> dict[str, Any]:
    return {
        "id":                 r.id,
        "source_id":          r.source_id,
        "source_url":         r.source_url,
        "source_internal_id": r.source_internal_id,
        "raw_text":           r.raw_text,
        "raw_html":           r.raw_html,
        "raw_json":           r.raw_json,
        "metadata_":          r.metadata,          # ← ORM attribute name
        "scraped_at":         r.scraped_at,
        "license":            r.license,
        "language":           r.language,
        "processed":          r.processed,
    }
```

**Upsert Call:**
```python
async def upsert_raw_batch(items: list[RawContent], batch_size: int = _DEFAULT_BATCH) -> int:
    for chunk in _chunks(items, batch_size):
        rows = [_raw_to_row(r) for r in chunk]  # ← Uses serializer
        stmt = pg_insert(RawContentRow).values(rows)
```

---

## 2. TrainingRecord → TrainingRecordRow

| **Pydantic Model** | **ORM Attribute** | **DB Column** | **Serializer** |
|---|---|---|---|
| `user` | `user_msg` | `user` | `"user_msg": t.user` ✓ |
| `assistant` | `assistant` | `assistant` | `"assistant": t.assistant` ✓ |
| All others | Same name | Same name | Mapped correctly ✓ |

**ORM Definition:**
```python
class TrainingRecordRow(Base):
    __tablename__ = "training_records"
    
    id            = Column(String(36), primary_key=True)
    source_id     = Column(String(64), index=True)
    caps_code     = Column(String(32))
    grade         = Column(Integer,   index=True)
    subject       = Column(String(64))
    content_type  = Column(String(32))
    system        = Column(Text)
    user_msg      = Column("user", Text, nullable=False)      # ← DB column is "user"
    assistant     = Column(Text, nullable=False)
    difficulty    = Column(String(32))
    jurisdiction  = Column(String(16))
    language      = Column(String(8))
    license       = Column(String(128))
    tags          = Column(JSONB)
```

**Serializer:**
```python
def _training_to_row(t: TrainingRecord) -> dict[str, Any]:
    return {
        "id":           t.id,
        "source_id":    t.source_id,
        "caps_code":    t.caps_code,
        "grade":        t.grade,
        "subject":      t.subject,
        "content_type": t.content_type.value,
        "system":       t.system,
        "user_msg":     t.user,              # ← ORM attribute name
        "assistant":    t.assistant,
        "difficulty":   t.difficulty.value if t.difficulty else None,
        "jurisdiction": t.jurisdiction,
        "language":     t.language,
        "license":      t.license,
        "tags":         t.tags,
    }
```

**Upsert Call:**
```python
async def upsert_training_batch(records: list[TrainingRecord], batch_size: int = _DEFAULT_BATCH) -> int:
    for chunk in _chunks(records, batch_size):
        rows = [_training_to_row(t) for t in chunk]  # ← Uses serializer
        stmt = pg_insert(TrainingRecordRow).values(rows)
```

---

## 3. NormalisedContent → NormalisedContentRow

| **Pydantic Model** | **ORM Attribute** | **DB Column** | **Serializer** |
|---|---|---|---|
| All fields | Same name | Same name | Direct mapping ✓ |

**Serializer:**
```python
def _norm_to_row(n: NormalisedContent) -> dict[str, Any]:
    return {
        "id":                     n.id,
        "source_id":              n.source_id,
        "source_url":             n.source_url,
        "source_internal_id":     n.source_internal_id,
        "subject":                n.subject,
        "grade":                  n.grade,
        "topic":                  n.topic,
        "subtopic":               n.subtopic,
        "content_type":           n.content_type.value,
        "difficulty":             n.difficulty.value if n.difficulty else None,
        "title":                  n.title,
        "body":                   n.body,
        "body_html":              n.body_html,
        "answer":                 n.answer,
        "options":                n.options,
        "explanation":            n.explanation,
        "caps_phase":             n.caps_phase,
        "caps_subject":           n.caps_subject,
        "caps_topic_code":        n.caps_topic_code,
        "caps_learning_outcome":  n.caps_learning_outcome,
        "caps_content_item_code": n.caps_content_item_code,
        "language":               n.language,
        "jurisdiction":           n.jurisdiction,
        "license":                n.license,
        "ingested_at":            n.ingested_at,
        "confidence_score":       n.confidence_score,
        "extra":                  n.extra,
    }
```

---

## SQLAlchemy Key Contract

**Rule:** When calling `.values(row_dict)` on an ORM insert statement, keys MUST be ORM attribute names.

SQLAlchemy automatically maps ORM attribute names to database column names via:
```python
metadata_ = Column("metadata", JSONB, default=dict)
#         ↑                ↑
#       ORM attr     DB column name
```

When the insert values dict has `"metadata_"`, SQLAlchemy resolves it to:
- ORM attribute: `RawContentRow.metadata_`
- Database column: `metadata`

---

## Verification Checklist

- [x] `_raw_to_row()` uses `"metadata_"` (ORM attribute) not `"metadata"`
- [x] `_training_to_row()` uses `"user_msg"` (ORM attribute) not `"user"`
- [x] All serializers are used in upsert functions
- [x] All upsert functions call `.values(row_dict)` with ORM attribute names
- [x] README.md schema documentation updated to match actual columns
- [x] No read-back deserialization (data flows forward only)

---

## Files Modified

1. **[scripts/ingestion/pipeline/storage.py](scripts/ingestion/pipeline/storage.py)**
   - ✓ `_raw_to_row()` — uses `"metadata_"` 
   - ✓ `_training_to_row()` — uses `"user_msg"`
   - ✓ `_norm_to_row()` — direct mapping
   - ✓ `upsert_raw_batch()` — calls `_raw_to_row()`
   - ✓ `upsert_content_batch()` — calls `_norm_to_row()`
   - ✓ `upsert_training_batch()` — calls `_training_to_row()`

2. **[scripts/ingestion/README.md](scripts/ingestion/README.md)**
   - ✓ Updated training_records schema: `user_turn` → `user`, `assistant_turn` → `assistant`
   - ✓ Added missing columns: `difficulty`, `jurisdiction`

---

## Key Takeaway

The ORM key mismatch is **completely resolved**. All serializer functions correctly map Pydantic model fields to ORM attribute names, which SQLAlchemy then transparently maps to database column names. This is the correct SQLAlchemy contract.

**No runtime issues expected.** Data ingestion will work correctly with ORM → DB column mapping fully enforced.
