# FE-SPIKE-002 — Initial bundle budget (≤120KB gzipped)

## Objective

Quantify the baseline JS payload for the learner shell after the React 19 upgrade so we can prove RC1/RC2 work begins under the 120KB gzipped guardrail from TODO_V4.1 and identify early remediation items.

## Setup

1. Ran `npm ci` (already executed for FE-SPIKE-001) to ensure a clean dependency tree.
2. Captured a production build log via `NEXT_TELEMETRY_DISABLED=1 npm run build > /tmp/fe-spike-002-build.log`.
3. Measured the two shared chunks and the heaviest route chunk with `gzip -c <file> | wc -c`.

## Findings

| Artifact | Path | Raw size | Gzipped size |
| --- | --- | --- | --- |
| Shared chunk A | `.next/static/chunks/255-e881f48ae1d2333a.js` | 46.2 kB | **45,?**

