"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { SUBJECTS } from "@/components/eduboost/constants";
import { useLearner } from "@/context/LearnerContext";
import { LearnerService } from "@/lib/api/services";
import { extractErrorMessage } from "@/lib/api/client";
import type { ActiveLearner, GamificationProfile } from "@/lib/api/types";
import { DashboardSkeleton } from "./DashboardSkeleton";

interface DashboardClientProps {
  initialLearner: ActiveLearner | null;
  initialGamification: GamificationProfile | null;
  fetchedAt?: string;
  source?: "api" | "fixture";
}

export function DashboardClient({
  initialLearner,
  initialGamification,
}: DashboardClientProps) {
  const { learner, setLearner } = useLearner();
  const [gamification, setGamification] = useState<GamificationProfile | null>(initialGamification);
  const [loading, setLoading] = useState(!initialGamification);
  const [error, setError] = useState("");
  const [offline, setOffline] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (!learner && initialLearner) {
      setLearner(initialLearner);
    }
  }, [learner, initialLearner, setLearner]);

  const fetchData = useCallback(async () => {
    if (!learner?.learner_id) {
      return;
    }

    setLoading(true);
    setError("");
    setOffline(typeof navigator !== "undefined" && !navigator.onLine);
    try {
      const gamificationRes = await LearnerService.getGamificationProfile(learner.id || learner.learner_id);
      setGamification(gamificationRes);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
      const msg = extractErrorMessage(err);
      setError(
        typeof navigator !== "undefined" && !navigator.onLine
          ? "You are offline. Reconnect to refresh your dashboard."
          : msg
      );
    } finally {
      setLoading(false);
    }
  }, [learner?.id, learner?.learner_id]);

  useEffect(() => {
    if (!initialGamification) {
      void fetchData();
    }
  }, [fetchData, initialGamification]);

  if (!learner) {
    return <DashboardSkeleton note="Checking learner profile..." />;
  }

  if (loading && !gamification) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
        <p className="mt-4 text-[var(--muted)] font-medium">Loading your dashboard...</p>
      </div>
    );
  }

  if (error && !gamification) {
    return (
      <div className="max-w-6xl mx-auto p-4 md:p-8">
        <header className="mb-10">
          <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">
            Welcome back, {learner.nickname || learner.display_name || "Learner"}!
          </h1>
          <p className="text-[var(--muted)] font-medium">
            {offline ? "Your latest progress needs a connection." : "We could not load your progress yet."}
          </p>
        </header>
        <ErrorMessage message={error} onRetry={() => void fetchData()} />
      </div>
    );
  }

  const totalXp = gamification?.total_xp ?? 0;
  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8">
      <header className="mb-10">
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">
          Welcome back,{" "}
          <button
            type="button"
            className="underline decoration-dotted underline-offset-4 hover:text-[var(--blue)]"
            onClick={() => router.push(`/learners/${learner.id || learner.learner_id}`)}
          >
            {learner.display_name || learner.nickname || "Learner"}
          </button>
          !
        </h1>
        <p className="text-[var(--muted)] font-medium">
          You&apos;re doing great! Here&apos;s a look at your progress today.
        </p>
      </header>

      {error && <ErrorMessage message={error} onRetry={() => void fetchData()} className="mb-8" />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2 p-8 bg-gradient-to-br from-[var(--surface)] to-[var(--surface2)] border-none shadow-xl relative overflow-hidden">
          <div className="relative z-10">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">Learning</h2>
            <div className="flex flex-col md:flex-row items-center gap-10">
              <div className="flex-1 space-y-6">
                <p className="text-lg text-[var(--text)] font-medium leading-relaxed">
                  Progress estimates and adaptive check-ins are temporarily unavailable while the question bank is rebuilt and independently reviewed.
                </p>
                <div className="flex flex-wrap gap-4">
                  <Button onClick={() => router.push("/lesson")} className="px-8 shadow-lg shadow-blue-500/20">
                    Start New Lesson
                  </Button>
                </div>
              </div>
            </div>
          </div>
          <div className="absolute -right-10 -bottom-10 text-9xl opacity-5 pointer-events-none">🦁</div>
        </Card>

        <div className="space-y-6">
          <Card className="p-6 border-none bg-[var(--surface)] shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-orange-100 text-orange-500 rounded-2xl flex items-center justify-center text-3xl shadow-inner">
                🔥
              </div>
              <div>
                <div className="text-sm text-[var(--muted)] font-bold uppercase tracking-wider">Daily Streak</div>
                <div className="text-2xl font-bold text-orange-500">{gamification?.streak_days || 0} Days</div>
              </div>
            </div>
          </Card>

          <Card className="p-6 border-none bg-[var(--surface)] shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-blue-100 text-blue-500 rounded-2xl flex items-center justify-center text-3xl shadow-inner">
                ✨
              </div>
              <div>
                <div className="text-sm text-[var(--muted)] font-bold uppercase tracking-wider">Total XP</div>
                <div className="text-2xl font-bold text-blue-500">{totalXp}</div>
              </div>
            </div>
            <div className="mt-4 h-2 bg-[var(--border)] rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-1000"
                style={{ width: `${Math.min(100, ((totalXp % 100) / 100) * 100)}%` }}
              />
            </div>
            <div className="mt-2 text-xs text-[var(--muted)] font-bold text-right">
              {100 - (totalXp % 100)} XP to Next Game Level
            </div>
          </Card>

          <Card className="p-6 border-none bg-[var(--surface)] shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-purple-100 text-purple-500 rounded-2xl flex items-center justify-center text-3xl shadow-inner">
                ⭐
              </div>
              <div>
                <div className="text-sm text-[var(--muted)] font-bold uppercase tracking-wider">Game Level</div>
                <div className="text-2xl font-bold text-purple-500">Level {gamification?.level || 1}</div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      <section className="mt-12">
        <h3 className="text-2xl font-bold mb-8 flex items-center gap-3">Your Subjects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {SUBJECTS.map((subject) => (
              <Card
                key={subject.code}
                className="p-6 border-none bg-[var(--surface)] shadow-md hover:-translate-y-1 hover:shadow-lg transition-all cursor-pointer group"
                onClick={() => router.push(`/lesson?subject=${subject.code}`)}
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform shadow-sm"
                  style={{ backgroundColor: `${subject.color}15`, color: subject.color }}
                >
                  {subject.icon}
                </div>
                <h4 className="font-bold text-lg mb-1">{subject.label}</h4>
              </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
