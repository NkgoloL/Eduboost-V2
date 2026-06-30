# Dependency Management — EduBoost

**Last Updated**: 2026-06-12  
**Audience**: Engineering team

---

## Overview

This document describes the canonical dependency paths, separation of concerns between requirements files, and tooling for dependency hygiene.

---

## Requirements Files

| File | Purpose | When to Update |
|------|---------|-----------------|
| `requirements/base.txt` | Core runtime dependencies | When adding features used in production |
| `requirements/dev.txt` | Development + testing dependencies | When adding linters, test tools |
| `requirements/docs.txt` | Documentation site dependencies | When adding MkDocs plugins |
| `requirements/ml.txt` | ML/AI dependencies (GPU/CUDA) | When adding transformers, torch, etc. |

### Canonical Paths

```
# Install core runtime
pip install -r requirements/base.txt

# Install development dependencies
pip install -r requirements/dev.txt

# Install docs dependencies
pip install -r requirements/docs.txt

# Install ML dependencies (large — only on GPU machines)
pip install -r requirements/ml.txt

# Install all (excluding ML)
pip install -r requirements/base.txt -r requirements/dev.txt
```

### File Separation Rules

1. **Never duplicate dependencies** across files
2. Use `pip-compile` (from pip-tools) to generate locked files from `.in` sources
3. Runtime dependencies go in `requirements/base.txt` (not dev.txt)
4. Dev-only tools (pytest, ruff, mypy) go in `requirements/dev.txt`

---

## Generating Locked Requirements

### Using pip-compile

```bash
# Install pip-tools
pip install pip-tools

# Generate base requirements
pip-compile requirements/base.in --output-file requirements/base.txt

# Generate dev requirements
pip-compile requirements/dev.in --output-file requirements/dev.txt

# Generate docs requirements
pip-compile requirements/docs.in --output-file requirements/docs.txt
```

### pin.sh Helper

```bash
# Pin all requirements at once
./scripts/pin.sh
```

---

## Dependency Audit Commands

### Check for Outdated Packages

```bash
# Using pip-review
pip install pip-review
pip-review --interactive

# Or using pip-tools
pip install pip-tools
pip-compile --dry-run requirements/base.txt
```

### Check for Conflicts

```bash
pip install pipcheck
pipcheck -r requirements/base.txt
pipcheck -r requirements/dev.txt
```

### Check for Vulnerabilities

```bash
pip install pip-audit
pip-audit -r requirements/base.txt
pip-audit -r requirements/dev.txt
```

---

## Makefile Targets

The following targets are available:

```bash
# Check for outdated packages
make deps-check

# Check for security vulnerabilities
make deps-vulnerable

# Check for conflicts
make deps-conflicts
```

---

## Dependency Update Policy

| Severity | Action | Frequency |
|----------|--------|-----------|
| Security vulnerability | Update immediately | ASAP |
| Major version bump | Test in branch, then update | Per release |
| Minor version bump | Update during regular maintenance | Monthly |
| Patch update | Update during regular maintenance | Weekly |

---

## Common Issues

### Version Conflicts

If you see resolution errors:

1. Check which package requires the conflicting version
2. Consider if one can be relaxed
3. Use pip's `--no-deps` cautiously
4. Document in this file if workaround applied

### Unused Dependencies

Run pip-tools to detect:

```bash
pip install pip-tools
pip-autopurge requirements/base.txt
```

---

## Dependabot Workflow

### Overview

EduBoost uses GitHub Dependabot to automate dependency updates. Configuration is in `.github/dependabot.yml`.

### Supported Ecosystems

| Ecosystem | Directory | Schedule | PR Limit |
|-----------|-----------|----------|----------|
| Python pip | `/` (root) | Weekly | 10 |
| npm | `/app/frontend` | Weekly | 5 |
| GitHub Actions | `/` | Monthly | 3 |
| Docker | `/` | Monthly | 3 |

### Review Process

1. **PR Creation**: Dependabot creates PRs with dependency updates
2. **Labeling**: PRs are auto-labeled with `dependencies` + ecosystem label
3. **Review Required**: All Dependabot PRs require at least one reviewer
4. **CI Checks**: Tests must pass before merge
5. **Merge Strategy**:
   - Patch updates (x.Y.z): Auto-merge enabled for passing tests
   - Minor/Major: Manual review required

### Critical CVE Response

| Severity | Response Time | Action |
|----------|---------------|--------|
| Critical (9.0+) | 24 hours | Emergency patch release |
| High (7.0-8.9) | 7 days | Priority patch release |
| Medium (4.0-6.9) | 30 days | Regular maintenance |
| Low (<4.0) | Next cycle | Schedule with regular updates |

### Disabling Dependabot for a Dependency

To temporarily hold a dependency:

```yaml
# In dependabot.yml
ignore:
  - dependency-name: "package-name"
    versions: [">=1.0.0"]
```

Or add to `.github/dependabot.yml` as `allow` to specify versions to update.

### Monitoring

- **Security Alerts**: GitHub sends email for critical vulnerabilities
- **Dependabot Dashboard**: `https://github.com/NkgoloL/eduboost-v2/network/updates`
- **CI Workflow**: `.github/workflows/dependency-scan.yml` runs daily vulnerability scans

---

## References

- [pip-tools documentation](https://pip-tools.readthedocs.io/)
- [pip-audit documentation](https://pypi.org/project/pip-audit/)
- [PyPA best practices](https://packaging.python.org/guides/)