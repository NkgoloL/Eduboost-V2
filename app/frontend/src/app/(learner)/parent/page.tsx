"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ParentDashboard } from "../../../components/eduboost/ParentDashboard";
import { useLearner } from "../../../context/LearnerContext";
import { Card } from "../../../components/ui/Card-legacy";
import { Button } from "../../../components/ui/Button-legacy";

export default function ParentPortalPage() {
  const router = useRouter();
  const { learner } = useLearner();
  const [hasGuardianSession, setHasGuardianSession] = useState(false);

  useEffect(() => {
    setHasGuardianSession(Boolean(window.localStorage.getItem("guardian_token") || window.localStorage.getItem("guardian_id")));
  }, []);

  if (hasGuardianSession) return <ParentDashboard onBack={() => router.push("/")} />;
  if (!learner) return null;
  const shareId = learner.id || learner.learner_id;

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">Invite Your Guardian</h1>
        <p className="text-[var(--muted)] font-medium">Share your learner ID with your parent or guardian so they can view your progress reports.</p>
      </header>
      <Card className="p-8 border-none bg-white shadow-xl flex flex-col items-center text-center">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Your Learner ID</h2>
        <div className="w-full bg-gray-50 p-4 rounded-xl border-2 border-dashed border-gray-200 font-mono text-blue-600 font-bold break-all mb-8">{shareId}</div>
        <Button variant="secondary" className="w-full py-4" onClick={() => void navigator.clipboard.writeText(shareId)}>Copy ID to Share</Button>
      </Card>
    </div>
  );
}
