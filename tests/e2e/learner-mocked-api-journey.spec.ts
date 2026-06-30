import { expect, test } from "@playwright/test";
import { mockLearnerJourneyApi, mockConsentDeniedApi } from "./support/mockApi";

test.describe("learner journey with mocked API", () => {
  test("renders learner journey with mocked success envelopes", async ({ page }) => {
    await mockLearnerJourneyApi(page);
    await page.goto(process.env.LEARNER_JOURNEY_PATH || "/");

    await expect(page.locator("body")).toBeVisible();
    const text = await page.locator("body").innerText();
    expect(text.trim().length).toBeGreaterThan(0);
  });

  test("renders safe learner denial state with mocked consent error", async ({ page }) => {
    await mockConsentDeniedApi(page);
    await page.goto(process.env.LEARNER_JOURNEY_PATH || "/");

    await expect(page.locator("body")).toBeVisible();
    const text = await page.locator("body").innerText();
    expect(text.trim().length).toBeGreaterThan(0);
  });
});
