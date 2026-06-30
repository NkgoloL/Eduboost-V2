# E2E Testing Guide

**Date**: 2026-06-12
**Updated**: 2026-06-14
**Scope**: Running and maintaining Playwright E2E tests for EduBoost V2

---

## Prerequisites

- Node.js 20+
- Python 3.12+ with `.venv` activated
- Docker Compose running (for full backend integration tests)
- `pnpm` 9.x (`corepack pnpm@9.14.4` or the WSL user-local shim)

---

## Quick Start

### 1. Install Dependencies

```bash
# Install root Playwright dependencies
pnpm install --frozen-lockfile

# Install frontend dependencies
pnpm --dir app/frontend install --frozen-lockfile

# Install Playwright browsers
pnpm exec playwright install --with-deps chromium firefox webkit

# Activate Python venv
source .venv/bin/activate
```

### 2. Start Backend Services

```bash
# Start the full stack
docker-compose up -d

# Wait for services to be ready
sleep 10
```

### 3. Run Tests

```bash
# Run all E2E tests
pnpm exec playwright test

# Run specific suite
pnpm exec playwright test tests/e2e/auth.spec.ts

# Run with UI (interactive mode)
pnpm exec playwright test --ui

# Run specific browser only
pnpm exec playwright test --project=chromium

# Run local smoke and mocked journeys
make frontend-e2e-smoke
make frontend-e2e-mocked
```

---

## Test Suites

| Suite | File | Coverage |
|-------|------|----------|
| Authentication | `tests/e2e/auth.spec.ts` | Register, login, logout, refresh |
| Learner Journey | `tests/e2e/learner-vertical-journey.spec.ts` | Full learner flow |
| Diagnostic | `tests/e2e/diagnostic.spec.ts` | Assessment flow |
| Lesson Generation | `tests/e2e/lesson_generation_flow.spec.ts` | Lesson creation |
| Study Plans | `tests/e2e/study_plan_and_lesson.spec.ts` | Study plan display |
| Parent Portal | `tests/e2e/parent_portal.spec.ts` | Parent features |
| Privacy | `tests/e2e/privacy.spec.ts` | POPIA export/erasure |
| Onboarding | `tests/e2e/onboarding.spec.ts` | New user setup |

---

## Configuration

### Environment Variables

```bash
# Frontend URL (default: http://localhost:3050)
export PLAYWRIGHT_BASE_URL=http://localhost:3050

# Backend URL (for API checks)
export API_BASE_URL=http://localhost:8000

# Skip Playwright's auto-started frontend when an external stack is already running
export PLAYWRIGHT_SKIP_WEB_SERVER=1
```

### playwright.config.ts

Key settings:
- `testDir: "./tests/e2e"` — Test discovery
- `timeout: 60_000` — Per-test timeout
- `retries: 2` — Retry on CI
- `workers: 2` — Parallelism on CI
- `webServer` — Starts `pnpm --dir app/frontend exec next dev --webpack -p 3050` unless `PLAYWRIGHT_SKIP_WEB_SERVER=1`

---

## CI Integration

### GitHub Actions Workflow

Tests run automatically on:
- Every PR to `main`
- Daily schedule at 3 AM

See: `.github/workflows/e2e.yml`

### Local CI Simulation

```bash
# Run with CI-like settings
CI=true pnpm exec playwright test
```

---

## Debugging Failed Tests

### View Screenshots

Failed tests automatically capture screenshots in `test-results/`:

```bash
ls test-results/
```

### View Traces

```bash
# Open trace in Playwright UI
pnpm exec playwright show-trace test-results/<trace-file>.zip
```

### Verbose Logging

```bash
# Run with debug output
DEBUG=pw:api pnpm exec playwright test
```

---

## Writing New Tests

### Basic Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/');
    // ... test steps
  });
});
```

### Authentication Helpers

Use the setup file for authenticated tests:

```typescript
test.use({ storageState: 'tests/e2e/auth.setup.ts' });
```

### Accessibility Testing

Add axe-core assertions:

```typescript
import { injectAxe } from '@axe-core/playwright';

test('should have no a11y violations', async ({ page }) => {
  await page.goto('/');
  await injectAxe(page);
  await expect(page.locator('main')).toHaveNoA11yViolations();
});
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Test hangs | Check backend is running, increase `navigationTimeout` |
| Auth fails | Update credentials in `auth.setup.ts` |
| Flaky tests | Increase wait times, use `expect.toBeVisible()` with timeout |
| Browser not found | Run `pnpm exec playwright install --with-deps chromium firefox webkit` |

---

## Maintenance

- Update tests when routes change
- Keep `playwright.config.ts` in sync with CI
- Review and archive flaky tests
- Run full suite before release
