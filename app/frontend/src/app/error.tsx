"use client";

import React from "react";
import { ErrorMessage } from "../components/ui/ErrorMessage";

export default function RootError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main id="main-content" className="min-h-screen flex items-center justify-center p-6">
      <ErrorMessage title="EduBoost hit a snag." message={error.message || "This screen failed to load."} onRetry={reset} />
    </main>
  );
}
