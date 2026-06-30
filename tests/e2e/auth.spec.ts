/**
 * tests/e2e/auth.spec.ts — EduBoost SA V2
 *
 * Browser E2E coverage:
 *   • Password Reset (request → sent → token reset → success / error paths)
 *   • Email Verification (auto-verify → success / error / resend / navigation)
 *
 * All API calls are intercepted with page.route() — tests are self-contained:
 * no real SendGrid, no real database required.
 *
 * Run: npx playwright test tests/e2e/auth.spec.ts
 *
 * Playwright config expected at: playwright.config.ts
 *   baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000"
 */

import { test, expect, type Page } from "@playwright/test";

// ─────────────────────────────────────────────────────────────────────────────
// Mock helpers
// ─────────────────────────────────────────────────────────────────────────────

async function mockForgotPassword(page: Page) {
  await page.route("**/api/v2/auth/forgot-password", async route => {
    await route.fulfill({
      status:      202,
      contentType: "application/json",
      body:        JSON.stringify({ detail: "If that email exists, a reset link has been sent." }),
    });
  });
}

async function mockResetPassword(page: Page, succeed = true) {
  await page.route("**/api/v2/auth/reset-password", async route => {
    if (succeed) {
      await route.fulfill({
        status:      200,
        contentType: "application/json",
        body:        JSON.stringify({ detail: "Password updated successfully." }),
      });
    } else {
      await route.fulfill({
        status:      400,
        contentType: "application/json",
        body:        JSON.stringify({ detail: "Invalid or expired token." }),
      });
    }
  });
}

async function mockVerifyEmail(page: Page, succeed = true) {
  await page.route("**/api/v2/auth/verify-email**", async route => {
    if (succeed) {
      await route.fulfill({
        status:      200,
        contentType: "application/json",
        body:        JSON.stringify({ detail: "Email verified successfully." }),
      });
    } else {
      await route.fulfill({
        status:      400,
        contentType: "application/json",
        body:        JSON.stringify({ detail: "Invalid or expired token." }),
      });
    }
  });
}

async function mockResendVerification(page: Page) {
  await page.route("**/api/v2/auth/send-verification", async route => {
    await route.fulfill({
      status:      202,
      contentType: "application/json",
      body:        JSON.stringify({ detail: "Verification email sent." }),
    });
  });
}


// ─────────────────────────────────────────────────────────────────────────────
// Password Reset
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Password Reset", () => {

  test("shows forgot-password form on /auth/reset-password", async ({ page }) => {
    await page.goto("/auth/reset-password");
    await expect(page.getByTestId("forgot-form")).toBeVisible();
    await expect(page.getByTestId("email-input")).toBeVisible();
    await expect(page.getByTestId("submit-btn")).toBeVisible();
  });

  test("submitting a valid email shows 'Check your inbox' screen", async ({ page }) => {
    await mockForgotPassword(page);
    await page.goto("/auth/reset-password");

    await page.getByTestId("email-input").fill("learner@school.co.za");
    await page.getByTestId("submit-btn").click();

    await expect(page.getByTestId("sent-message")).toBeVisible();
    await expect(page.getByText("Check your inbox")).toBeVisible();
  });

  test("submit button is disabled while request is in-flight", async ({ page }) => {
    await page.route("**/api/v2/auth/forgot-password", async route => {
      await new Promise(r => setTimeout(r, 400));
      await route.fulfill({ status: 202, body: "{}" });
    });

    await page.goto("/auth/reset-password");
    await page.getByTestId("email-input").fill("test@example.com");
    await page.getByTestId("submit-btn").click();

    await expect(page.getByTestId("submit-btn")).toBeDisabled();
  });

  test("shows 'Check your inbox' even for unregistered email (anti-enumeration)", async ({ page }) => {
    await mockForgotPassword(page); // always 202
    await page.goto("/auth/reset-password");

    await page.getByTestId("email-input").fill("nobody@notregistered.co.za");
    await page.getByTestId("submit-btn").click();

    await expect(page.getByTestId("sent-message")).toBeVisible();
  });

  test("'Use a different email' resets to request form", async ({ page }) => {
    await mockForgotPassword(page);
    await page.goto("/auth/reset-password");

    await page.getByTestId("email-input").fill("learner@school.co.za");
    await page.getByTestId("submit-btn").click();
    await expect(page.getByTestId("sent-message")).toBeVisible();

    await page.getByText("Use a different email").click();
    await expect(page.getByTestId("forgot-form")).toBeVisible();
  });

  test("shows reset form (new password inputs) when token is in URL", async ({ page }) => {
    await page.goto("/auth/reset-password?token=MOCK_TOKEN_ABC");
    await expect(page.getByTestId("reset-form")).toBeVisible();
    await expect(page.getByTestId("password-input")).toBeVisible();
    await expect(page.getByTestId("confirm-input")).toBeVisible();
    await expect(page.getByTestId("reset-btn")).toBeVisible();
  });

  test("password strength meter updates as user types", async ({ page }) => {
    await page.goto("/auth/reset-password?token=MOCK");
    await page.getByTestId("password-input").fill("Str0ng!");
    await expect(page.locator("text=/Weak|Fair|Good|Strong/")).toBeVisible();
  });

  test("strength meter is absent when password field is empty", async ({ page }) => {
    await page.goto("/auth/reset-password?token=MOCK");
    // Meter only renders when password has content
    await expect(page.locator("text=/Very Strong/")).not.toBeVisible();
  });

  test("shows error if passwords do not match", async ({ page }) => {
    await page.goto("/auth/reset-password?token=MOCK");
    await page.getByTestId("password-input").fill("ValidPass1");
    await page.getByTestId("confirm-input").fill("DifferentPass1");
    await page.getByTestId("reset-btn").click();
    await expect(page.getByText("Passwords do not match")).toBeVisible();
  });

  test("shows error if password is too weak (strength < 3)", async ({ page }) => {
    await page.goto("/auth/reset-password?token=MOCK");
    await page.getByTestId("password-input").fill("password");  // no upper / digit
    await page.getByTestId("confirm-input").fill("password");
    await page.getByTestId("reset-btn").click();
    await expect(page.getByText(/stronger password/i)).toBeVisible();
  });

  test("successful reset shows success screen", async ({ page }) => {
    await mockResetPassword(page, true);
    await page.goto("/auth/reset-password?token=MOCK_TOKEN");

    await page.getByTestId("password-input").fill("NewPass1!");
    await page.getByTestId("confirm-input").fill("NewPass1!");
    await page.getByTestId("reset-btn").click();

    await expect(page.getByTestId("success-message")).toBeVisible();
    await expect(page.getByText("Password updated")).toBeVisible();
  });

  test("invalid / expired token shows error message", async ({ page }) => {
    await mockResetPassword(page, false);
    await page.goto("/auth/reset-password?token=EXPIRED");

    await page.getByTestId("password-input").fill("NewPass1!");
    await page.getByTestId("confirm-input").fill("NewPass1!");
    await page.getByTestId("reset-btn").click();

    await expect(page.getByText("Invalid or expired token")).toBeVisible();
  });

  test("reset button is disabled while submitting", async ({ page }) => {
    await page.route("**/api/v2/auth/reset-password", async route => {
      await new Promise(r => setTimeout(r, 400));
      await route.fulfill({ status: 200, body: "{}" });
    });

    await page.goto("/auth/reset-password?token=MOCK");
    await page.getByTestId("password-input").fill("NewPass1!");
    await page.getByTestId("confirm-input").fill("NewPass1!");
    await page.getByTestId("reset-btn").click();

    await expect(page.getByTestId("reset-btn")).toBeDisabled();
  });

  test("'Back to login' link is present on request step", async ({ page }) => {
    await page.goto("/auth/reset-password");
    const link = page.getByRole("link", { name: /back to login/i });
    await expect(link).toBeVisible();
    await expect(link).toHaveAttribute("href", "/auth/login");
  });

  test("'Log in' button on success screen navigates to /auth/login", async ({ page }) => {
    await mockResetPassword(page, true);
    await page.goto("/auth/reset-password?token=MOCK");

    await page.getByTestId("password-input").fill("NewPass1!");
    await page.getByTestId("confirm-input").fill("NewPass1!");
    await page.getByTestId("reset-btn").click();
    await expect(page.getByTestId("success-message")).toBeVisible();

    await page.getByRole("button", { name: /log in/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/);
  });
});


// ─────────────────────────────────────────────────────────────────────────────
// Email Verification
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Email Verification", () => {

  test("auto-verifies and shows success when token is valid", async ({ page }) => {
    await mockVerifyEmail(page, true);
    await page.goto("/auth/verify-email?token=VALID_TOKEN");

    await expect(page.getByTestId("verify-success")).toBeVisible();
    await expect(page.getByText("Email verified")).toBeVisible();
    await expect(page.getByTestId("continue-btn")).toBeVisible();
  });

  test("shows error state when token is invalid/expired", async ({ page }) => {
    await mockVerifyEmail(page, false);
    await page.goto("/auth/verify-email?token=EXPIRED_TOKEN");

    await expect(page.getByTestId("verify-error")).toBeVisible();
    await expect(page.getByTestId("resend-btn")).toBeVisible();
    await expect(page.getByText("Invalid or expired token")).toBeVisible();
  });

  test("shows error when no token is in URL", async ({ page }) => {
    await page.goto("/auth/verify-email");
    await expect(page.getByTestId("verify-error")).toBeVisible();
    await expect(page.getByText(/No verification token/i)).toBeVisible();
  });

  test("resend-btn requests a new verification email", async ({ page }) => {
    await mockVerifyEmail(page, false);
    await mockResendVerification(page);

    await page.goto("/auth/verify-email?token=BAD");
    await page.getByTestId("resend-btn").click();

    await expect(page.getByTestId("resent-message")).toBeVisible();
    await expect(page.getByText("Email sent")).toBeVisible();
  });

  test("resend button is disabled while sending", async ({ page }) => {
    await mockVerifyEmail(page, false);
    await page.route("**/api/v2/auth/send-verification", async route => {
      await new Promise(r => setTimeout(r, 400));
      await route.fulfill({ status: 202, body: "{}" });
    });

    await page.goto("/auth/verify-email?token=BAD");
    await page.getByTestId("resend-btn").click();

    await expect(page.getByTestId("resend-btn")).toBeDisabled();
  });

  test("continue-btn navigates to /onboarding after successful verification", async ({ page }) => {
    await mockVerifyEmail(page, true);
    // Mock the onboarding page so navigation can complete
    await page.route("**/onboarding**", async route =>
      route.fulfill({ status: 200, body: "<html><body>onboarding</body></html>" })
    );
    await page.goto("/auth/verify-email?token=VALID");
    await page.getByTestId("continue-btn").click();
    await expect(page).toHaveURL(/\/onboarding/);
  });

  test("'Back to login' link is present on error state", async ({ page }) => {
    await mockVerifyEmail(page, false);
    await page.goto("/auth/verify-email?token=BAD");

    const link = page.getByRole("link", { name: /back to login/i });
    await expect(link).toBeVisible();
    await expect(link).toHaveAttribute("href", "/auth/login");
  });

  test("shows loading/verifying state before API responds", async ({ page }) => {
    let resolveRoute!: () => void;
    await page.route("**/api/v2/auth/verify-email**", async route => {
      await new Promise<void>(r => { resolveRoute = r; });
      await route.fulfill({ status: 200, body: "{}" });
    });

    await page.goto("/auth/verify-email?token=SLOW");
    // Verifying spinner text visible before route resolves
    await expect(page.getByText(/Verifying/i)).toBeVisible();
    resolveRoute();
    // After resolution, success state should appear
    await expect(page.getByTestId("verify-success")).toBeVisible();
  });
});
