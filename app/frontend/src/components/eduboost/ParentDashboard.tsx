"use client";

import React, { useEffect, useMemo, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import { DataRightsService, ParentService } from "../../lib/api/services";
import { extractErrorMessage } from "../../lib/api/client";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Stars } from "./EntryScreens";
import type { ParentExportBundle, ParentTrustDashboardLearner, ParentTrustDashboardResponse } from "../../lib/api/types";

interface ParentDashboardProps {
  onBack: () => void;
}

export function ParentDashboard({ onBack }: ParentDashboardProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dashboard, setDashboard] = useState<ParentTrustDashboardResponse | null>(null);
  const [exportBundle, setExportBundle] = useState<ParentExportBundle | null>(null);
  const [privacyStatus, setPrivacyStatus] = useState<Record<string, string>>({});

  useEffect(() => {
    const guardianId = typeof window !== "undefined" ? localStorage.getItem("guardian_id") : null;
    if (!guardianId) {
      setError("Parent access requires a guardian session.");
      setLoading(false);
      return;
    }

    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const [dashboardData, exportData] = await Promise.all([
          ParentService.getTrustDashboard(guardianId),
          ParentService.getExportBundle(guardianId),
        ]);
        setDashboard(dashboardData);
        setExportBundle(exportData);
      } catch (err) {
        const detail = extractErrorMessage(err, "");
        setError(
          detail && detail !== "Failed to load the parent dashboard."
            ? `Failed to load the parent dashboard. ${detail}`
            : "Failed to load the parent dashboard."
        );
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);


  const runDataRightsAction = async (learnerId: string, action: "export" | "restrict" | "erase") => {
    setPrivacyStatus((current) => ({ ...current, [learnerId]: "Submitting privacy request..." }));
    try {
      if (action === "export") {
        const bundle = await DataRightsService.exportLearner(learnerId, "json");
        setPrivacyStatus((current) => ({ ...current, [learnerId]: `Export ready: ${bundle.filename}` }));
      } else if (action === "restrict") {
        await DataRightsService.restrictProcessing(learnerId, "guardian_requested_from_dashboard");
        setPrivacyStatus((current) => ({ ...current, [learnerId]: "Processing restricted. Optional learner processing is paused." }));
      } else {
        await DataRightsService.requestErasure(learnerId, "guardian_requested_from_dashboard");
        setPrivacyStatus((current) => ({ ...current, [learnerId]: "Erasure request submitted for review." }));
      }
    } catch (err) {
      setPrivacyStatus((current) => ({ ...current, [learnerId]: extractErrorMessage(err, "Privacy request failed") }));
    }
  };

  const chartData = useMemo(
    () =>
      (dashboard?.learners || []).map((learner) => ({
        name: learner.display_name,
        completion: learner.lesson_completion_rate_7d,
        streak: learner.streak_days,
      })),
    [dashboard?.learners]
  );

  return (
    <main id="main-content" className="screen min-h-screen bg-[var(--bg)] p-6 overflow-y-auto">
      <Stars />
      <div className="relative z-10 max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-['Baloo_2'] text-white">Parent Trust Dashboard</h1>
            <p className="text-blue-100">Progress summaries, knowledge gaps, and export links for your learners.</p>
          </div>
          <Button variant="secondary" onClick={onBack}>Return to App</Button>
        </div>

        {error && <div className="bg-red-500/20 text-red-200 p-4 rounded-xl mb-6 border border-red-500/30">{error}</div>}

        {loading ? (
          <div className="py-20 text-center text-blue-200">Loading dashboard...</div>
        ) : !dashboard || dashboard.learners.length === 0 ? (
          <Card className="p-10 bg-white/10 border-white/10 text-center text-blue-50">
            No active learners were found for this guardian yet.
          </Card>
        ) : (
          <>
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
              <Card className="xl:col-span-2 p-6 bg-[var(--surface2)]/70 border-[var(--border)] shadow-2xl">
                <h2 className="text-xl font-bold text-white mb-4">7-Day Completion Trend</h2>
                <p className="sr-only">Bar chart showing recent lesson completion for each learner.</p>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="completion" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>

              <Card className="p-6 bg-[var(--surface2)]/70 border-[var(--border)] shadow-2xl">
                <h2 className="text-xl font-bold text-white mb-4">Export Access</h2>
                <div className="space-y-3">
                  {(exportBundle?.exports || []).map((entry) => (
                    <a
                      key={entry.learner_id}
                      href={entry.export_url}
                      className="block rounded-xl border border-white/10 bg-black/10 p-4 text-blue-100 hover:bg-black/20 transition-colors"
                    >
                      <div className="font-bold text-white">{entry.display_name}</div>
                      <div className="text-xs text-blue-200 break-all">{entry.export_url}</div>
                    </a>
                  ))}
                </div>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {dashboard.learners.map((learner: ParentTrustDashboardLearner) => (
                <Card key={learner.learner_id} className="p-6 bg-[var(--surface2)]/70 border-[var(--border)] shadow-2xl">
                  <div className="flex justify-between items-start gap-4 mb-5">
                    <div>
                      <h3 className="text-2xl font-bold text-white">{learner.display_name}</h3>
                      <p className="text-blue-200 text-sm">
                        Grade {learner.grade_level} · {learner.archetype || "General"} archetype
                      </p>
                    </div>
                    <div className="rounded-full bg-blue-500/20 px-3 py-1 text-sm font-bold text-blue-100">
                      {learner.lesson_completion_rate_7d}% complete
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-5">
                    <div className="rounded-2xl bg-black/10 p-4">
                      <div className="text-xs uppercase tracking-widest text-blue-200 mb-1">IRT Theta</div>
                      <div className="text-2xl font-black text-white">{learner.irt_theta.toFixed(2)}</div>
                    </div>
                    <div className="rounded-2xl bg-black/10 p-4">
                      <div className="text-xs uppercase tracking-widest text-blue-200 mb-1">Streak</div>
                      <div className="text-2xl font-black text-white">{learner.streak_days} days</div>
                    </div>
                  </div>

                  <div className="mb-5">
                    <div className="text-xs uppercase tracking-widest text-blue-200 mb-2">Top Knowledge Gaps</div>
                    <div className="flex flex-wrap gap-2">
                      {learner.top_knowledge_gaps.length > 0 ? (
                        learner.top_knowledge_gaps.map((gap) => (
                          <span key={gap} className="rounded-full bg-white/10 px-3 py-1 text-sm text-white">
                            {gap}
                          </span>
                        ))
                      ) : (
                        <span className="rounded-full bg-green-500/20 px-3 py-1 text-sm text-green-100">
                          No unresolved gaps
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="rounded-2xl bg-white/10 p-4 mb-4">
                    <div className="text-xs uppercase tracking-widest text-blue-200 mb-2">AI Progress Summary</div>
                    <p className="text-blue-50 leading-relaxed">{learner.ai_progress_summary}</p>
                  </div>

                  <div className="rounded-2xl bg-black/10 p-4" aria-label={`Privacy controls for ${learner.display_name}`}>
                    <div className="text-xs uppercase tracking-widest text-blue-200 mb-3">Privacy controls</div>
                    <div className="flex flex-wrap gap-3">
                      <button type="button" onClick={() => void runDataRightsAction(learner.learner_id, "export")} className="rounded-xl bg-blue-600 px-4 py-2 font-bold text-white hover:bg-blue-500 transition-colors">Request export</button>
                      <button type="button" onClick={() => void runDataRightsAction(learner.learner_id, "restrict")} className="rounded-xl bg-yellow-500/20 px-4 py-2 font-bold text-yellow-100 hover:bg-yellow-500/30 transition-colors">Restrict processing</button>
                      <button type="button" onClick={() => void runDataRightsAction(learner.learner_id, "erase")} className="rounded-xl bg-red-500/20 px-4 py-2 font-bold text-red-100 hover:bg-red-500/30 transition-colors">Request erasure</button>
                    </div>
                    {privacyStatus[learner.learner_id] && (
                      <p className="mt-3 text-sm text-blue-100" role="status" aria-live="polite">{privacyStatus[learner.learner_id]}</p>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
