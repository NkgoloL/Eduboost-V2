"use client";

import React, { useEffect, useState } from "react";
import { useLearner } from "../../../context/LearnerContext";
import { LearnerService } from "../../../lib/api/services";
import { Card } from "../../../components/ui/Card";
import { Badge } from "../../../components/ui/Badge";
import { LoadingSpinner } from "../../../components/ui/LoadingSpinner";
import { ErrorMessage } from "../../../components/ui/ErrorMessage";

export default function BadgesPage() {
  const { learner } = useLearner();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!learner?.learner_id) return;

    const fetchProfile = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await LearnerService.getGamificationProfile(learner.learner_id);
        setProfile(res);
      } catch (err) {
        console.error("Gamification profile fetch error:", err);
        setError("Failed to load your achievements. Keep learning to earn more!");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [learner?.learner_id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
        <p className="mt-4 text-[var(--muted)] font-medium">Polishing your trophies...</p>
      </div>
    );
  }

  const badges = profile?.earned_badges || [];
  const nextLevelXp = (profile?.level || 1) * 100;
  const progress = ((profile?.total_xp % 100) / 100) * 100;

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">
          🏆 Your Achievements
        </h1>
        <p className="text-[var(--muted)] font-medium">
          Celebrate your hard work and see all the badges you've earned on your journey.
        </p>
      </header>

      {error && <ErrorMessage message={error} className="mb-8" />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
        <Card className="lg:col-span-2 p-8 bg-gradient-to-br from-yellow-400 to-orange-500 text-white border-none shadow-xl relative overflow-hidden">
          <div className="relative z-10">
            <div className="flex items-center gap-6 mb-8">
              <div className="w-24 h-24 bg-white/20 backdrop-blur-md rounded-3xl flex items-center justify-center text-5xl border border-white/30 shadow-xl">
                {learner.avatar || "🦁"}
              </div>
              <div>
                <h2 className="text-3xl font-black mb-1">{learner.nickname}</h2>
                <div className="flex items-center gap-2">
                  <span className="bg-white/30 px-3 py-1 rounded-full text-xs font-bold tracking-widest uppercase">
                    Level {profile?.level || 1}
                  </span>
                  <span className="bg-orange-600/30 px-3 py-1 rounded-full text-xs font-bold tracking-widest uppercase">
                    {profile?.streak_days || 0} Day Streak 🔥
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <span className="font-bold text-lg">Level Progress</span>
                <span className="font-black text-2xl">{profile?.total_xp || 0} XP</span>
              </div>
              <div className="h-4 bg-black/10 rounded-full overflow-hidden border border-white/20">
                <div 
                  className="h-full bg-white rounded-full transition-all duration-1000 shadow-[0_0_15px_rgba(255,255,255,0.5)]"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm font-medium text-orange-100 text-right">
                {100 - (profile?.total_xp % 100)} XP until Level {(profile?.level || 1) + 1}
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
        <h3 className="text-2xl font-bold mb-8 flex items-center gap-3">
          ✨ Earned Badges
        </h3>
        
        {badges.length === 0 ? (
          <div className="text-center py-20 bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200">
            <div className="text-6xl mb-4">🥚</div>
            <h4 className="text-xl font-bold text-gray-800 mb-2">No badges yet!</h4>
            <p className="text-gray-500 max-w-xs mx-auto">
              Complete lessons and diagnostics to start your collection. Your first badge is waiting!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
            {badges.map((badge, idx) => (
              <Card 
                key={idx} 
                className="p-6 border-none bg-white shadow-md hover:shadow-xl hover:-translate-y-1 transition-all text-center flex flex-col items-center animate-in zoom-in duration-300"
              >
                <div className="w-20 h-20 bg-yellow-50 rounded-full flex items-center justify-center text-4xl mb-4 shadow-inner border border-yellow-100">
                  {badge.icon || "🏆"}
                </div>
                <h4 className="font-bold text-gray-800 leading-tight mb-2">{badge.name}</h4>
                <Badge variant="secondary" className="text-[10px] uppercase tracking-tighter">
                  {badge.date_earned ? new Date(badge.date_earned).toLocaleDateString() : "Earned!"}
                </Badge>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
