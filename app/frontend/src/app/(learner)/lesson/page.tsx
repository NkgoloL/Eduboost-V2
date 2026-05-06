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
  const [completionError, setCompletionError] = useState("");
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
    setCompletionError("");
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
        setError(
          typeof navigator !== "undefined" && !navigator.onLine
            ? "You are offline. Reconnect to generate this lesson."
            : "Failed to generate lesson. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    setCompletionError("");
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
      setCompletionError("The lesson is complete, but we could not sync your XP yet. Please try again.");
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
        error={completionError}
      />
    );
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
              className={`w-full flex items-center gap-4 p-5 rounded-2xl border-2 transition-all text-left group hover:shadow-md ${
                subject === entry.code
                  ? "bg-white dark:bg-[var(--surface)] border-[var(--gold)] shadow-lg scale-[1.03] z-10"
                  : "bg-[var(--surface)]/40 border-[var(--border)] hover:border-[var(--muted)]/50"
              }`}
            >
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shadow-sm transition-transform group-hover:scale-110"
                style={{ backgroundColor: `${entry.color}20`, color: entry.color }}
              >
                {entry.icon}
              </div>
              <div className="flex-1">
                <span className={`block font-black text-lg ${subject === entry.code ? "text-[var(--text)]" : "text-[var(--muted)]"}`}>
                  {entry.label}
                </span>
                {subject === entry.code && (
                  <span className="text-[10px] font-bold text-[var(--gold)] uppercase tracking-tighter">Active Choice</span>
                )}
              </div>
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
                      className={`p-6 rounded-3xl border-2 transition-all text-left group relative overflow-hidden ${
                        topic === entry
                          ? "bg-blue-600 border-blue-500 text-white shadow-2xl scale-[1.02]"
                          : "bg-[var(--surface)] border-[var(--border)] text-[var(--text)] hover:border-blue-400 hover:shadow-md"
                      }`}
                    >
                      <div className="relative z-10">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-black text-xl leading-tight">{entry}</span>
                          {topic === entry && <span className="text-2xl animate-pulse">✨</span>}
                        </div>
                        <p className={`text-sm font-medium ${topic === entry ? "text-blue-100" : "text-[var(--muted)]"}`}>
                          Personalized Grade {learner.grade} lesson with your AI tutor.
                        </p>
                      </div>
                      {topic === entry && (
                        <div className="absolute top-0 right-0 p-2 opacity-10 text-6xl pointer-events-none">
                          🚀
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-8 pt-8 border-t border-[var(--border)] flex flex-col sm:flex-row items-center justify-between gap-4">
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
