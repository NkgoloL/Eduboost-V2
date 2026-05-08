"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useLearner } from "../../context/LearnerContext";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { ErrorMessage } from "../ui/ErrorMessage";

interface RouteGuardProps {
  children: React.ReactNode;
  required: "learner" | "parent" | "teacher" | "admin";
}

function hasGuardianToken() {
  return typeof window !== "undefined" && Boolean(window.localStorage.getItem("guardian_token"));
}

export function RouteGuard({ children, required }: RouteGuardProps) {
  const router = useRouter();
  const { learner, loading } = useLearner();
  const isLearnerRoute = required === "learner";
  const allowed = isLearnerRoute ? Boolean(learner) : hasGuardianToken();

  useEffect(() => {
    if (!loading && !allowed) {
      router.push(required === "parent" ? "/login" : "/");
    }
  }, [allowed, loading, required, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center" role="status" aria-live="polite">
        <LoadingSpinner />
        <p className="mt-4 text-[var(--muted)] font-medium">Checking your session...</p>
      </div>
    );
  }

  if (!allowed) {
    return (
      <ErrorMessage
        title="Session required"
        message={required === "parent" ? "Please log in as a guardian to access this dashboard." : "Please choose a learner profile to continue."}
        onRetry={() => router.push(required === "parent" ? "/login" : "/")}
      />
    );
  }

  return <>{children}</>;
}
