"use client";

import React from "react";

export function LoadingSpinner({ text = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className="animate-spin text-4xl">⏳</div>
      {text && <p className="text-[var(--muted)] font-medium">{text}</p>}
    </div>
  );
}
