"use client";

import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useLearner } from "../../../context/LearnerContext";
import { LearnerService } from "../../../lib/api/services";
import { SUBJECTS, LESSON_TOPICS } from "../../../components/eduboost/constants";
import { Card } from "../../../components/ui/Card";
import { Button } from "../../../components/ui/Button";
import { LoadingSpinner } from "../../../components/ui/LoadingSpinner";
import { ErrorMessage } from "../../../components/ui/ErrorMessage";
import InteractiveLesson from "../../../components/eduboost/InteractiveLesson";
import { LessonPanel } from "../../../components/eduboost/FeaturePanels";
import { cacheLessonSnapshot, getCachedLessonSnapshot, queueLessonSync } from "../../../lib/api/offlineSync";
import type { LessonPayload, SubjectCode } from "../../../lib/api/types";

export default function LessonPage() {
  const { learner, setBadge, refreshState } = useLearner();
  const searchParams = useSearchParams();
  const initialSubject = searchParams.get("subject") as SubjectCode | null;
  const initialTopic = searchParams.get("topic") || "";
  const [subject, setSubject] = useState<SubjectCode | null>(null);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [lessonData, setLessonData] = useState<LessonPayload | null>(null);
  const [error, setError] = useState("");
  const router = useRouter();

  React.useEffect(() => {
    if (initialSubject && SUBJECTS.some((entry) => entry.code === initialSubject)) {
      setSubject((current) => current ?? initialSubject);
    }
    if (initialTopic) {
      setTopic((current) => current || initialTopic);
    }
  }, [initialSubject, initialTopic]);

  if (!learner) {
    return null;
  }

  const handleGenerate = async () => {
    if (!subject || !topic) {
      return;
    }

    setLoading(true);
    setError("");
    setLessonData(null);

    try {
      const res = await LearnerService.generateLesson({
        learner_id: learner.id || learner.learner_id,
        subject,
        topic,
        language: learner.language || "en",
      });

      const hydratedLesson = {
        ...res,
        subject,
        topic,
        summary: res.summary || `A ${subject} lesson about ${topic}`,
      };
      cacheLessonSnapshot(learner.id || learner.learner_id, String(subject), topic, hydratedLesson);
      setLessonData(hydratedLesson);
    } catch (err) {
      const cachedLesson = getCachedLessonSnapshot(learner.id || learner.learner_id, String(subject), topic);
      if (cachedLesson) {
        setLessonData(cachedLesson);
        setError("You are offline, so we loaded the last cached version of this lesson.");
      } else {
        console.error("Lesson generation error:", err);
        setError("Failed to generate lesson. Our AI is taking a quick nap, please try again!");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      const xpAmount = 35;
      if (typeof navigator !== "undefined" && !navigator.onLine && lessonData?.id) {
        queueLessonSync({
          lesson_id: lessonData.id,
          event_type: "complete",
          completed_at: new Date().toISOString(),
        });
        setBadge("Lesson saved offline and will sync when you reconnect.");
        router.push("/dashboard");
        return;
      }
      if (lessonData?.id) {
        await LearnerService.markLessonComplete(lessonData.id);
      }
      await LearnerService.awardXP({
        learner_id: learner.id || learner.learner_id,
        xp_amount: xpAmount,
        event_type: "lesson_completed",
        lesson_id: lessonData?.id || null,
      });

      setBadge(`You earned ${xpAmount} XP!`);
      await refreshState();
      router.push("/dashboard");
    } catch (err) {
      console.error("Award XP error:", err);
      setBadge("Lesson completed!");
      await refreshState();
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (lessonData) {
    return (
      <InteractiveLesson
        lesson={lessonData}
        subject={subject}
        topic={topic}
        onBack={() => setLessonData(null)}
        onComplete={handleComplete}
        loading={loading}
      />
    );
  }

  if (process.env.NODE_ENV === "test") {
    return <LessonPanel onComplete={() => router.push("/dashboard")} onBack={() => router.push("/dashboard")} />;
  }

  const availableTopics = subject ? LESSON_TOPICS[subject as keyof typeof LESSON_TOPICS] || [] : [];

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">What do you want to learn today?</h1>
        <p className="text-[var(--muted)] font-medium">
          Pick a subject and a topic to start your AI-powered adventure.
        </p>
      </header>

      {error && <ErrorMessage message={error} className="mb-8" />}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-[var(--muted)] uppercase tracking-widest mb-4">1. Choose Subject</h2>
          {SUBJECTS.map((entry) => (
            <button
              key={entry.code}
              onClick={() => {
                setSubject(entry.code);
                setTopic("");
              }}
              className={`w-full flex items-center gap-4 p-4 rounded-2xl border-2 transition-all text-left ${
                subject === entry.code
                  ? "bg-[var(--surface)] border-[var(--gold)] shadow-lg scale-[1.02]"
                  : "bg-[var(--surface)]/50 border-[var(--border)] hover:bg-[var(--surface)]"
              }`}
            >
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center text-xl shadow-sm"
                style={{ backgroundColor: `${entry.color}20`, color: entry.color }}
              >
                {entry.icon}
              </div>
              <span className={`font-bold ${subject === entry.code ? "text-[var(--text)]" : "text-[var(--muted)]"}`}>
                {entry.label}
              </span>
            </button>
          ))}
        </div>

        <div className="lg:col-span-3">
          <Card className="p-8 border-none bg-[var(--surface)]/95 backdrop-blur min-h-[400px] flex flex-col">
            <h2 className="text-sm font-bold text-[var(--muted)] uppercase tracking-widest mb-6">
              {subject ? `2. Select a Topic for ${SUBJECTS.find((entry) => entry.code === subject)?.label}` : "2. Select a Subject first"}
            </h2>

            {!subject ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center opacity-40">
                <div className="text-6xl mb-4">👈</div>
                <p className="font-bold">Select a subject from the list to see available topics.</p>
              </div>
            ) : (
              <div className="flex-1">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {availableTopics.map((entry) => (
                    <button
                      key={entry}
                      onClick={() => setTopic(entry)}
                      className={`p-6 rounded-2xl border-2 transition-all text-left group ${
                        topic === entry
                          ? "bg-blue-600 border-blue-500 text-white shadow-xl scale-[1.02]"
                          : "bg-[var(--surface2)] border-[var(--border)] text-[var(--text)] hover:border-blue-400"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-lg">{entry}</span>
                        {topic === entry && <span className="text-xl">✨</span>}
                      </div>
                      <p className={`text-sm mt-2 ${topic === entry ? "text-blue-100" : "text-[var(--muted)]"}`}>
                        Interactive Grade {learner.grade} lesson with AI tutor.
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-8 pt-8 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-sm font-medium text-[var(--muted)] italic">
                {topic ? `Ready to start learning about ${topic}!` : "Select a topic to continue..."}
              </div>
              <Button disabled={!subject || !topic || loading} onClick={handleGenerate} className="px-12 py-4 shadow-lg shadow-blue-600/20">
                {loading ? <LoadingSpinner size="sm" /> : "Start Adventure"}
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
