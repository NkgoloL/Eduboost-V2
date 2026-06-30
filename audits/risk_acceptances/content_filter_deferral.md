# Risk Acceptance / Decision Memo — Content Filter Middleware

**Phase 0 task:** T050
**Status:** ⚠️ **UNSIGNED** — awaiting Security/Safety owner sign-off.
**Date opened:** 2026-05-27
**Author of draft:** Engineering (Phase 0 remediation)
**Required reviewer/signer:** Security/Safety owner (per TODO T050 reviewer
designation)

---

## Background

The 2026-05-27 Technical State Audit observed that the project should have
a content filter middleware (`app/core/content_filter.py` defining
`content_filter_middleware`) that screens AI-mediated traffic to minors.
The TODO doc states the file "exists and defines `content_filter_middleware`"
but is not registered in `app/api_v2.py`.

### Reality on `origin/master`

A focused search of `origin/master` at the audit replay finds **no
`content_filter.py` module anywhere in the tree** and **no reference to
`content_filter_middleware`** in `app/api_v2.py` or elsewhere:

```text
$ find . -path ./node_modules -prune -o -path ./.venv -prune \
       -o -name "content_filter*" -print
(no output)

$ grep -rln "content_filter_middleware\|content_filter" app/ --include="*.py"
(no output)
```

The audit's premise that the module exists locally but is unwired does not
match what is on `origin/master`. The actual situation is more serious:
**there is no content filter implementation in version control at all.**

This memo exists so the Security/Safety owner can make an informed
release-blocking decision against the **actual** state of the codebase,
not against the audit's outdated premise.

---

## Decision required

The Security/Safety owner must choose one of three paths and sign below.

### Option A — Implement and wire a content filter before launch

Cost: substantial (multi-day) engineering work plus security review.

Required engineering work if chosen:

1. Draft a threat model for the AI-mediated learner traffic surface. Enumerate
   prohibited content categories (e.g., self-harm, sexual content, prompt
   injection that leaks system instructions, attempts to extract PII about
   other learners).
2. Implement `app/core/content_filter.py` exposing `content_filter_middleware`.
   The middleware screens both inbound requests and outbound LLM responses.
3. Register the middleware in `app/api_v2.py` in correct order (after
   authentication, before LLM-calling routes).
4. Add tests under `tests/security/` proving:
   - Prohibited content in → safe 4xx response (e.g., 400 with a structured
     error code, no exception leakage).
   - Clean educational content → pass-through (no false positives).
   - Outbound response screening: LLM hallucination of prohibited content →
     filtered before returning to learner.
5. Document the policy: `docs/safety/content_policy.md` (this also covers
   Phase 1 T101).
6. Security review and sign-off on the threat model + implementation.

This is roughly a 3–5 day effort (`L` complexity in the TODO scale) with
explicit security review.

### Option B — Formally defer the content filter past the next release

Acceptable only with a signed risk acceptance from the Security/Safety
owner, the Information Officer (POPIA), and the Product owner. The
acceptance must record:

- **Owner:** _________________________________
- **Residual risk:** _________________________________________________
  _____________________________________________________________________
  _____________________________________________________________________
- **Mitigations in lieu of a content filter:**
  - [ ] LLM provider's own moderation API enabled (specify provider + model)
  - [ ] LLM system prompts hardened against jailbreaks (link to prompt file)
  - [ ] Per-learner LLM call budget guardrails (Phase 2 T233 status: _____)
  - [ ] Manual moderation queue for flagged content (process owner: _____)
  - [ ] Other: __________________________________________________________
- **Re-evaluation date:** _____________ (must be before any expansion of the
  learner population beyond pilot scope).
- **Notification path on incident:** _______________________________________

### Option C — Block release until the decision is made

Default if neither A nor B is signed within seven business days of this
memo's creation. The release-blocking flag set by the audit remains in
force.

---

## Recommendation from Engineering

Engineering recommends **Option A** for the following reasons:

1. The product serves minors as the primary audience. POPIA processing of
   minor data combined with AI-mediated content is the highest-risk surface
   in the system.
2. The LLM provider's own moderation API is not a sufficient substitute on
   its own — it covers prompt input but does not enforce the project's
   specific CAPS / age-appropriate content policy.
3. The audit's classification of T050 as P0 is appropriate given the
   processing context.
4. The work is bounded (`L` per the TODO) and the threat model can reuse
   existing prior art (OpenAI moderation guidelines, Anthropic safe-system
   prompts, NIST AI RMF GV-4).

Engineering does not have the authority to make this call alone.

---

## Sign-off

| Role | Name | Decision (A / B / C) | Date | Signature |
|---|---|---|---|---|
| Security/Safety owner | | | | |
| Information Officer (POPIA) | | | | |
| Product owner | | | | |

Until all three rows are signed and committed in a follow-up PR, T050
remains **OPEN** in the Phase 0 register, and Phase 1 T100 (wire the
filter) cannot start.
