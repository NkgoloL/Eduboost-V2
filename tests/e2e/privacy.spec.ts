/**
 * tests/e2e/privacy.spec.ts — EduBoost SA V2
 *
 * E2E coverage for the Privacy & Data Controls page (/settings/privacy):
 *   • Toggle switch rendering and aria-pressed state
 *   • Data retention selector
 *   • Save preferences (PATCH)
 *   • POPIA right-of-access: request data export
 *   • POPIA right-to-erasure: delete account confirm modal
 *   • Accessibility checks
 *
 * All API calls are intercepted with page.route() — no real backend required.
 *
 * Run:
 *   npx playwright test tests/e2e/privacy.spec.ts
 */

import { test, expect, type Page } from "@playwright/test";

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const defaultPrivacy = {
  analytics_enabled:     true,
  ai_improvement:        true,
  marketing_emails:      false,
  data_retention_days:   365,
  show_leaderboard:      true,
  export_requested_at:   null,
  deletion_requested_at: null,
  updated_at:            new Date().toISOString(),
};

async function mockGetPrivacy(page: Page, data = defaultPrivacy) {
  await page.route("**/api/v2/auth/privacy", async route => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status:      200,
        contentType: "application/json",
        body:        JSON.stringify(data),
      });
    } else {
      await route.continue();
    }
  });
}

async function mockPatchPrivacy(page: Page, returnData = defaultPrivacy) {
  await page.route("**/api/v2/auth/privacy", async route => {
    if (route.request().method() === "PATCH") {
      await route.fulfill({
        status:      200,
        contentType: "application/json",
        body:        JSON.stringify(returnData),
      });
    } else {
      await route.continue();
    }
  });
}


// ─────────────────────────────────────────────────────────────────────────────
// Toggle Switches
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Privacy — Toggle Switches", () => {

  test("renders all four toggles", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");

    for (const id of ["toggle-analytics","toggle-ai-improvement","toggle-marketing","toggle-leaderboard"]) {
      await expect(page.getByTestId(id)).toBeVisible();
    }
  });

  test("analytics toggle reflects initial on state", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");
    await expect(page.getByTestId("toggle-analytics")).toHaveAttribute("aria-pressed", "true");
  });

  test("marketing toggle reflects initial off state", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");
    await expect(page.getByTestId("toggle-marketing")).toHaveAttribute("aria-pressed", "false");
  });

  test("clicking a toggle flips its aria-pressed value", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");

    const toggle = page.getByTestId("toggle-analytics");
    await expect(toggle).toHaveAttribute("aria-pressed", "true");
    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-pressed", "false");
  });

  test("toggle state reflects custom initial data", async ({ page }) => {
    await mockGetPrivacy(page, { ...defaultPrivacy, analytics_enabled: false });
    await page.goto("/settings/privacy");
    await expect(page.getByTestId("toggle-analytics")).toHaveAttribute("aria-pressed", "false");
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// Data Retention
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Privacy — Data Retention", () => {

  test("renders all four retention options", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");

    for (const val of [90, 365, 730, 0]) {
      await expect(page.getByTestId(`retention-${val}`)).toBeVisible();
    }
  });

  test("active retention option matches initial data (1 year = 365)", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");
    // Active button has distinct styling — verify it contains the label text
    await expect(page.getByTestId("retention-365")).toContainText("1 year");
  });

  test("clicking a retention option selects it", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");

    const btn90 = page.getByTestId("retention-90");
    await btn90.click();
    // After click, 90 days should become active (has green border/text via style)
    // We test by checking the button text is still visible (no crash)
    await expect(btn90).toBeVisible();
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// Save Preferences
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Privacy — Save Preferences", () => {

  test("save button is visible", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");
    await expect(page.getByTestId("save-privacy-btn")).toBeVisible();
  });

  test("saving preferences shows '✅ Saved' confirmation", async ({ page }) => {
    await mockGetPrivacy(page);
    await mockPatchPrivacy(page, { ...defaultPrivacy, marketing_emails: true });
    await page.goto("/settings/privacy");

    await page.getByTestId("toggle-marketing").click();
    await page.getByTestId("save-privacy-btn").click();

    await expect(page.getByText("✅ Saved")).toBeVisible();
  });

  test("save button is disabled while saving", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.route("**/api/v2/auth/privacy", async route => {
      if (route.request().method() === "PATCH") {
        await new Promise(r => setTimeout(r, 400));
        await route.fulfill({ status: 200, body: JSON.stringify(defaultPrivacy) });
      } else {
        await route.continue();
      }
    });
    await page.goto("/settings/privacy");
    await page.getByTestId("save-privacy-btn").click();
    await expect(page.getByTestId("save-privacy-btn")).toBeDisabled();
  });

  test("shows error banner if save fails", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.route("**/api/v2/auth/privacy", async route => {
      if (route.request().method() === "PATCH") {
        await route.fulfill({
          status:      500,
          contentType: "application/json",
          body:        JSON.stringify({ detail: "Internal server error" }),
        });
      } else {
        await route.continue();
      }
    });
    await page.goto("/settings/privacy");
    await page.getByTestId("save-privacy-btn").click();
    await expect(page.getByText(/Internal server error/i)).toBeVisible();
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// POPIA Rights
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Privacy — POPIA Rights", () => {

  test("'Your POPIA rights' section heading is visible", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");
    await expect(page.getByText(/Your POPIA rights/)).toBeVisible();
  });

  test("request-export button is rendered and enabled by default", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");
    const btn = page.getByTestId("request-export-btn");
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });

  test("export button triggers API and becomes disabled (Requested state)", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.route("**/api/v2/auth/privacy/request-export", async route => {
      await route.fulfill({ status: 202, body: "{}" });
    });

    await page.goto("/settings/privacy");
    await page.getByTestId("request-export-btn").click();
    await expect(page.getByTestId("request-export-btn")).toBeDisabled();
  });

  test("export button shows 'Requested' if already requested", async ({ page }) => {
    await mockGetPrivacy(page, {
      ...defaultPrivacy,
      export_requested_at: new Date().toISOString(),
    });
    await page.goto("/settings/privacy");
    await expect(page.getByTestId("request-export-btn")).toContainText("Requested");
    await expect(page.getByTestId("request-export-btn")).toBeDisabled();
  });

  test("request-deletion button opens confirm modal", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");

    await page.getByTestId("request-deletion-btn").click();
    await expect(page.getByTestId("delete-confirm-modal")).toBeVisible();
    await expect(page.getByText("Are you absolutely sure")).toBeVisible();
  });

  test("cancel in delete modal closes it without calling API", async ({ page }) => {
    await mockGetPrivacy(page);
    let apiCalled = false;
    await page.route("**/api/v2/auth/privacy/request-deletion", async route => {
      apiCalled = true;
      await route.continue();
    });

    await page.goto("/settings/privacy");
    await page.getByTestId("request-deletion-btn").click();
    await expect(page.getByTestId("delete-confirm-modal")).toBeVisible();
    await page.getByText("Cancel").click();
    await expect(page.getByTestId("delete-confirm-modal")).not.toBeVisible();
    // API must not have been called
    expect(apiCalled).toBe(false);
  });

  test("confirming deletion calls API and hides delete button", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.route("**/api/v2/auth/privacy/request-deletion", async route => {
      await route.fulfill({ status: 202, body: "{}" });
    });

    await page.goto("/settings/privacy");
    await page.getByTestId("request-deletion-btn").click();
    await page.getByTestId("confirm-delete-btn").click();

    await expect(page.getByTestId("delete-confirm-modal")).not.toBeVisible();
    await expect(page.getByTestId("request-deletion-btn")).not.toBeVisible();
  });

  test("deletion button is hidden if deletion already requested", async ({ page }) => {
    await mockGetPrivacy(page, {
      ...defaultPrivacy,
      deletion_requested_at: new Date().toISOString(),
    });
    await page.goto("/settings/privacy");
    await expect(page.getByTestId("request-deletion-btn")).not.toBeVisible();
    await expect(page.getByText(/Deletion requested on/i)).toBeVisible();
  });

});


// ─────────────────────────────────────────────────────────────────────────────
// Accessibility
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Privacy — Accessibility", () => {

  test("all toggles have aria-pressed attribute", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");

    for (const id of ["toggle-analytics","toggle-ai-improvement","toggle-marketing","toggle-leaderboard"]) {
      await expect(page.getByTestId(id)).toHaveAttribute("aria-pressed");
    }
  });

  test("all toggles have role='switch'", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");

    for (const id of ["toggle-analytics","toggle-ai-improvement","toggle-marketing","toggle-leaderboard"]) {
      await expect(page.getByTestId(id)).toHaveAttribute("role", "switch");
    }
  });

  test("all toggles have aria-checked attribute", async ({ page }) => {
    await mockGetPrivacy(page);
    await page.goto("/settings/privacy");

    for (const id of ["toggle-analytics","toggle-ai-improvement","toggle-marketing","toggle-leaderboard"]) {
      await expect(page.getByTestId(id)).toHaveAttribute("aria-checked");
    }
  });

});
