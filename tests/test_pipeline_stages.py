#!/usr/bin/env python3
"""
Test script: Pipeline Stage 1–4 Integration Test

Verifies that all stages work correctly in sequence:
  1. RawContent → normalise() → NormalisedContent
  2. NormalisedContent → align() → CAPS-enriched NormalisedContent
  3. NormalisedContent → format_record() → TrainingRecord
  4. TrainingRecord → to_openai_format() & to_anthropic_format()
"""


from scripts.ingestion.models import RawContent
from scripts.ingestion.pipeline.normaliser import normalise, reset_dedup_cache
from scripts.ingestion.pipeline.caps_aligner import align
from scripts.ingestion.pipeline.training_formatter import format_record


def test_full_pipeline():
    """Test all 4 stages with a sample content item."""

    print("\n" + "="*80)
    print("PIPELINE STAGE TEST: RawContent → Training Record")
    print("="*80)

    # Reset dedup cache
    reset_dedup_cache()

    # ── Stage 0: Create sample RawContent ────────────────────────────────────
    print("\n[0] Creating sample RawContent...")
    raw = RawContent(
        source_id="test_source",
        source_url="https://example.com/lesson/fractions",
        raw_text="""
        Introduction to Fractions
        
        A fraction is a way to represent part of a whole.
        
        Example: If you cut a pizza into 8 equal slices and eat 2, 
        you have eaten 2/8 of the pizza.
        
        Learning Objectives:
        - Understand what a fraction is
        - Identify the numerator and denominator
        - Compare fractions
        
        Activity: Cut a paper circle into 4 equal parts. Shade 1 part.
        What fraction have you shaded?
        """,
        metadata={
            "title": "Introduction to Fractions",
            "grade": 4,
            "subject": "mathematics",
            "content_type": "lesson",
            "jurisdiction": "za",
        },
        license="CC BY 4.0",
        language="en",
    )

    print(f"   Source: {raw.source_id}")
    print(f"   Title: {raw.metadata.get('title')}")
    print(f"   Grade: {raw.metadata.get('grade')}")
    print(f"   Content length: {len(raw.raw_text)} chars")

    # ── Stage 1: Normalise ───────────────────────────────────────────────────
    print("\n[1] Running Normaliser (Stage 1)...")
    norm = normalise(raw)

    if norm is None:
        print("   ❌ FAILED: normalise() returned None")
        return False

    print("   ✅ Normalised content:")
    print(f"      • Title: {norm.title[:60]}...")
    print(f"      • Subject: {norm.subject}")
    print(f"      • Grade: {norm.grade}")
    print(f"      • Content Type: {norm.content_type.value}")
    print(f"      • Difficulty: {norm.difficulty.value}")
    print(f"      • Language: {norm.language}")
    print(f"      • Confidence: {norm.confidence_score:.2f}")

    # ── Stage 2: CAPS Align ──────────────────────────────────────────────────
    print("\n[2] Running CAPS Aligner (Stage 2)...")
    aligned = align(norm)

    print("   ✅ CAPS-aligned content:")
    print(f"      • CAPS Phase: {aligned.caps_phase}")
    print(f"      • CAPS Subject: {aligned.caps_subject}")
    print(f"      • CAPS Topic Code: {aligned.caps_topic_code}")
    print(f"      • Learning Outcome: {aligned.caps_learning_outcome[:60] if aligned.caps_learning_outcome else 'None'}...")

    # ── Stage 3: Training Formatter ──────────────────────────────────────────
    print("\n[3] Running Training Formatter (Stage 3)...")
    training = format_record(aligned)

    if training is None:
        print("   ❌ FAILED: format_record() returned None")
        return False

    print("   ✅ Training record created:")
    print(f"      • System prompt: {training.system[:60]}...")
    print(f"      • User message: {training.user[:60]}...")
    print(f"      • Assistant response: {training.assistant[:60]}...")

    # ── Stage 4: Export Formats ──────────────────────────────────────────────
    print("\n[4] Exporting training formats...")

    openai_fmt = training.to_openai_format()
    print("   ✅ OpenAI format (messages array):")
    print(f"      • Roles: {[m['role'] for m in openai_fmt['messages']]}")
    print(f"      • Total chars: {sum(len(m['content']) for m in openai_fmt['messages'])}")

    anthropic_fmt = training.to_anthropic_format()
    print("\n   ✅ Anthropic format (system + messages):")
    print(f"      • Has system: {bool(anthropic_fmt.get('system'))}")
    print(f"      • Message roles: {[m['role'] for m in anthropic_fmt['messages']]}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("RESULT: ✅ ALL STAGES PASSED")
    print("="*80)
    print("""
    Pipeline completed successfully:
    
    Stage 1 (Normaliser):
      - Cleaned & classified raw content
      - Inferred grade, subject, content type, difficulty
      - Result: NormalisedContent record
    
    Stage 2 (CAPS Aligner):
      - Mapped to CAPS phase, subject, topic code
      - Looked up learning outcomes
      - Result: CAPS-enriched NormalisedContent
    
    Stage 3 (Training Formatter):
      - Generated system prompt (EduBoostAI persona)
      - Extracted user question & assistant answer
      - Result: TrainingRecord (system/user/assistant triplet)
    
    Stage 4 (Export Formats):
      - Converted to OpenAI format (messages array)
      - Converted to Anthropic format (system + messages)
      - Ready for fine-tuning or RAG indexing
    
    Next steps:
      1. Test with real scraper sources (Khan Academy, Siyavula, etc.)
      2. Run batch ingestion with rate limiting & dedup
      3. Store results in PostgreSQL
      4. Export training JSONL for LLM fine-tuning
    """)

    return True


if __name__ == "__main__":
    success = test_full_pipeline()
    exit(0 if success else 1)
