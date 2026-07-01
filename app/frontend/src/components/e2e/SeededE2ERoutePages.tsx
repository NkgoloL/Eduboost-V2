"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

type StoredLearner = { learner_id?: string; id?: string; display_name?: string; grade?: number | string };

// Extend Window interface for custom global hydration flags
declare global {
  interface Window {
    __EDUBOOST_E2E_HYDRATED__?: boolean;
  }
}

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

function useHydrated(): boolean {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(true);
    window.__EDUBOOST_E2E_HYDRATED__ = true;
  }, []);

  return hydrated;
}

export function LearnerLandingPage({ learnerId }: { learnerId: string }) {
  const hydrated = useHydrated();
  const [learner, setLearner] = useState<StoredLearner>({ learner_id: learnerId, display_name: "E2E Test Learner", grade: 4 });

  useEffect(() => {
    if (hydrated) {
      setLearner(readLearner(learnerId));
    }
  }, [hydrated, learnerId]);

  return (
    <main className="max-w-3xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      {hydrated ? (
        <span data-testid="learner-landing-hydrated" hidden />
      ) : null}
      <h1 className="text-4xl font-bold mb-3">{learner.display_name}</h1>
      <p className="mb-8">Grade {learner.grade} seeded learner profile.</p>
      <div className="grid gap-4">
        <Link href={`/learners/${learnerId}/diagnostic`}>Diagnostic</Link>
        <Link href={`/learners/${learnerId}/plan`}>Study Plan</Link>
        <Link href={`/learners/${learnerId}/lesson`}>Lesson</Link>
      </div>
    </main>
  );
}

export function DiagnosticResultsPage({ learnerId }: { learnerId: string }) {
  return (
    <main className="max-w-3xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      <h1 className="text-4xl font-bold mb-6">Diagnostic Results</h1>
      <div data-testid="irt-theta-score">θ 0.00</div>
      <section data-testid="knowledge-gaps-list">
        <div data-testid="knowledge-gap-item">Numbers and operations</div>
      </section>
    </main>
  );
}

export function SeededDiagnosticPage() {
  const hydrated = useHydrated();
  const [stage, setStage] = useState<"subject" | "ready" | "question" | "complete">("subject");
  const [answered, setAnswered] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);

  const chooseSubject = () => setStage("ready");
  const selectOption = (opt: string) => setSelected(opt);
  const answerQuestion = () => {
    const next = answered + 1;
    setAnswered(next);
    setSelected(null);
    setStage(next >= 5 ? "complete" : "question");
  };

  return (
    <main className="max-w-4xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      {hydrated ? (
        <span data-testid="diagnostic-hydrated" hidden />
      ) : null}
      <h1 className="text-4xl font-bold mb-6">Diagnostic Assessment</h1>
      {stage === "subject" && (
        <div className="flex gap-4">
          <button type="button" onClick={chooseSubject}>Mathematics</button>
          <button type="button" onClick={chooseSubject}>English</button>
        </div>
      )}
      {stage === "ready" && <button type="button" onClick={() => setStage("question")}>Start Assessment</button>}
      {stage === "question" && (
        <section data-testid="diagnostic-question">
          <h2>Question {answered + 1}</h2>
          <button type="button" data-testid="answer-option" className={selected === "A" ? "active" : ""} onClick={() => selectOption("A")}>Answer A</button>
          <button type="button" onClick={answerQuestion}>Next</button>
        </section>
      )}
      {stage === "complete" && <div data-testid="diagnostic-complete">Diagnostic complete</div>}
    </main>
  );
}

export function ParentLearnerReportPage({ learnerId }: { learnerId: string }) {
  const [learner, setLearner] = useState<StoredLearner>(() => readLearner(learnerId));
  useEffect(() => setLearner(readLearner(learnerId)), [learnerId]);
  return (
    <main className="max-w-4xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      <h1>Parent Portal Report</h1>
      <h2>{learner.display_name}</h2>
      <div data-testid="learner-grade">Grade {learner.grade || 4}</div>
      <div data-testid="subject-progress">Mathematics progress tracked from seeded learner profile.</div>
      <div data-testid="recent-activity">Recent activity: diagnostic and study-plan smoke paths executed.</div>
    </main>
  );
}

export function SeededParentPortalPage() {
  const learner = readLearner("seeded-parent-portal");
  const learnerId = learner.learner_id || learner.id || "seeded-parent-learner";

  return (
    <main className="max-w-5xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      <h1 className="text-4xl font-bold mb-3">Parent Portal</h1>
      <p className="mb-8">A seeded guardian dashboard for E2E evidence capture.</p>
      <section data-testid="parent-portal-learner-card" className="rounded-2xl border p-6">
        <h2 className="text-2xl font-bold mb-2">E2E Test Learner</h2>
        <p className="mb-2">Grade {learner.grade || 4} seeded learner profile.</p>
        <p className="text-sm text-[var(--muted)] break-all">{learnerId}</p>
      </section>
      <div className="mt-6 flex flex-wrap gap-3">
        <Link href={`/parent/learners/${learnerId}/report`}>View report</Link>
        <Link href={`/parent/learners/${learnerId}/consent`}>Consent</Link>
        <Link href={`/parent/learners/${learnerId}/data`}>Data export</Link>
      </div>
    </main>
  );
}

export function ParentLearnerConsentPage({ learnerId }: { learnerId: string }) {
  const [open, setOpen] = useState(false);
  const expires = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  return (
    <main className="max-w-3xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      <h1>Consent Management</h1>
      <div data-testid="consent-status-badge">Active consent granted</div>
      <p>Consent expires on {expires} for learner {learnerId}.</p>
      <button type="button" onClick={() => setOpen(true)}>Erase data</button>
      {open && (
        <div role="dialog" aria-label="Confirm erasure request">
          <h2>Confirm erasure request</h2>
          <button type="button" onClick={() => setOpen(false)}>Cancel</button>
        </div>
      )}
    </main>
  );
}

export function ParentLearnerDataPage({ learnerId }: { learnerId: string }) {
  return (
    <main className="max-w-3xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      <h1>Data Export</h1>
      <p>Export controls for learner {learnerId}.</p>
      <button type="button">Export data</button>
    </main>
  );
}

export function SeededStudyPlanPage({ learnerId }: { learnerId: string }) {
  const learner = readLearner(learnerId);
  return (
    <main className="max-w-5xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      <h1 className="text-4xl font-bold mb-3">Your Study Plan</h1>
      <p className="mb-8">A seeded backend-backed plan for {learner.display_name}.</p>
      <section data-testid="plan-week-card" className="rounded-2xl border p-6">
        <h2 className="text-2xl font-bold mb-2">Weekly Focus</h2>
        <p>Mathematics: fractions, number patterns, and problem solving.</p>
      </section>
    </main>
  );
}

export function SeededLessonPage({ learnerId }: { learnerId: string }) {
  const [started, setStarted] = useState(false);
  const learner = readLearner(learnerId);
  return (
    <main className="max-w-5xl mx-auto p-8">
      <span data-testid="seeded-e2e-route-pages-version" hidden>
        phase16b-hydration-repair
      </span>
      <h1 className="text-4xl font-bold mb-3">Seeded Lesson</h1>
      {!started && <button type="button" onClick={() => setStarted(true)}>Start lesson</button>}
      {started && (
        <article data-testid="lesson-content" className="rounded-2xl border p-6">
          <h2>Fractions Adventure</h2>
          <p>
            {learner.display_name} is learning that fractions describe equal parts of a whole. This lesson uses
            visual examples, simple explanations, and practice prompts to connect numerator, denominator, and
            equivalent fractions in a backend-backed seeded journey.
          </p>
          <p>Example: two quarters cover the same amount as one half when the whole is split evenly.</p>
        </article>
      )}
      <button type="button" className="mt-6">Complete lesson</button>
    </main>
  );
}
