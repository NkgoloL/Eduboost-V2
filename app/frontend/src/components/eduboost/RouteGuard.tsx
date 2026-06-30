"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLearner } from "../../context/LearnerContext";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { ErrorMessage } from "../ui/ErrorMessage";

interface RouteGuardProps {
  children: React.ReactNode;
  required: "learner" | "parent" | "teacher" | "admin";
}

async function fetchSessionState(): Promise<{ authenticated: boolean }> {
  try {
    const response = await fetch("/api/auth/session", { cache: "no-store" });
    if (!response.ok) {
      return { authenticated: false };
    }
    const payload = await response.json();
    return { authenticated: Boolean(payload?.authenticated), legacyToken: false } as { authenticated: boolean };
  } catch {
    return { authenticated: false };
  }
}

export function RouteGuard({ children, required }: RouteGuardProps) {
  const router = useRouter();
  const { learner, loading } = useLearner();
  const [sessionLoaded, setSessionLoaded] = useState(false);
  const [guardianAuthenticated, setGuardianAuthenticated] = useState(false);
  const isLearnerRoute = required === "learner";
  const allowed = isLearnerRoute ? Boolean(learner) : guardianAuthenticated;

  useEffect(() => {
    if (isLearnerRoute) {
      setSessionLoaded(true);
      return;
    }
    let active = true;
    fetchSessionState().then((result) => {
      if (active) {
        setGuardianAuthenticated(result.authenticated);
        setSessionLoaded(true);
      }
    });
    return () => {
      active = false;
    };
  }, [isLearnerRoute]);

  useEffect(() => {
    if (!loading && !allowed) {
      router.push(required === "parent" ? "/login" : "/");
    }
  }, [allowed, loading, required, router]);

  if (loading || !sessionLoaded) {
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
