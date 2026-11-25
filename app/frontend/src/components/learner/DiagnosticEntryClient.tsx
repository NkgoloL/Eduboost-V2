"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { DiagnosticSkeleton } from "@/components/learner/DiagnosticSkeleton";
import { useLearner } from "@/context/LearnerContext";
import type { ActiveLearner, SubjectCode } from "@/lib/api/types";

interface DiagnosticEntryClientProps {
  initialLearner: ActiveLearner | null;
  availableSubjects?: SubjectCode[];
}

export function DiagnosticEntryClient({ initialLearner }: DiagnosticEntryClientProps) {
  const { learner, setLearner } = useLearner();
  const router = useRouter();

  useEffect(() => {
    if (!learner && initialLearner) {
      setLearner(initialLearner);
    }
  }, [learner, initialLearner, setLearner]);

  if (!learner) {
    return <DiagnosticSkeleton />;
  }

  return (
    <main className="mx-auto max-w-3xl p-8" aria-live="polite">
      <h1 className="text-3xl font-bold">Check-ins are temporarily unavailable</h1>
      <p className="mt-4 text-lg">The Grade 4 question bank is being rebuilt and reviewed by educators. You can continue with lessons; no mastery or placement score will be shown.</p>
      <button type="button" className="mt-6 rounded bg-blue-700 px-5 py-3 text-white" onClick={() => router.push("/dashboard")}>Return to dashboard</button>
    </main>
  );
}
