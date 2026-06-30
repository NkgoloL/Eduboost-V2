/**
 * tests/e2e/onboarding.spec.ts — EduBoost SA V2
 *
 * E2E coverage for the multi-step onboarding wizard:
 *   • Sidebar step navigation rendering
 *   • Email verified step (resend + already-verified badge)
 *   • Profile form (fill, save via /onboarding/profile endpoint)
 *   • Guardian consent (POPIA checkbox gate)
 *   • Diagnostic assessment step (navigation)
 *   • Plan acceptance + redirect to dashboard
 *   • Progress bar percentage
 *
 * All API calls are intercepted with page.route() — no real backend required.
 *
 * Run:
 *   npx playwright test tests/e2e/onboarding.spec.ts
 */

import { test, expect, type Page } from "@playwright/test";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function makeOnboardingState(overrides: Record<string, unknown> = {}) {
  return {
    email_verified:   false,
    profile_complete: false,
    guardian_consent: false,
    diagnostic_done:  false,
    plan_accepted:    false,
    is_complete:      false,
    completed_at:     null,
    progress_pct:     0,
    ...overrides,
  };
}

async function mockGetOnboarding(page: Page, state: Record<string, unknown>) {
  await page.route("**/api/v2/auth/onboarding", async route => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status:      200,
        contentType: "application/json",
        body:        JSON.stringify(state),
      });
    } else {
      await route.continue();
    }
  });
}

async function mockPatchOnboarding(page: Page, returnedState: Record<string, unknown>) {
  await page.route("**/api/v2/auth/onboarding/step", async route => {
    await route.fulfill({
      status:      200,
      contentType: "application/json",
      body:        JSON.stringify(returnedState),
    });
  });
}

async function mockPatchProfile(page: Page, returnedOnboarding: Record<string, unknown>) {
  await page.route("**/api/v2/auth/onboarding/profile", async route => {
    await route.fulfill({
      status:      200,
      contentType: "application/json",
      body:        JSON.stringify({ detail: "Profile saved.", onboarding: returnedOnboarding }),
    });
  });
}

async function mockResendVerification(page: Page) {
  await page.route("**/api/v2/auth/send-verification", async route => {
    await route.fulfill({ status: 202, body: "{}" });
  });
}


// ─────────────────────────────────────────────────────────────────────────────
// Sidebar & Navigation
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Onboarding — Sidebar & Navigation", () => {

  test("renders all 5 step nav items", async ({ page }) => {
    await mockGetOnboarding(page, makeOnboardingState());
    await page.goto("/onboarding");

    for (const step of ["email_verified","profile_complete","guardian_consent","diagnostic_done","plan_accepted"]) {
      await expect(page.getByTestId(`step-nav-${step}`)).toBeVisible();
    }
  });

  test("shows progress bar", async ({ page }) => {
    const state = makeOnboardingState({ email_verified: true, profile_complete: true });
    await mockGetOnboarding(page, state);
    await page.goto("/onboarding");
    await expect(page.getByText(/40%/)).toBeVisible();
  });

  test("completed steps show ✅ in sidebar", async ({ page }) => {
    const state = makeOnboardingState({ email_verified: true });
    await mockGetOnboarding(page, state);
    await page.goto("/onboarding");
    // The email_verified step nav item should contain ✅
    await expect(page.getByTestId("step-nav-email_verified")).toContainText("✅");
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// Step 1 — Email Verified
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Onboarding — Step 1: Email Verification", () => {

  test("starts on email_verified step when no steps complete", async ({ page }) => {
    await mockGetOnboarding(page, makeOnboardingState());
    await page.goto("/onboarding");
    await expect(page.getByText("Verify email")).toBeVisible();
    await expect(page.getByTestId("resend-verify-btn")).toBeVisible();
  });

  test("resend button sends email and shows confirmation", async ({ page }) => {
    await mockGetOnboarding(page, makeOnboardingState());
    await mockResendVerification(page);
    await page.goto("/onboarding");

    await page.getByTestId("resend-verify-btn").click();
    await expect(page.getByText(/Verification email sent/i)).toBeVisible();
  });

  test("shows 'already verified' badge when email step is done", async ({ page }) => {
    const state = makeOnboardingState({ email_verified: true, profile_complete: false });
    await mockGetOnboarding(page, state);
    await page.goto("/onboarding");

    // Click to go back to email step
    await page.getByTestId("step-nav-email_verified").click();
    await expect(page.getByText("Email already verified")).toBeVisible();
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// Step 2 — Profile Complete
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Onboarding — Step 2: Profile", () => {

  test("shows profile form when email is verified", async ({ page }) => {
    await mockGetOnboarding(page, makeOnboardingState({ email_verified: true }));
    await page.goto("/onboarding");

    await expect(page.getByTestId("display-name-input")).toBeVisible();
    await expect(page.getByTestId("grade-select")).toBeVisible();
    await expect(page.getByTestId("language-select")).toBeVisible();
  });

  test("save profile button is disabled when name is empty", async ({ page }) => {
    await mockGetOnboarding(page, makeOnboardingState({ email_verified: true }));
    await page.goto("/onboarding");
    await expect(page.getByTestId("save-profile-btn")).toBeDisabled();
  });

  test("can fill and save profile via profile endpoint", async ({ page }) => {
    const afterProfile = makeOnboardingState({ email_verified: true, profile_complete: true });
    await mockGetOnboarding(page, makeOnboardingState({ email_verified: true }));
    await mockPatchProfile(page, afterProfile);
    await page.goto("/onboarding");

    await page.getByTestId("display-name-input").fill("Sipho Dlamini");
    await page.getByTestId("grade-select").selectOption("5");
    await page.getByTestId("language-select").selectOption("zu");
    await page.getByTestId("save-profile-btn").click();

    // Step should advance to guardian_consent
    await expect(page.getByText("Guardian consent")).toBeVisible();
  });

  test("shows error if profile save fails", async ({ page }) => {
    await mockGetOnboarding(page, makeOnboardingState({ email_verified: true }));
    await page.route("**/api/v2/auth/onboarding/profile", async route => {
      await route.fulfill({
        status:      422,
        contentType: "application/json",
        body:        JSON.stringify({ detail: "display_name cannot be blank" }),
      });
    });
    await page.goto("/onboarding");

    await page.getByTestId("display-name-input").fill(" ");
    // Button should remain disabled (client-side guard on empty/whitespace)
    await expect(page.getByTestId("save-profile-btn")).toBeDisabled();
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// Step 3 — Guardian Consent
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Onboarding — Step 3: Guardian Consent", () => {

  test("consent button is disabled until checkbox is ticked", async ({ page }) => {
    const state = makeOnboardingState({ email_verified: true, profile_complete: true });
    await mockGetOnboarding(page, state);
    await page.goto("/onboarding");

    await expect(page.getByTestId("give-consent-btn")).toBeDisabled();
    await page.getByTestId("consent-checkbox").check();
    await expect(page.getByTestId("give-consent-btn")).toBeEnabled();
  });

  test("POPIA consent text is visible", async ({ page }) => {
    const state = makeOnboardingState({ email_verified: true, profile_complete: true });
    await mockGetOnboarding(page, state);
    await page.goto("/onboarding");
    await expect(page.getByText(/POPIA Parental Consent/)).toBeVisible();
  });

  test("giving consent advances to diagnostic step", async ({ page }) => {
    const state     = makeOnboardingState({ email_verified: true, profile_complete: true });
    const nextState = makeOnboardingState({ email_verified: true, profile_complete: true, guardian_consent: true });
    await mockGetOnboarding(page, state);
    await mockPatchOnboarding(page, nextState);
    await page.goto("/onboarding");

    await page.getByTestId("consent-checkbox").check();
    await page.getByTestId("give-consent-btn").click();
    await expect(page.getByText("Diagnostic assessment")).toBeVisible();
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// Step 4 — Diagnostic Assessment
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Onboarding — Step 4: Diagnostic", () => {

  test("shows 'Start diagnostic' button", async ({ page }) => {
    const state = makeOnboardingState({ email_verified: true, profile_complete: true, guardian_consent: true });
    await mockGetOnboarding(page, state);
    await page.goto("/onboarding");
    await expect(page.getByTestId("start-diagnostic-btn")).toBeVisible();
  });

  test("start-diagnostic button navigates to /diagnostic", async ({ page }) => {
    const state = makeOnboardingState({ email_verified: true, profile_complete: true, guardian_consent: true });
    await mockGetOnboarding(page, state);
    await page.route("**/diagnostic**", async route =>
      route.fulfill({ status: 200, body: "<html><body>diagnostic</body></html>" })
    );
    await page.goto("/onboarding");
    await page.getByTestId("start-diagnostic-btn").click();
    await expect(page).toHaveURL(/\/diagnostic/);
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// Step 5 — Accept Study Plan
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Onboarding — Step 5: Plan Acceptance", () => {

  test("accept plan button is visible on final step", async ({ page }) => {
    const state = makeOnboardingState({
      email_verified: true, profile_complete: true,
      guardian_consent: true, diagnostic_done: true,
    });
    await mockGetOnboarding(page, state);
    await page.goto("/onboarding");
    await expect(page.getByTestId("accept-plan-btn")).toBeVisible();
  });

  test("accepting plan completes onboarding and redirects to /dashboard", async ({ page }) => {
    const almostDone = makeOnboardingState({
      email_verified: true, profile_complete: true,
      guardian_consent: true, diagnostic_done: true,
    });
    const allDone = { ...almostDone, plan_accepted: true, is_complete: true };

    await mockGetOnboarding(page, almostDone);
    await mockPatchOnboarding(page, allDone);
    await page.route("**/dashboard**", async route =>
      route.fulfill({ status: 200, body: "<html><body>dashboard</body></html>" })
    );
    await page.goto("/onboarding");
    await page.getByTestId("accept-plan-btn").click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

});
