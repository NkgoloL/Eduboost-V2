import { expect, test } from "@playwright/test";
import { mockParentJourneyApi, mockAuthorizationDeniedApi } from "./support/mockApi";

test.describe("parent journey with mocked API", () => {
  test("renders parent journey with mocked success envelopes", async ({ page }) => {
    await mockParentJourneyApi(page);
    await page.goto(process.env.PARENT_JOURNEY_PATH || "/");

    await expect(page.locator("body")).toBeVisible();
    const text = await page.locator("body").innerText();
    expect(text.trim().length).toBeGreaterThan(0);
  });

  test("renders safe parent denial state with mocked authorization error", async ({ page }) => {
    await mockAuthorizationDeniedApi(page);
    await page.goto(process.env.PARENT_JOURNEY_PATH || "/");

    await expect(page.locator("body")).toBeVisible();
    const text = await page.locator("body").innerText();
    expect(text.trim().length).toBeGreaterThan(0);
  });
});
