# EduBoost V2 Agent Instructions

This file mirrors the repository’s agent-driven workflow style, but applies specifically to the V2 migration stream.

## Core Rule
Treat `gemini-code-1777601244294.md` as the active architectural north star for V2 work.

## Working Mode
- Prefer incremental replacement over destructive rewrite.
- Preserve legacy compatibility until a V2 replacement slice is implemented.
- Update V2-specific audit docs after every loop cycle.
- Keep MkDocs + mkdocstrings pages aligned with new V2 modules.

## Completion Standard
A V2 slice is only complete when:
1. code is added or migrated
2. docs are updated
3. audit files are updated
4. the work is committed
