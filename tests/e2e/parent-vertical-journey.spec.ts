import { expect, test } from "@playwright/test";

test.describe("parent vertical journey", () => {
  test("loads parent journey entrypoint and exposes parent-safe UI", async ({ page }) => {
    await page.goto(process.env.PARENT_JOURNEY_PATH || "/");

    await expect(page.locator("body")).toBeVisible();

    // Smoke assertion: the live app must not render a blank shell.
    const text = await page.locator("body").innerText();
    expect(text.trim().length).toBeGreaterThan(0);
  });
});
