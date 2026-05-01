"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLearner } from "../../../context/LearnerContext";
import { LearnerService } from "../../../lib/api/services";
import { SUBJECTS } from "../../../components/eduboost/constants";
import { Card } from "../../../components/ui/Card";
import { Button } from "../../../components/ui/Button";
import { LoadingSpinner } from "../../../components/ui/LoadingSpinner";
import { ErrorMessage } from "../../../components/ui/ErrorMessage";

export default function DashboardPage() {
  const { learner, masteryData, setMasteryData } = useLearner();
  const [gamification, setGamification] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    if (!learner?.learner_id) return;

    const fetchData = async () => {
      setLoading(true);
      setError("");
      try {
        const [masteryRes, gamificationRes] = await Promise.all([
          LearnerService.getMastery(learner.learner_id),
          LearnerService.getGamificationProfile(learner.learner_id),
        ]);

        // Update mastery data in context
        if (masteryRes && masteryRes.mastery) {
          const newMastery = { ...masteryData };
          masteryRes.mastery.forEach((m) => {
            newMastery[m.subject_code] = Math.round(m.mastery_score * 100);
          });
          setMasteryData(newMastery);
        }

        setGamification(gamificationRes);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        setError("Failed to load dashboard data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [learner?.learner_id]);

  if (loading && !gamification) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
        <p className="mt-4 text-[var(--muted)] font-medium">Loading your dashboard...</p>
      </div>
    );
  }

  const overallMastery = Math.round(
    Object.values(masteryData).reduce((a, v) => a + v, 0) / 
    (Object.values(masteryData).length || 1)
  );

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8">
      {/* Header Section */}
      <header className="mb-10">
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">
          🏠 Welcome back, {learner?.nickname || "Learner"}!
        </h1>
        <p className="text-[var(--muted)] font-medium">
          You're doing great! Here's a look at your progress today.
        </p>
      </header>

      {error && <ErrorMessage message={error} className="mb-8" />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Progress Overview Card */}
        <Card className="lg:col-span-2 p-8 bg-gradient-to-br from-[var(--surface)] to-[var(--surface2)] border-none shadow-xl relative overflow-hidden">
          <div className="relative z-10">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              📊 Learning Progress
            </h2>
            
            <div className="flex flex-col md:flex-row items-center gap-10">
              <div className="relative w-40 h-40 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="transparent"
                    stroke="var(--border)"
                    strokeWidth="12"
                  />
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="transparent"
                    stroke="var(--gold)"
                    strokeWidth="12"
                    strokeDasharray={2 * Math.PI * 70}
                    strokeDashoffset={2 * Math.PI * 70 * (1 - overallMastery / 100)}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold">{overallMastery}%</span>
                  <span className="text-xs text-[var(--muted)] font-bold uppercase tracking-wider">Overall</span>
                </div>
              </div>

              <div className="flex-1 space-y-6">
                <p className="text-lg text-[var(--text)] font-medium leading-relaxed">
                  You have mastered <strong>{overallMastery}%</strong> of your curriculum goals. 
                  {overallMastery > 50 ? " Keep up the amazing work! 🚀" : " Let's boost those scores today!"}
                </p>
                <div className="flex flex-wrap gap-4">
                  <Button onClick={() => router.push("/lesson")} className="px-8 shadow-lg shadow-blue-500/20">
                    📖 Start New Lesson
                  </Button>
                  <Button variant="secondary" onClick={() => router.push("/diagnostic")} className="px-8">
                    🧪 Take Assessment
                  </Button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Decorative Background Element */}
          <div className="absolute -right-10 -bottom-10 text-9xl opacity-5 pointer-events-none">🦁</div>
        </Card>

        {/* Stats Sidebar */}
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
                <div className="text-2xl font-bold text-blue-500">{gamification?.total_xp || 0}</div>
              </div>
            </div>
            <div className="mt-4 h-2 bg-[var(--border)] rounded-full overflow-hidden">
              <div 
                className="h-full bg-blue-500 rounded-full transition-all duration-1000"
                style={{ width: `${Math.min(100, ((gamification?.total_xp % 100) / 100) * 100)}%` }}
              />
            </div>
            <div className="mt-2 text-xs text-[var(--muted)] font-bold text-right">
              {100 - (gamification?.total_xp % 100)} XP to Next Level
            </div>
          </Card>

          <Card className="p-6 border-none bg-[var(--surface)] shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-purple-100 text-purple-500 rounded-2xl flex items-center justify-center text-3xl shadow-inner">
                ⭐
              </div>
              <div>
                <div className="text-sm text-[var(--muted)] font-bold uppercase tracking-wider">Current Level</div>
                <div className="text-2xl font-bold text-purple-500">Level {gamification?.level || 1}</div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Subjects Grid */}
      <section className="mt-12">
        <h3 className="text-2xl font-bold mb-8 flex items-center gap-3">
          📚 Your Subjects
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {SUBJECTS.map((subject) => {
            const mastery = masteryData[subject.code] || 0;
            return (
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
                <div className="flex items-end justify-between">
                  <div className="text-sm font-bold text-[var(--muted)] uppercase tracking-tight">Mastery</div>
                  <div className="text-xl font-black" style={{ color: subject.color }}>{mastery}%</div>
                </div>
                <div className="mt-3 h-1.5 bg-[var(--border)] rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all duration-1000"
                    style={{ width: `${mastery}%`, backgroundColor: subject.color }}
                  />
                </div>
              </Card>
            );
          })}
        </div>
      </section>
    </div>
  );
}
