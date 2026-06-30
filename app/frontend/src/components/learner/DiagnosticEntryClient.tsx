"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { InteractiveDiagnostic } from "@/components/eduboost/InteractiveDiagnostic";
import { DiagnosticSkeleton } from "@/components/learner/DiagnosticSkeleton";
import { useLearner } from "@/context/LearnerContext";
import type { ActiveLearner, SubjectCode } from "@/lib/api/types";

interface DiagnosticEntryClientProps {
  initialLearner: ActiveLearner | null;
  availableSubjects?: SubjectCode[];
}

export function DiagnosticEntryClient({ initialLearner }: DiagnosticEntryClientProps) {
  const { learner, setLearner, setMasteryData } = useLearner();
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
    <InteractiveDiagnostic
      learner={learner}
      onComplete={(subject: SubjectCode, mastery: number) => {
        setMasteryData((prev) => ({ ...prev, [subject]: mastery }));
        router.push("/plan");
      }}
      onBack={() => router.push("/dashboard")}
    />
  );
}
