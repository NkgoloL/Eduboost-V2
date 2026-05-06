import type { MasteryResponse } from "../../lib/api/types";

export async function getLearnerMasteryAPI(learnerId: string): Promise<MasteryResponse> {
  const res = await fetch(`/api/v2/learners/${learnerId}/mastery`);
  return res.json();
}

export async function runDiagnosticAPI(learnerId: string, opts: Record<string, unknown>) {
  const res = await fetch(`/api/v2/diagnostics/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ learner_id: learnerId, ...opts }),
  });
  return res.json();
}

export async function awardXPAPI(learnerId: string, xp: number) {
  const res = await fetch(`/api/v2/gamification/award-xp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ learner_id: learnerId, xp_amount: xp }),
  });
  return res.json();
}

export async function getLearnerProfileAPI(learnerId: string) {
  const res = await fetch(`/api/v2/learners/${learnerId}`);
  return res.json();
}
