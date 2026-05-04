"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLearner } from "../../../context/LearnerContext";
import { LearnerService } from "../../../lib/api/services";
import { Card } from "../../../components/ui/Card";
import { LoadingSpinner } from "../../../components/ui/LoadingSpinner";
import { ErrorMessage } from "../../../components/ui/ErrorMessage";
import type { StudyPlanItem, StudyPlanResponse } from "../../../lib/api/types";

const subjectFromPlanItem = (item: StudyPlanItem) => {
  const key = `${item.code || ""} ${item.label || ""}`.toUpperCase();
  if (key.includes("MATH")) return "MATH";
  if (key.includes("ENG") || key.includes("READING")) return "ENG";
  if (key.includes("LIFE")) return "LIFE";
  if (key.includes("NS") || key.includes("SCIENCE")) return "NS";
  if (key.includes("SS") || key.includes("SOCIAL")) return "SS";
  return "";
};

const lessonHrefForPlanItem = (item: StudyPlanItem) => {
  const params = new URLSearchParams();
  const subject = subjectFromPlanItem(item);
  if (subject) params.set("subject", subject);
  if (item.label) params.set("topic", item.label);
  const query = params.toString();
  return query ? `/lesson?${query}` : "/lesson";
};

export default function StudyPlanPage() {
  const { learner } = useLearner();
  const [plan, setPlan] = useState<StudyPlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [offline, setOffline] = useState(false);
  const router = useRouter();

  const fetchPlan = useCallback(async () => {
    if (!learner?.learner_id) {
      return;
    }

    setLoading(true);
    setError("");
    setOffline(typeof navigator !== "undefined" && !navigator.onLine);
    try {
      const res = await LearnerService.getStudyPlan(learner.id || learner.learner_id);
      setPlan(res);
    } catch (err) {
      console.error("Study plan fetch error:", err);
      setError(
        typeof navigator !== "undefined" && !navigator.onLine
          ? "You are offline. Reconnect to build your study plan."
          : "Failed to load your study plan. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, [learner?.id, learner?.learner_id]);

  useEffect(() => {
    void fetchPlan();
  }, [fetchPlan]);

  if (!learner) {
    return null;
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
        <p className="mt-4 text-[var(--muted)] font-medium">Preparing your custom plan...</p>
      </div>
    );
  }

  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const schedule = plan?.days || plan?.schedule || {};
  const currentDay = new Intl.DateTimeFormat("en-US", { weekday: "short" }).format(new Date());
  const hasScheduledItems = days.some((day) => (schedule?.[day] || []).length > 0);

  if (error && !plan) {
    return (
      <div className="max-w-6xl mx-auto p-4 md:p-8">
        <header className="mb-12">
          <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">Your Study Plan</h1>
          <p className="text-[var(--muted)] font-medium">
            {offline ? "Your plan needs a connection to refresh." : "We could not prepare your plan yet."}
          </p>
        </header>
        <ErrorMessage message={error} onRetry={() => void fetchPlan()} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">Your Study Plan</h1>
        <p className="text-[var(--muted)] font-medium">
          A personalized schedule built just for you based on your goals and progress.
        </p>
      </header>

      {error && <ErrorMessage message={error} onRetry={() => void fetchPlan()} className="mb-8" />}

      <Card className="p-8 border-none bg-[var(--surface)] text-[var(--text)] mb-12 shadow-xl ring-1 ring-[var(--border)]">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div>
            <h2 className="text-2xl font-bold mb-2">Weekly Focus</h2>
            <p className="text-[var(--muted)] text-lg">{plan?.week_focus || "General Grade Review & Mastery Boost"}</p>
          </div>
          <div className="bg-[var(--surface2)] px-6 py-3 rounded-2xl border border-[var(--border)] text-center">
            <div className="text-xs font-bold uppercase tracking-widest opacity-80 mb-1">Target Grade</div>
            <div className="text-2xl font-black">Grade {learner.grade}</div>
          </div>
        </div>
      </Card>

      {!hasScheduledItems && (
        <Card className="mb-8 p-8 border-dashed bg-[var(--surface)] text-center">
          <h3 className="text-xl font-bold mb-2">No study blocks yet</h3>
          <p className="text-[var(--muted)] mb-6">Take an assessment or generate a lesson so your plan can adapt.</p>
          <button onClick={() => router.push("/diagnostic")} className="btn-primary">
            Take Assessment
          </button>
        </Card>
      )}

      <div className="space-y-6">
        {days.map((day) => {
          const items = schedule?.[day] || [];
          const isToday = day === currentDay;

          return (
            <div key={day} className={`flex flex-col md:flex-row gap-4 md:gap-8 ${isToday ? "relative" : ""}`}>
              <div className="md:w-32 flex flex-row md:flex-col items-center justify-center gap-2 md:gap-1 md:pt-4">
                <span className={`text-xl font-black uppercase tracking-normal ${isToday ? "text-[var(--blue)]" : "text-[var(--muted)]"}`}>{day}</span>
                {isToday && (
                  <span className="ml-2 md:ml-0 md:mt-1 bg-[var(--surface2)] text-[var(--blue)] text-[10px] px-2 py-0.5 rounded-full font-bold">
                    TODAY
                  </span>
                )}
              </div>

              <div className="flex-1 space-y-4">
                {items.length === 0 ? (
                  <div className="p-6 rounded-2xl border-2 border-dashed border-[var(--border)] text-[var(--muted)] italic text-sm">
                    Rest day! Take some time to play and recharge.
                  </div>
                ) : (
                  items.map((item: StudyPlanItem, idx: number) => (
                    <Card
                      key={`${day}-${idx}`}
                      className={`p-6 border-none flex flex-col sm:flex-row items-center gap-6 transition-all shadow-md hover:shadow-lg ${
                        isToday ? "bg-[var(--surface)] ring-2 ring-blue-500/30" : "bg-[var(--surface)]"
                      }`}
                    >
                      <div className="w-16 h-16 bg-[var(--surface2)] rounded-2xl flex items-center justify-center text-3xl shadow-inner">
                        {item.emoji || "📚"}
                      </div>
                      <div className="flex-1 text-center sm:text-left">
                        <div className="flex flex-wrap justify-center sm:justify-start items-center gap-2 mb-1">
                          <h4 className="font-bold text-lg text-[var(--text)]">{item.label}</h4>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-widest ${
                              item.type === "gap-fill"
                                ? "bg-orange-100 text-orange-600"
                                : item.type === "completed"
                                  ? "bg-green-100 text-green-600"
                                  : "bg-blue-100 text-blue-600"
                            }`}
                          >
                            {item.type?.replace("-", " ") || "curriculum"}
                          </span>
                        </div>
                        <p className="text-sm text-[var(--muted)] font-medium">
                          {item.type === "gap-fill"
                            ? "Focusing on a concept from a previous level."
                            : "Standard curriculum goal for your grade."}
                        </p>
                      </div>
                      <button
                        onClick={() => router.push(lessonHrefForPlanItem(item))}
                        className={`px-6 py-2 rounded-xl font-bold transition-all ${
                          item.type === "completed"
                            ? "bg-green-500/10 text-green-300 cursor-default"
                            : "bg-[var(--surface2)] text-[var(--text)] hover:bg-blue-600 hover:text-white"
                        }`}
                        disabled={item.type === "completed"}
                      >
                        {item.type === "completed" ? "Done" : "Start"}
                      </button>
                    </Card>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
