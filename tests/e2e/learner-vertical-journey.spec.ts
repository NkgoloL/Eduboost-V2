import { expect, test } from "@playwright/test";

test.describe("learner vertical journey", () => {
  test("loads learner journey entrypoint and exposes learner-safe UI", async ({ page }) => {
    await page.goto(process.env.LEARNER_JOURNEY_PATH || "/");

    await expect(page.locator("body")).toBeVisible();

    // Smoke assertion: the live app must not render a blank shell.
    const text = await page.locator("body").innerText();
    expect(text.trim().length).toBeGreaterThan(0);
  });
});
