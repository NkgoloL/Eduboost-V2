# Content Generation Configuration

**File**: [scripts/curriculum/content_generation_config.py](scripts/curriculum/content_generation_config.py)  
**Purpose**: Configure LLM providers, quality validators, and generation parameters  
**Status**: Ready for implementation

---

## Configuration Overview

This module will handle:

1. LLM provider setup (Anthropic Claude, Groq, or fallback)
2. Quality validation framework for generated content
3. Batch generation parameters and concurrency control
4. Content template specifications
5. Logging and monitoring setup

---

## Environment Variables Required

Add these to `.env` file for Phase 2:

```bash
# LLM Providers
ANTHROPIC_API_KEY=<your-anthropic-api-key>
GROQ_API_KEY=<your-groq-api-key>
LLM_PROVIDER=anthropic  # or 'groq'

# Generation Parameters
GENERATION_MODEL=claude-3.5-sonnet  # or 'groq-mixtral'
GENERATION_MAX_TOKENS=4000
GENERATION_TEMPERATURE=0.7
GENERATION_TOP_P=0.9

# Quality Control
MIN_LESSON_LENGTH=500  # characters
MAX_LESSON_LENGTH=10000
MIN_CONFIDENCE_SCORE=0.85

# Batch Processing
BATCH_SIZE=10
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT_SECONDS=60
RETRY_ATTEMPTS=3

# Monitoring
GENERATION_LOG_LEVEL=INFO
SAVE_GENERATION_ARTIFACTS=true
ARTIFACT_DIR=data/generated/artifacts
```

---

## Quality Validators

Each lesson generated must pass these validators:

### Required Fields Validator

```python
required_fields = [
    'lesson_title',           # str, 1-200 characters
    'lesson_body',            # str, min 500 characters
    'scope_id',               # str, matches topic map scope
    'variant',                # str, one of: standard, visual, kinesthetic
    'teacher_notes',          # str, min 100 characters
    'parent_notes',           # str, min 100 characters
    'extension_prompts',      # list of str, min 3 items
    'estimated_duration',     # int, 10-180 minutes
    'prerequisite_topics',    # list of str, can be empty
]

# All fields must be non-null and properly typed
```

### Content Quality Validator

```python
content_checks = {
    'no_hallucinations': {
        'rule': 'Content must not contain made-up facts',
        'method': 'Fact-check against CAPS source',
        'pass_rate': 100,  # Must be 100%
    },
    'grade_appropriate': {
        'rule': 'Vocabulary and concepts match grade level',
        'method': 'Readability scoring (Flesch-Kincaid)',
        'pass_rate': 95,  # ≥95%
    },
    'no_AI_artifacts': {
        'rule': 'No generic AI phrases ("As an AI...", "It is important...")',
        'method': 'Pattern matching against AI slop keywords',
        'pass_rate': 98,  # ≥98%
    },
    'pedagogical_sound': {
        'rule': 'Includes learning objectives, examples, activities',
        'method': 'Structure validation',
        'pass_rate': 95,  # ≥95%
    },
    'inclusive_language': {
        'rule': 'Uses inclusive, respectful language',
        'method': 'Bias detection scoring',
        'pass_rate': 98,  # ≥98%
    },
}
```

### Structure Validator

```python
structure_checks = {
    'has_title': {
        'rule': 'Lesson title present',
        'validation': len(lesson['lesson_title']) > 5 and len(lesson['lesson_title']) < 200,
    },
    'has_learning_objectives': {
        'rule': 'Learning objectives clearly stated',
        'validation': 'learner will' in lesson['lesson_body'].lower() or 'objective' in lesson['lesson_body'].lower(),
    },
    'has_examples': {
        'rule': 'Real-world examples included',
        'validation': 'example' in lesson['lesson_body'].lower(),
    },
    'has_activities': {
        'rule': 'Learner activities included',
        'validation': 'activity' in lesson['lesson_body'].lower() or 'exercise' in lesson['lesson_body'].lower(),
    },
    'has_summary': {
        'rule': 'Summary or review section included',
        'validation': 'summary' in lesson['lesson_body'].lower() or 'review' in lesson['lesson_body'].lower(),
    },
}
```

### Compliance Validator

```python
compliance_checks = {
    'no_external_links': {
        'rule': 'No unverified external URLs in content',
        'validation': 'http' not in lesson['lesson_body'],
    },
    'no_email_addresses': {
        'rule': 'No email addresses exposed',
        'validation': '@' not in lesson['lesson_body'],
    },
    'copyright_compliant': {
        'rule': 'Content derived from CAPS (licensed for reuse)',
        'validation': True,  # By design, derived from CAPS
    },
    'popia_compliant': {
        'rule': 'No personal information included',
        'validation': 'Grade 7 learner' not in lesson['lesson_body'],  # Generic, not personal
    },
}
```

---

## LLM Prompt Templates

### Main Lesson Generation Prompt

```markdown
You are an expert South African curriculum developer creating high-quality 
educational lessons aligned with the CAPS (Curriculum and Assessment Policy Statement).

**Context**:
- Grade Level: {{grade_level}}
- Subject: {{subject}}
- Topic: {{topic_title}}
- Learning Outcomes: {{caps_learning_outcomes}}
- Prerequisite Topics: {{prerequisites}}

**Your Task**:
Create a comprehensive lesson that:

1. **Lesson Title**: Clear, engaging, 1-200 characters
   - Example: "Understanding Fractions: Parts of a Whole"

2. **Lesson Body** (500-2000 words):
   - Start with 2-3 clear learning objectives
   - Explain the concept in learner-friendly language
   - Include 3-5 real-world examples from South African context
   - Provide 2-3 step-by-step practice activities
   - Include a summary/review section
   - Use {{grade_level}}-appropriate vocabulary

3. **Teacher Notes** (200+ characters):
   - Pedagogical tips for effective teaching
   - Common misconceptions to watch for
   - Differentiation strategies
   - Time management guidance

4. **Parent Notes** (200+ characters):
   - How parents can support learning at home
   - Real-world applications
   - Fun extension activities families can do together
   - Key vocabulary to discuss

5. **Extension Prompts** (3+ items):
   - Challenge questions for advanced learners
   - Real-world problem-solving scenarios
   - Cross-curricular connections
   - Format as JSON array

6. **Estimated Duration**: 30-120 minutes

**Requirements**:
- Ground all examples in South African context
- Use inclusive, accessible language
- Avoid jargon unless explained
- Be factually accurate
- Follow CAPS assessment principles

**Output Format**: JSON with required fields
```

### Variant Generation Prompt (Visual)

```markdown
Create a VISUAL VARIANT of this lesson that emphasizes:
- Diagrams and visual explanations
- Visual step-by-step processes
- Graphic organizers
- Charts and tables where appropriate

Ensure descriptions are detailed enough for:
- Teachers to create visual aids
- Learners to draw/create visuals
- Digital rendering as infographics

Output as lesson_body with detailed visual descriptions in markdown.
```

### Variant Generation Prompt (Kinesthetic)

```markdown
Create a KINESTHETIC/HANDS-ON VARIANT of this lesson that emphasizes:
- Physical manipulatives and concrete materials
- Movement and gesture-based learning
- Practical experiments and activities
- Real-world problem-solving tasks

Include:
- Materials needed (use common South African items)
- Step-by-step activity instructions
- Safety considerations
- Success criteria for activities

Output as lesson_body with detailed activity instructions.
```

---

## Generation Workflow

### Phase 1: Pre-Generation Setup

```
1. Load approved topic maps from data/caps/topic_maps/
2. Verify all topics have `topic_map_approved: true` status
3. Initialize LLM provider (Anthropic/Groq)
4. Set up generation logging and artifact collection
5. Create generation batch manifest
```

### Phase 2: Batch Generation

```
For each approved topic map:
  For each variant (standard, visual, kinesthetic):
    1. Render LLM prompt with topic context
    2. Call LLM provider with prompt
    3. Parse LLM response to structured lesson
    4. Run quality validators on generated lesson
    5. Log generation metadata (tokens, duration, score)
    6. Save to data/generated/lessons/
    7. On failure: Log error, retry up to 3 times, mark as failed
```

### Phase 3: Quality Assurance

```
1. Run automated validation on all generated lessons
2. Generate QA report with pass/fail metrics
3. Flag lessons failing critical validators
4. Prepare sample set for manual review (10% of total)
5. Collect expert feedback and incorporate learnings
```

### Phase 4: Database Import

```
1. Validate all lessons pass quality bar
2. Transform lessons to database schema
3. Test import on staging environment
4. Execute bulk import transaction
5. Verify data integrity post-import
6. Create backup checkpoint
```

---

## Expected Outputs

### Generated Lesson Structure

```json
{
  "generated_lesson": {
    "scope_id": "grade7_mathematics_en",
    "topic_id": "fraction_operations_division",
    "lesson_title": "Dividing Fractions: Why It Works",
    "variant": "standard",
    "lesson_body": "...[2000+ words]...",
    "teacher_notes": "...[200+ words]...",
    "parent_notes": "...[200+ words]...",
    "extension_prompts": [
      "How would dividing fractions help in real-world baking recipes?",
      "Create a word problem involving fraction division from your daily life",
      "Explain why multiplying by the reciprocal works mathematically"
    ],
    "estimated_duration_minutes": 45,
    "prerequisite_topics": ["fraction_basics", "fraction_multiplication"],
    "metadata": {
      "generated_at": "2026-06-05T20:30:00Z",
      "llm_provider": "anthropic",
      "llm_model": "claude-3.5-sonnet",
      "tokens_used": 2847,
      "generation_duration_seconds": 8.3,
      "quality_score": 0.94,
      "quality_checks_passed": [
        "no_hallucinations",
        "grade_appropriate",
        "pedagogical_sound",
        "inclusive_language",
        "required_fields"
      ],
      "quality_checks_failed": [],
      "confidence_score": 0.94
    }
  }
}
```

### Generation Statistics Report

```
CONTENT GENERATION EXECUTION REPORT
Generated: 2026-06-05 21:30 UTC

PHASE 1: Foundation Phase (5 scopes × 3 variants = 15 lessons)
  Status: ✅ COMPLETE
  Generated: 15/15 (100%)
  Quality Score: 0.96 average
  Pass Rate: 100% (0 failed)
  Duration: 2 min 34 sec

PHASE 2: Intermediate Phase (20 scopes × 3 variants = 60 lessons)
  Status: ✅ COMPLETE
  Generated: 60/60 (100%)
  Quality Score: 0.94 average
  Pass Rate: 98% (1 failed, auto-retry: success)
  Duration: 8 min 12 sec

PHASE 3: Senior Phase (25 scopes × 3 variants = 75 lessons)
  Status: ✅ COMPLETE
  Generated: 75/75 (100%)
  Quality Score: 0.93 average
  Pass Rate: 97% (2 failed, auto-retry: 1 success, 1 manual review)
  Duration: 10 min 5 sec

TOTAL
  Generated: 150/150 (100%)
  Quality Score: 0.94 average
  Pass Rate: 98% (1 manual review pending)
  Total Duration: 20 min 51 sec
  LLM Cost: $47.32 (Anthropic)
  Per-Lesson Cost: $0.315

QA STATUS
  Automated Validation: 149/150 passed (99.3%)
  Manual Review Needed: 1 lesson
  Ready for Database Import: 149 lessons
  Rejection Rate: 0.7%
```

---

## Success Criteria

✅ Phase 2 Content Generation is successful when:

- Generated 150 lessons (50 scopes × 3 variants)
- ≥98% pass quality validation
- All required fields populated for approved lessons
- All lessons ready for database import
- QA report signed off
- No blocking issues blocking database import

---

## Implementation Roadmap

**Week 1 (June 6-7)**:
- [ ] Set up LLM provider credentials
- [ ] Implement quality validators
- [ ] Test generation on sample lesson
- [ ] Prepare generation environment

**Week 2 (June 10-14)**:
- [ ] Run Phase 1 generation (Foundation)
- [ ] Run Phase 2 generation (Intermediate)
- [ ] Run Phase 3 generation (Senior)
- [ ] Collect generation statistics

**Week 3 (June 17-18)**:
- [ ] Run full QA validation
- [ ] Conduct manual review sample (10%)
- [ ] Prepare database import
- [ ] Execute import to staging

---

**Next Step**: Create implementation scripts for content_generation_config.py, quality_validators.py, and lesson_generator.py

**Blocker**: Awaiting LLM API credentials setup in Phase 2 Step 3
