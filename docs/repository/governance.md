# Repository Governance — EduBoost

**Last Updated**: 2026-06-12  
**Audience**: Contributors, maintainers, administrators

---

## Branch Strategy

### Main Branch

- **Name**: `master`
- **Protection**: Strict
- **Direct pushes**: Never allowed
- **History**: Linear (no force pushes)

### Release Branches

- **Naming**: `release/v<major>.<minor>.<patch>`
- **Created from**: `master`
- **Merged to**: `master` via PR
- **Deletion**: 30 days after release

### Feature Branches

- **Naming**: `feature/<ticket>-<description>` or `pr/<pr-number>`
- **Created from**: `master`
- **Merged via**: Pull request

### Hotfix Branches

- **Naming**: `hotfix/<description>`
- **Created from**: `master`
- **Requires**: Expedited PR review

---

## Branch Protection Settings

### Master Branch

The following settings are enforced on `master`:

| Setting | Value |
|---------|-------|
| Require pull request reviews | ✅ (at least 1 reviewer) |
| Required reviews before merging | 1 |
| Require status checks to pass | ✅ |
| Require branches to be up to date | ✅ |
| Include administrators | ✅ |
| Allow force pushes | ❌ |
| Allow deletions | ❌ |
| Require signed commits | Recommended |

### Release Branches

| Setting | Value |
|---------|-------|
| Require pull request reviews | ✅ |
| Require status checks | ✅ |
| Allow force pushes | ❌ |
| Allow deletions | ❌ |

---

## Pull Request Requirements

### Before Opening PR

- [ ] All tests pass locally (`make test-fast`)
- [ ] Code formatted (`make lint`)
- [ ] Type checks pass (`make typecheck`)
- [ ] No new security vulnerabilities (`make security-check`)
- [ ] PR description follows template

### PR Description Template

```markdown
## Summary
<!-- What does this PR do? -->

## Changes
<!-- List the changes -->

## Testing
<!-- How was this tested? -->

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Security impact considered
```

### Review Requirements

- **1 reviewer** minimum for all PRs
- **2 reviewers** for:
  - Security-related changes
  - Database migrations
  - Dependency updates
  - API contract changes

---

## CI/CD Workflows

### Required Checks

All PRs must pass these checks before merge:

1. **Unit Tests** — `pytest tests/unit/`
2. **Integration Tests** — `pytest tests/integration/`
3. **Lint** — `ruff check .`
4. **Type Check** — `mypy app/`
5. **Security** — `pip-audit` (if dependencies changed)

### Optional Checks

These run but don't block merge:

- E2E Tests (run nightly)
- Performance Benchmarks
- Coverage reports

---

## Commit Guidelines

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### Example

```
feat(auth): add JWT refresh token rotation

- Implement refresh token rotation on login
- Store token version in database
- Invalidate old tokens on refresh

Closes #123
```

---

## Contributor Workflow

1. **Fork** the repository
2. **Create** a feature branch from `master`
3. **Make** your changes with tests
4. **Push** and open a Pull Request
5. **Address** review feedback
6. **Merge** after approval

---

## Security Considerations

### Secret Management

- Never commit secrets to the repository
- Use environment variables or secrets management
- `.env.example` should contain only placeholders

### Vulnerability Reporting

If you find a security vulnerability:

1. **DO NOT** open a public issue
2. Email **security@eduboost.co.za** directly
3. We will acknowledge within 24 hours
4. We will work on a fix and disclosure timeline

---

## Contact

- **Repository Maintainers**: @NkgoloL
- **Security Issues**: security@eduboost.co.za
- **General Questions**: support@eduboost.co.za