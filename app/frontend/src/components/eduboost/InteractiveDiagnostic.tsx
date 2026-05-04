"use client";

import React, { useMemo, useState } from "react";
import { DiagnosticService } from "../../lib/api/services";
import { Card } from "../ui/Card";
import { Stars } from "./EntryScreens";
import type { ActiveLearner, DiagnosticAnswerInput, DiagnosticItem, DiagnosticResult, RankedGap, SubjectCode } from "../../lib/api/types";

interface InteractiveDiagnosticProps {
  learner: ActiveLearner;
  onComplete: (subject: SubjectCode, mastery: number) => void;
  onBack: () => void;
}

export function InteractiveDiagnostic({ learner, onComplete, onBack }: InteractiveDiagnosticProps) {
  const [subject, setSubject] = useState<SubjectCode | null>(null);
  const [items, setItems] = useState<DiagnosticItem[]>([]);
  const [answers, setAnswers] = useState<DiagnosticAnswerInput[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [completed, setCompleted] = useState(false);
  const [gapReport, setGapReport] = useState<DiagnosticResult | null>(null);
  const [questionCount, setQuestionCount] = useState(0);
  const maxQuestions = 10;

  const subjects = [
    { code: "MATH", label: "Mathematics", emoji: "🔢", color: "#FFD700" },
    { code: "ENG", label: "English", emoji: "📚", color: "#4CAF50" },
    { code: "NS", label: "Natural Science", emoji: "🔬", color: "#2196F3" },
    { code: "SS", label: "Social Science", emoji: "🌍", color: "#FF5722" },
    { code: "LIFE", label: "Life Orientation", emoji: "🤝", color: "#9C27B0" },
  ] as const;

  const currentItem = items[questionCount] || null;

  const masteryScore = useMemo(() => {
    if (!gapReport?.theta_after) {
      return 70;
    }
    return Math.max(0, Math.min(100, Math.round(((gapReport.theta_after + 3) / 6) * 100)));
  }, [gapReport?.theta_after]);

  const handleStart = async (subjectCode: SubjectCode) => {
    setLoading(true);
    setError("");
    setSubject(subjectCode);
    setAnswers([]);
    setGapReport(null);
    setCompleted(false);
    setQuestionCount(0);
    try {
      const fetchedItems = await DiagnosticService.getItems(learner.id || learner.learner_id);
      const filtered = fetchedItems.filter((item) => !item.subject || item.subject === subjectCode);
      setItems(filtered.slice(0, maxQuestions));
      if (filtered.length === 0) {
        setError("No diagnostic items are available for that subject yet.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start diagnostic.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (option: string) => {
    if (!currentItem?.item_id || !subject) {
      return;
    }

    const nextAnswers = [...answers, { item_id: currentItem.item_id, selected_option: option }];
    setAnswers(nextAnswers);

    if (questionCount < items.length - 1) {
      setQuestionCount((count) => count + 1);
      return;
    }

    setLoading(true);
    setError("");
    try {
      const result = await DiagnosticService.submit(learner.id || learner.learner_id, nextAnswers);
      setGapReport(result);
      setCompleted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit diagnostic.");
    } finally {
      setLoading(false);
    }
  };

  if (completed && gapReport) {
    const rankedGaps = gapReport.ranked_gaps || [];
    return (
      <div className="screen flex items-center justify-center p-4">
        <Stars />
        <Card className="relative z-10 p-8 max-w-2xl w-full bg-white/90 backdrop-blur-xl shadow-2xl border-none rounded-3xl">
          <div className="text-center mb-10">
            <div className="text-7xl mb-6 animate-bounce">🏆</div>
            <h2 className="text-4xl font-['Baloo_2'] text-gray-800 font-bold">Assessment Complete!</h2>
            <p className="text-gray-500 text-lg mt-2">
              Amazing work, {learner.nickname || learner.display_name || "Learner"}!
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-3xl mb-10 border border-blue-100 shadow-inner">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-bold text-blue-900 text-xl">Subject Mastery</h3>
              <div className="text-3xl font-black text-blue-600">{masteryScore}%</div>
            </div>

            <div className="h-4 bg-blue-100 rounded-full overflow-hidden mb-8">
              <div className="h-full bg-blue-500 rounded-full transition-all duration-1000" style={{ width: `${masteryScore}%` }} />
            </div>

            <div>
              <p className="text-sm font-bold text-blue-800 mb-3 uppercase tracking-wider">Gap Analysis:</p>
              <div className="flex flex-wrap gap-2">
                {rankedGaps.length > 0 ? (
                  rankedGaps.map((gap: RankedGap, index: number) => (
                    <span key={`${gap.subject}-${gap.topic}-${index}`} className="bg-white/80 px-4 py-2 rounded-2xl text-sm font-semibold border border-blue-200 text-blue-700 shadow-sm">
                      {gap.subject}: {gap.topic}
                    </span>
                  ))
                ) : (
                  <div className="bg-green-100 text-green-700 px-6 py-3 rounded-2xl font-bold">You have mastered all current concepts!</div>
                )}
              </div>
            </div>
          </div>

          <button
            className="btn-primary w-full py-5 text-xl rounded-2xl"
            onClick={() => onComplete(subject || "MATH", masteryScore)}
          >
            Update My Study Plan
          </button>
        </Card>
      </div>
    );
  }

  if (currentItem) {
    const progress = ((questionCount + 1) / Math.max(items.length, 1)) * 100;
    return (
      <div className="screen flex items-center justify-center p-4">
        <Stars />
        <Card className="relative z-10 w-full max-w-2xl p-10 bg-white/95 backdrop-blur shadow-2xl border-none rounded-3xl">
          <div className="mb-8">
            <div className="flex justify-between items-center mb-3">
              <span className="bg-blue-100 text-blue-600 px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest">
                {subject} • Grade {learner.grade}
              </span>
              <span className="text-gray-400 text-xs font-bold font-mono">
                Question {questionCount + 1} / {items.length}
              </span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: `${progress}%` }} />
            </div>
          </div>

          <div className="min-h-[120px] flex items-center mb-10">
            <h3 className="text-2xl md:text-3xl font-bold text-gray-800 leading-tight">
              {currentItem.question_text || currentItem.question}
            </h3>
          </div>

          <div className="grid grid-cols-1 gap-4 mb-10">
            {currentItem.options.map((option, index) => (
              <button
                key={`${currentItem.item_id}-${index}`}
                disabled={loading}
                onClick={() => void handleAnswer(option)}
                className="group relative text-left p-6 border-2 border-gray-50 rounded-2xl hover:border-blue-400 hover:bg-blue-50 transition-all transform hover:-translate-y-1 active:scale-95 shadow-sm"
              >
                <div className="flex items-center gap-4">
                  <span className="w-10 h-10 flex items-center justify-center rounded-xl bg-gray-50 group-hover:bg-blue-100 text-gray-400 group-hover:text-blue-600 font-bold transition-colors">
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span className="font-bold text-gray-700 text-lg">{option}</span>
                </div>
              </button>
            ))}
          </div>

          {error && <div className="bg-red-50 text-red-500 p-4 rounded-xl mb-6 text-sm font-medium border border-red-100">{error}</div>}

          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2 text-gray-400 text-xs font-bold uppercase tracking-wider">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              Adaptive Engine
            </div>
            {loading && <div className="text-blue-500 font-bold text-sm">Calculating...</div>}
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="screen flex items-center justify-center p-4">
      <Stars />
      <Card className="relative z-10 w-full max-w-lg p-10 bg-white/95 backdrop-blur shadow-2xl border-none rounded-3xl">
        <button onClick={onBack} className="text-gray-400 hover:text-gray-600 mb-8 flex items-center gap-2 font-bold transition-colors">
          Back to Dashboard
        </button>

        <h2 className="text-4xl font-['Baloo_2'] text-gray-800 mb-2 font-bold">Diagnostic</h2>
        <p className="text-gray-500 mb-10 text-lg">Pick a subject to start your adaptive check-in.</p>

        <div className="grid grid-cols-1 gap-4">
          {subjects.map((entry) => (
            <button
              key={entry.code}
              onClick={() => void handleStart(entry.code)}
              disabled={loading}
              className="group flex items-center gap-5 p-6 border-2 border-gray-50 rounded-3xl hover:border-blue-400 hover:bg-blue-50 transition-all text-left shadow-sm hover:shadow-md active:scale-95"
            >
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-4xl shadow-inner transition-transform group-hover:scale-110" style={{ backgroundColor: `${entry.color}15` }}>
                {entry.emoji}
              </div>
              <div>
                <span className="block font-black text-gray-800 text-xl">{entry.label}</span>
                <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Adaptive Assessment</span>
              </div>
              {loading && subject === entry.code ? <div className="ml-auto text-blue-500 font-bold">Loading...</div> : <div className="ml-auto text-gray-200 group-hover:text-blue-400 transition-colors">→</div>}
            </button>
          ))}
        </div>

        {error && <div className="mt-6 bg-red-50 text-red-500 p-4 rounded-xl text-sm font-medium border border-red-100">{error}</div>}
      </Card>
    </div>
  );
}
