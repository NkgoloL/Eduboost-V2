# Content Filter Decision — 2026-05-28

**Status:** Proposed (awaiting sign-off)
**Context:** T050 — Sign content filter decision
**Related:** T100 — Wire content filter middleware if T050 chooses implementation

## Context

EduBoost is an educational platform serving minors (learners under 18) with AI-mediated learning flows. The platform includes:

- AI-generated lesson content
- AI-powered diagnostic assessments
- AI-mediated practice exercises
- User-generated content (guardian/teacher inputs)
- Open-ended text interactions with AI models

A content filter was identified in Phase 0 security hardening (T040-T071) as a safety control, but implementation was gated pending this decision.

## Decision Options

### Option A — Implement runtime content filter now (RECOMMENDED)

**Description:** Implement or restore `app/core/content_filter.py` and register middleware in `app/api_v2.py` to block unsafe content in real-time.

**Requirements:**
- Implement or restore content filter middleware
- Register middleware in FastAPI v2 with documented order
- Add tests proving blocked content returns safe 4xx responses
- Add negative tests proving ordinary educational content passes
- Ensure middleware covers all AI-mediated endpoints
- Document filter rules and false-positive handling

**Scope:**
- Block: hate speech, explicit content, violence, self-harm, PII in outputs
- Allow: CAPS-aligned educational content, standard math/science terminology
- Log: all blocked content for safety review
- Override: admin bypass for false-positive handling

**Pros:**
- Active safety control for minor users
- Meets POPIA and child protection obligations
- Reduces risk of harmful AI outputs
- Aligns with best practices for AI-mediated education
- Provides audit trail for safety incidents

**Cons:**
- Implementation effort required
- Risk of false positives blocking legitimate content
- Requires ongoing rule maintenance
- May add latency to AI responses
- Requires test coverage for edge cases

### Option B — Defer with signed launch restriction

**Description:** Defer content filter implementation with signed risk acceptance and explicit launch restrictions.

**Requirements:**
- Signed risk acceptance from Security, Privacy, and Product owners
- Launch restriction: no public/live learner-data launch until filter implemented
- Documented monitoring plan for AI output safety
- Incident response plan for harmful content events
- Regular safety reviews until filter is implemented

**Pros:**
- Allows immediate launch with other controls in place
- Reduces implementation pressure
- Time to design robust filter rules

**Cons:**
- No active safety control for AI outputs
- Risk of harmful content reaching minors
- May violate POPIA child protection obligations
- Launch restriction may delay revenue
- Relies on reactive incident response vs. proactive prevention

### Option C — Remove from this release scope with explicit rationale

**Description:** Remove content filter from Phase 1 scope with documented rationale for exclusion.

**Requirements:**
- Explicit rationale for why filter is not needed
- Alternative safety controls documented
- Sign-off from Security, Privacy, and Product owners
- Plan for when/if filter will be added
- Risk acceptance for minor users

**Pros:**
- Reduces Phase 1 scope
- Allows focus on other priorities

**Cons:**
- Requires strong justification for serving minors without content filter
- High risk of regulatory non-compliance
- May be unacceptable to stakeholders
- Leaves critical safety gap

## Recommended Decision

**Option A — Implement runtime content filter now**

**Rationale:**
1. EduBoost serves minors (learners under 18), which triggers higher safety obligations under POPIA and child protection laws
2. The platform includes AI-mediated learning flows where content generation is not fully predictable
3. A safety control that is only documented but not enforced is not a control
4. Implementation effort is manageable compared to the risk of harmful content reaching minors
5. Industry best practice for AI-mediated education platforms serving minors
6. Reduces liability and regulatory risk
7. Provides audit trail for safety incidents

## Implementation Scope (if Option A selected)

### Phase 1 Implementation (T100)

**Immediate:**
- Restore or implement `app/core/content_filter.py` with rule-based filtering
- Register middleware in `app/api_v2.py` before AI endpoints
- Add unit tests for filter rules
- Add integration tests for middleware behavior
- Document filter rules and override procedures

**Filter Rules:**
- Block: hate speech, explicit sexual content, violence, self-harm promotion, PII in AI outputs
- Allow: CAPS-aligned educational content, standard terminology, age-appropriate content
- Log: all blocked content with context for safety review
- Override: admin bypass with audit trail for false positives

### Testing Requirements

**Unit tests:**
- Filter rule coverage for blocked categories
- False-positive handling for educational content
- Override mechanism with audit logging

**Integration tests:**
- Middleware returns 4xx for blocked content
- Ordinary educational content passes through
- Admin override works with audit trail

**Negative tests:**
- Edge cases: borderline content, context-dependent terms
- Performance: latency impact on AI endpoints
- Internationalization: language-specific filtering

## Consequences

If Option A is selected:
- T100 must be completed before Phase 1 closure
- Additional test coverage required
- Middleware latency must be monitored
- Filter rules require ongoing maintenance
- False-positive handling procedures needed

If Option B is selected:
- Launch restriction documented and enforced
- Risk acceptance signed by required stakeholders
- Monitoring plan implemented
- Incident response plan activated
- Timeline for filter implementation defined

If Option C is selected:
- Strong justification required
- Alternative safety controls documented
- Sign-off from all required stakeholders
- Plan for future filter implementation
- High regulatory risk acknowledged

## Sign-off Required

- **Security/Safety Owner:** [REQUIRED]
- **POPIA/Privacy Owner:** [REQUIRED]
- **Product Owner:** [REQUIRED]
- **CTO/Engineering Lead:** [REQUIRED]

## References

- T050: Sign content filter decision
- T100: Wire content filter middleware if T050 chooses implementation
- T040-T071: Phase 0 security hardening
- POPIA Section 8: Processing of personal information of children
- `docs/privacy/information_officer.md`
- `PRIVACY_NOTICE.md`
