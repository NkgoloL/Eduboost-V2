"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useLearner } from "../../../context/LearnerContext";
import { LearnerService } from "../../../lib/api/services";
import { Card } from "../../../components/ui/Card";
import { Badge } from "../../../components/ui/Badge";
import { LoadingSpinner } from "../../../components/ui/LoadingSpinner";
import { ErrorMessage } from "../../../components/ui/ErrorMessage";
import type { GamificationBadge, GamificationProfile } from "../../../lib/api/types";

export default function BadgesPage() {
  const { learner } = useLearner();
  const [profile, setProfile] = useState<GamificationProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [offline, setOffline] = useState(false);

  const fetchProfile = useCallback(async () => {
    if (!learner?.learner_id) {
      return;
    }

    setLoading(true);
    setError("");
    setOffline(typeof navigator !== "undefined" && !navigator.onLine);
    try {
      const res = await LearnerService.getGamificationProfile(learner.id || learner.learner_id);
      setProfile(res);
    } catch (err) {
      console.error("Gamification profile fetch error:", err);
      setError(
        typeof navigator !== "undefined" && !navigator.onLine
          ? "You are offline. Reconnect to refresh your achievements."
          : "Failed to load your achievements. Keep learning to earn more!"
      );
    } finally {
      setLoading(false);
    }
  }, [learner?.id, learner?.learner_id]);

  useEffect(() => {
    void fetchProfile();
  }, [fetchProfile]);

  if (!learner) {
    return null;
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
        <p className="mt-4 text-[var(--muted)] font-medium">Polishing your trophies...</p>
      </div>
    );
  }

  if (error && !profile) {
    return (
      <div className="max-w-6xl mx-auto p-4 md:p-8">
        <header className="mb-12">
          <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">Your Achievements</h1>
          <p className="text-[var(--muted)] font-medium">
            {offline ? "Your achievements need a connection to refresh." : "We could not load your badges yet."}
          </p>
        </header>
        <ErrorMessage message={error} onRetry={() => void fetchProfile()} />
      </div>
    );
  }

  const badges = profile?.earned_badges || [];
  const totalXp = profile?.total_xp ?? 0;
  const progress = ((totalXp % 100) / 100) * 100;

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">Your Achievements</h1>
        <p className="text-[var(--muted)] font-medium">
          Celebrate your hard work and see all the badges you&apos;ve earned on your journey.
        </p>
      </header>

      {error && <ErrorMessage message={error} onRetry={() => void fetchProfile()} className="mb-8" />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
        <Card className="lg:col-span-2 p-8 bg-[var(--surface)] text-[var(--text)] border-none shadow-xl relative overflow-hidden ring-1 ring-[var(--border)]">
          <div className="relative z-10">
            <div className="flex items-center gap-6 mb-8">
              <div className="w-24 h-24 bg-[var(--surface2)] backdrop-blur-md rounded-3xl flex items-center justify-center text-5xl border border-[var(--border)] shadow-xl">
                {typeof learner.avatar === "number" ? learner.avatar : "🦁"}
              </div>
              <div>
                <h2 className="text-3xl font-black mb-1">{learner.nickname || learner.display_name || "Learner"}</h2>
                <div className="flex items-center gap-2">
                  <span className="bg-[var(--surface2)] px-3 py-1 rounded-full text-xs font-bold tracking-widest uppercase">
                    Level {profile?.level || 1}
                  </span>
                  <span className="bg-[var(--surface2)] px-3 py-1 rounded-full text-xs font-bold tracking-widest uppercase">
                    {profile?.streak_days || 0} Day Streak
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <span className="font-bold text-lg">Level Progress</span>
                <span className="font-black text-2xl">{totalXp} XP</span>
              </div>
              <div className="h-4 bg-[var(--surface2)] rounded-full overflow-hidden border border-[var(--border)]">
                <div
                  className="h-full bg-[var(--gold)] rounded-full transition-all duration-1000"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm font-medium text-[var(--muted)] text-right">
                {100 - (totalXp % 100)} XP until Level {(profile?.level || 1) + 1}
              </p>
            </div>
          </div>
          <div className="absolute -right-20 -bottom-20 text-[20rem] opacity-10 rotate-12 pointer-events-none">✨</div>
        </Card>

        <Card className="p-8 border-none bg-[var(--surface)] shadow-lg flex flex-col items-center justify-center text-center">
          <div className="text-6xl mb-4">🎖️</div>
          <h3 className="text-2xl font-bold mb-2">Badge Count</h3>
          <div className="text-5xl font-black text-orange-500 mb-2">{badges.length}</div>
          <p className="text-[var(--muted)] font-medium">Badges earned so far</p>
        </Card>
      </div>

      <section>
        <h3 className="text-2xl font-bold mb-8 flex items-center gap-3">Earned Badges</h3>
        {badges.length === 0 ? (
          <div className="text-center py-20 bg-[var(--surface)] rounded-3xl border-2 border-dashed border-[var(--border)]">
            <div className="text-6xl mb-4">🏁</div>
            <h4 className="text-xl font-bold text-[var(--text)] mb-2">No badges yet!</h4>
            <p className="text-[var(--muted)] max-w-xs mx-auto">
              Complete lessons and diagnostics to start your collection. Your first badge is waiting!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
            {badges.map((badge: GamificationBadge, idx: number) => (
              <Card
                key={`${badge.badge_key || badge.name}-${idx}`}
                className="p-6 border-none bg-[var(--surface)] shadow-md hover:shadow-xl hover:-translate-y-1 transition-all text-center flex flex-col items-center animate-in zoom-in duration-300"
              >
                <div className="w-20 h-20 bg-[var(--surface2)] rounded-full flex items-center justify-center text-4xl mb-4 shadow-inner border border-[var(--border)]">
                  {badge.icon || "🏆"}
                </div>
                <h4 className="font-bold text-[var(--text)] leading-tight mb-2">{badge.name}</h4>
                <Badge variant="secondary" className="text-[10px] uppercase tracking-tighter">
                  {badge.date_earned || badge.earned_at
                    ? new Date(badge.date_earned || badge.earned_at || "").toLocaleDateString()
                    : "Earned!"}
                </Badge>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
