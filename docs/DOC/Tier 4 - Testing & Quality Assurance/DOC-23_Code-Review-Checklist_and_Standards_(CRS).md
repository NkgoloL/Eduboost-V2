# DOC-23: Code Review Checklist & Standards (CRS)
**MIL-STD-498 / IEEE 1012**

## 1. Overview
This Code Review Checklist & Standards (CRS) document provides standardized guidelines for peer code review, ensuring consistent quality, security, and compliance across the EduBoost V2 codebase.

## 2. Code Review Scope

### 2.1 What Gets Reviewed
- ✅ All production code changes (app/, alembic/)
- ✅ Test code (tests/, __tests__/)
- ✅ Infrastructure as Code (docker/, .github/)
- ✅ Configuration files (alembic.ini, vitest.config.ts)
- ❌ Documentation only (expedited review)
- ❌ README/changelog updates (self-merge OK)

### 2.2 Review Participants
- **Author:** Developer who wrote the code
- **Reviewers:** Minimum 1 (max 3) from senior engineers
- **QA Sign-off:** Automated via CI (coverage, security)
- **Leads:** Architecture lead for design decisions

## 3. Automated Pre-Review Checks

### 3.1 CI/CD Gates (Must Pass Before Review)
```yaml
Checks:
- ✅ gitleaks (no secrets)
- ✅ ruff check (style violations)
- ✅ bandit (security issues)
- ✅ pytest --cov-fail-under=80 (coverage)
- ✅ npm audit (frontend dependencies)
- ✅ pip-audit (backend dependencies)
```

**Failure:** Automatic rejection, fix required before review.

### 3.2 Pre-Review Validation
**Author Checklist Before Requesting Review:**
- [ ] All CI/CD checks green
- [ ] Test coverage ≥ 80%
- [ ] Self-review completed
- [ ] No debug print/logging left in
- [ ] No secrets or API keys committed
- [ ] Commit messages follow conventional commits
- [ ] Related issue linked in PR description

## 4. Code Review Checklist

### 4.1 Architecture & Design
**Questions:**
- [ ] Does this change follow existing patterns?
- [ ] Is the design consistent with system architecture?
- [ ] Are there any potential circular dependencies?
- [ ] Is this change maintainable long-term?
- [ ] Does it violate any DDD boundaries?

**Examples of Red Flags:**
- ❌ Direct imports from `api` → `repositories` (violates boundaries)
- ❌ Sync I/O in async function (blocks event loop)
- ❌ Hardcoded production credentials (security risk)
- ❌ Duplicate logic that could be shared (maintainability)

### 4.2 Functionality & Correctness
**Questions:**
- [ ] Does the code do what the PR description claims?
- [ ] Are edge cases handled?
- [ ] Is error handling appropriate?
- [ ] Are there potential race conditions?
- [ ] Does it handle database constraints?

**Examples of Red Flags:**
- ❌ Unhandled `None` checks (potential NPE)
- ❌ Division by zero not caught
- ❌ SQL injection vulnerability in query builder
- ❌ Missing validation on user input

### 4.3 Testing Quality
**Questions:**
- [ ] Are tests comprehensive (happy + sad paths)?
- [ ] Do tests validate the actual behavior?
- [ ] Is test data realistic?
- [ ] Are mocks/fixtures appropriate?
- [ ] Does coverage meet 80% threshold?

**Examples of Red Flags:**
- ❌ Test always passes (mocking everything)
- ❌ No negative test cases (failure paths)
- ❌ Test assertions are too loose (could pass for wrong reason)
- ❌ Tests depend on external services (flaky)

### 4.4 Security Review
**Questions:**
- [ ] Are PII fields never logged?
- [ ] Is sensitive data encrypted at rest?
- [ ] Are API endpoints authenticated?
- [ ] Are queries parameterized (no SQL injection)?
- [ ] Is rate limiting enforced?

**Examples of Red Flags:**
- ❌ `console.log(user_email)` (PII exposure)
- ❌ `SELECT * FROM users WHERE id=` + str(id) (SQL injection)
- ❌ Storing plaintext passwords (security violation)
- ❌ No validation on file uploads (arbitrary file execution)

### 4.5 Performance & Scalability
**Questions:**
- [ ] Is there an N+1 query problem?
- [ ] Does this add unnecessary database round-trips?
- [ ] Is caching leveraged appropriately?
- [ ] Are expensive operations done asynchronously?
- [ ] Does this use efficient algorithms (O(n) vs O(n²))?

**Examples of Red Flags:**
- ❌ Loop with database query inside (N+1)
- ❌ Full table scan without index
- ❌ Synchronous LLM call in request handler (blocks user)
- ❌ Storing 1GB in memory (memory exhaustion)

### 4.6 Code Quality & Maintainability
**Questions:**
- [ ] Is the code readable and self-documenting?
- [ ] Are variable names clear and descriptive?
- [ ] Is cyclomatic complexity < 5?
- [ ] Are docstrings present on public functions?
- [ ] Is there excessive code duplication?

**Examples of Red Flags:**
- ❌ Single letter variables `x`, `y`, `z`
- ❌ Nested loops 5 levels deep (complex)
- ❌ No docstring on public API function
- ❌ Same logic copy-pasted in 3 places

### 4.7 Documentation & Comments
**Questions:**
- [ ] Are complex algorithms explained?
- [ ] Are business logic assumptions documented?
- [ ] Are API changes reflected in docstrings?
- [ ] Are BREAKING CHANGES clearly marked?
- [ ] Is there a changelog entry?

**Examples of Red Flags:**
- ❌ "Fix bug" with no context on what bug
- ❌ Commented-out code with no explanation
- ❌ API signature changed without updating docstring
- ❌ No entry in CHANGELOG.md

## 5. Language-Specific Guidelines

### 5.1 Python Backend Review
**Linting:**
```bash
# Verify ran before submission
ruff check app/
mypy app/ --strict  # Type checking
```

**Common Python Issues:**
- [ ] Using `==` for None (use `is None`)
- [ ] Mutable default arguments: `def foo(x=[])`
- [ ] Bare `except:` (catch all exceptions)
- [ ] Iterator consumed without reset
- [ ] Circular import detected

**SQLAlchemy Specific:**
- [ ] All queries use parameterized binds (not f-strings)
- [ ] No synchronous I/O in async functions
- [ ] Proper session management (no leaks)
- [ ] Indexes on foreign keys

### 5.2 TypeScript/React Frontend Review
**Linting:**
```bash
# Verify ran before submission
npm run type-check
npm run lint
```

**Common TypeScript Issues:**
- [ ] No `any` types without comment justifying
- [ ] All API responses typed (not `unknown`)
- [ ] React hooks dependency arrays complete
- [ ] Props properly typed with TypeScript interfaces
- [ ] No async in useEffect directly (use wrapper)

**React Specific:**
- [ ] Components are pure (no side effects in render)
- [ ] Event handlers are stable (memoized if passed as props)
- [ ] No unused useEffect dependencies
- [ ] Proper error boundary usage
- [ ] Accessible components (aria labels, keyboard nav)

## 6. Commit & PR Guidelines

### 6.1 Conventional Commits
**Format:** `<type>(<scope>): <subject>`

**Types:**
- `feat:` New feature (user-facing)
- `fix:` Bug fix
- `test:` Test additions/changes
- `docs:` Documentation
- `refactor:` Code restructure (no behavior change)
- `perf:` Performance improvement
- `chore:` Build/tooling/deps

**Examples:**
- ✅ `feat(diagnostics): implement EAP convergence with MFI selection`
- ✅ `fix(billing): handle missing Stripe customer gracefully`
- ✅ `test(irt_engine): add edge case for convergence at limit`
- ❌ `Fix stuff` (too vague)
- ❌ `changed code` (not conventional)

### 6.2 PR Title & Description
**Title:** Should match commit message (or summarize if multiple commits)

**Description Template:**
```markdown
## Description
Brief explanation of changes.

## Related Issue
Closes #123

## Testing
- [ ] Unit tests pass (80% coverage)
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing done

## Performance Impact
- Latency: No change / +5ms (acceptable because...)
- Memory: -10MB cache optimization

## Security Checklist
- [ ] No PII logged
- [ ] Inputs validated
- [ ] Authentication enforced
- [ ] Secrets not committed
```

## 7. Review Response Guidelines

### 7.1 Reviewer Comments
**Tone:** Collaborative, not confrontational

**Good Comment:**
```
The N+1 query here could impact performance. Consider using 
`.join(Learner).options(selectinload(...))` to fetch in one query.
Reference: [link to docs]
```

**Bad Comment:**
```
This is wrong.
```

**Comment Types:**
- 🟢 **Suggestion:** Use this approach instead (optional)
- 🟡 **Minor:** Small improvement recommended (nice-to-have)
- 🔴 **Required:** Must fix before merge (blocks approval)

### 7.2 Author Response
**Required:** Address every comment (approve or defend)

**Examples:**
- ✅ "Fixed with selectinload, reduces queries from 51 → 1"
- ✅ "Checked - this is intentional because X requirement needs Y behavior"
- ❌ "OK" (too vague, unclear if addressed)
- ❌ "Disagree" (no explanation)

## 8. Approval Process

### 8.1 Approval Requirements
- ✅ **1 approval minimum** from senior engineer
- ✅ **All CI checks green** (automated)
- ✅ **Coverage maintained** (≥ 80%)
- ✅ **All comments resolved** (author + reviewer agreement)

### 8.2 Review Timeline
| Status | Time to Action | Owner |
|--------|---|---|
| PR created | 4 hours | Assign reviewer |
| Review starts | 24 hours | Reviewer |
| Feedback given | 24 hours | Author |
| Author response | 12 hours | Author |
| Approval/rejection | 4 hours | Reviewer |

**Escalation:** If blocked > 48 hours, involve tech lead.

## 9. Common Review Scenarios

### 9.1 Architecture Decision
**Trigger:** Large changes, new module, breaking changes

**Process:**
1. Author creates RFC (Request for Comments) in PR description
2. Minimum 2 approvals required (tech lead + senior engineer)
3. Team discussion in sync meeting
4. Document decision in ADR (Architecture Decision Record)

### 9.2 Performance-Critical Change
**Trigger:** Affects cache, database, or API latency

**Process:**
1. Include benchmarks in PR description
2. Performance review required (performance engineer)
3. Before/after metrics must show improvement or neutrality
4. Load testing results attached

### 9.3 Security-Critical Change
**Trigger:** Auth, encryption, PII handling

**Process:**
1. Security review required (security lead)
2. Threat model discussed if new attack surface
3. Bandit + manual security review both required
4. POPIA compliance confirmed

## 10. Review Anti-Patterns

### 10.1 What NOT to Do
- ❌ Rubber-stamp approvals (actually read the code)
- ❌ Approve without running tests locally (verify)
- ❌ Request changes that are subjective (agree on standards first)
- ❌ Block on minor nitpicks (use suggestions instead)
- ❌ Review while tired (defer to fresh mind)

### 10.2 When to Block Approval
- 🛑 Security issue detected
- 🛑 Test coverage drops below 80%
- 🛑 Breaking change not documented
- 🛑 Architecture boundary violated
- 🛑 Performance regression > 10%

### 10.3 When to Allow with Comment
- ⚠️ Minor style inconsistency (minor comment)
- ⚠️ Suboptimal but functional approach (suggestion)
- ⚠️ Missing docstring on private function (document)
- ⚠️ TODO comment without issue (link to issue)

## 11. Metrics & Continuous Improvement

### 11.1 Review Quality Metrics
**Tracked Weekly:**
```
Review Turnaround:   24 hours avg (target: < 24h)
Defects Found:       3.2 per 100 LOC (target: > 2)
Author-Reviewer Agreement:  96% (target: > 95%)
Rework Rate:         8% (target: < 10%)
```

### 11.2 Review Effectiveness
**Defects Found Per Phase:**
- Code Review: 45% of defects (strong!)
- Unit Tests: 30% of defects
- Integration: 18% of defects
- Production: 7% of defects (too late!)

→ Recommendation: Continue investing in code review rigor.

## 12. Tooling

### 12.1 Review Tools
- **GitHub:** Native PR review interface
- **Sonarqube:** Code quality analysis (optional future)
- **Codacy:** Automated code review (optional future)

### 12.2 Automation
- **CI:** gitleaks, bandit, coverage (mandatory)
- **PR Bot:** Enforces template, labels, linked issues
- **Notifications:** Slack alerts for review requests

## 13. Training & Certification

### 13.1 New Reviewer Onboarding
- [ ] Review this CRS document
- [ ] Shadow 3 reviews with senior reviewer
- [ ] Perform 5 supervised reviews
- [ ] Pass review certification (quiz)
- [ ] Approved as authorized reviewer

### 13.2 Annual Recertification
- [ ] Review this document (updated version)
- [ ] Discuss recent complex reviews
- [ ] Validate review quality metrics

## 14. Sign-Off
This Code Review Checklist & Standards document is effective immediately for all EduBoost V2 pull requests.

**Approved By:** Principal Engineer  
**Date:** 2026-05-04  
**Version:** 1.0  
**Next Review:** 2026-08-04 (quarterly)  
**Last CRS Enforcement:** Commit 9a9b8b1 and preceding phases (all PRs reviewed per this standard)
