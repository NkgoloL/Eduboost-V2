# Dependency Management

EduBoost V2 uses the `requirements/` directory as the canonical Python dependency surface. Root-level `requirements*.txt` files are compatibility aliases for common tooling and should stay one-line includes.

## Canonical files

| Purpose | Input file | Locked file | Compatibility alias |
|---|---|---|---|
| Runtime/API | `requirements/base.in` | `requirements/base.txt` | `requirements.txt` |
| Development/test/quality | `requirements/dev.in` | `requirements/dev.txt` | `requirements-dev.txt` |
| Documentation | `requirements/docs.in` | `requirements/docs.txt` | `requirements-docs.txt` |
| ML/fine-tuning/offline jobs | `requirements/ml.in` | `requirements/ml.txt` | `requirements-ml.txt` |

## Rules

- Add top-level dependency intent to the matching `.in` file, not directly to the compiled `.txt` file.
- Regenerate lock files with `pip-compile` from `pip-tools`.
- Do not add application runtime packages to `requirements/dev.in` only.
- Keep ML and fine-tuning dependencies out of the runtime image unless explicitly needed.
- Keep root alias files as compatibility shims for Docker, CI, and developer muscle memory.
- Review dependency changes for license, vulnerability, supply-chain, and image-size impact.

## Common commands

```bash
pip install pip-tools
pip-compile --output-file=requirements/base.txt requirements/base.in
pip-compile --output-file=requirements/dev.txt requirements/dev.in
pip-compile --output-file=requirements/docs.txt requirements/docs.in
pip-compile --output-file=requirements/ml.txt requirements/ml.in
```

## Runtime image guidance

Production API images should install `requirements/base.txt` unless a specific deployment target requires an extra group. Documentation, development, and ML dependencies should not be installed in the production API image by default.
