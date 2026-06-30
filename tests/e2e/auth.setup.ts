import { test as setup, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const AUTH_DIR = path.join(__dirname, "../../playwright/.auth");
const STATE_FILE = path.join(AUTH_DIR, "guardian.json");
const FIXTURE_FILE = path.join(AUTH_DIR, "fixtures.json");
const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000/api/v2";

setup("create dev learner session", async ({ page, request }) => {
  fs.mkdirSync(AUTH_DIR, { recursive: true });

  const response = await request.post(`${API_BASE_URL}/auth/dev-session`);
  expect(response.ok()).toBeTruthy();
  const envelope = await response.json();
  const session = envelope.data ?? envelope;
  const learner = session.learner;
  expect(learner).toBeTruthy();

  await page.goto("/");
  await page.evaluate(
    ({ token, guardianId, activeLearner }) => {
      window.localStorage.setItem("guardian_token", token);
      window.localStorage.setItem("guardian_id", guardianId);
      window.localStorage.setItem("eb_active_learner", JSON.stringify(activeLearner));
    },
    {
      token: session.access_token,
      guardianId: session.guardian_id,
      activeLearner: learner,
    }
  );

  await page.context().storageState({ path: STATE_FILE });
  fs.writeFileSync(
    FIXTURE_FILE,
    JSON.stringify(
      {
        accessToken: session.access_token,
        guardianId: session.guardian_id,
        learnerId: learner.learner_id ?? learner.id,
        learnerName: learner.display_name ?? learner.nickname ?? "Dev learner",
        learner,
      },
      null,
      2
    )
  );
});
