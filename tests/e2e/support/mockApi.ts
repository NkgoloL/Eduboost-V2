import { Page } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

type FixtureName =
  | "learner_dashboard_success"
  | "diagnostic_submit_success"
  | "lesson_generation_success"
  | "parent_dashboard_success"
  | "consent_denied_error"
  | "authorization_denied_error";

const fixtureMap: Record<FixtureName, string> = {
  learner_dashboard_success: "learner_dashboard_success.json",
  diagnostic_submit_success: "diagnostic_submit_success.json",
  lesson_generation_success: "lesson_generation_success.json",
  parent_dashboard_success: "parent_dashboard_success.json",
  consent_denied_error: "consent_denied_error.json",
  authorization_denied_error: "authorization_denied_error.json"
};

export function loadApiFixture(name: FixtureName): unknown {
  const fixturePath = path.resolve(
    process.cwd(),
    "tests",
    "fixtures",
    "frontend",
    "api",
    fixtureMap[name]
  );

  return JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
}

export async function mockJson(page: Page, urlPattern: string | RegExp, fixtureName: FixtureName) {
  const body = loadApiFixture(fixtureName);

  await page.route(urlPattern, async (route) => {
    await route.fulfill({
      status: fixtureName.endsWith("_error") ? 403 : 200,
      contentType: "application/json",
      body: JSON.stringify(body)
    });
  });
}

export async function mockLearnerJourneyApi(page: Page) {
  await mockJson(page, /\/api\/v2\/learners\/.*dashboard|\/v2\/learners\/.*dashboard/, "learner_dashboard_success");
  await mockJson(page, /\/api\/v2\/diagnostics\/.*submit|\/v2\/diagnostics\/.*submit/, "diagnostic_submit_success");
  await mockJson(page, /\/api\/v2\/lessons\/.*generate|\/v2\/lessons\/.*generate/, "lesson_generation_success");
}

export async function mockParentJourneyApi(page: Page) {
  await mockJson(page, /\/api\/v2\/parents\/.*dashboard|\/v2\/parents\/.*dashboard/, "parent_dashboard_success");
}

export async function mockConsentDeniedApi(page: Page) {
  await mockJson(page, /\/api\/v2\/.*|\/v2\/.*/, "consent_denied_error");
}

export async function mockAuthorizationDeniedApi(page: Page) {
  await mockJson(page, /\/api\/v2\/.*|\/v2\/.*/, "authorization_denied_error");
}
