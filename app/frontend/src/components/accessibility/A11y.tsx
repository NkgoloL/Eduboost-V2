"use client";

import React from "react";

export function SkipLink({ target = "main-content" }: { target?: string }) {
  return (
    <a href={`#${target}`} className="skip-link">
      Skip to main content
    </a>
  );
}

export function ScreenReaderStatus({ children }: { children: React.ReactNode }) {
  return (
    <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
      {children}
    </div>
  );
}
