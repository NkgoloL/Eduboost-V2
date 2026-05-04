"use client";

import { useRouter } from "next/navigation";
import { useLearner } from "../../../context/LearnerContext";
import { InteractiveDiagnostic } from "../../../components/eduboost/InteractiveDiagnostic";
import type { SubjectCode } from "../../../lib/api/types";

export default function DiagnosticPage() {
  const { learner, setMasteryData } = useLearner();
  const router = useRouter();

  if (!learner) {
    return null;
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
