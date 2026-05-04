"use client";

import React from "react";

interface LoadingSpinnerProps {
  text?: string;
  size?: "sm" | "md" | "lg";
}

const SIZE_CLASS: Record<NonNullable<LoadingSpinnerProps["size"]>, string> = {
  sm: "text-xl",
  md: "text-4xl",
  lg: "text-6xl",
};

export function LoadingSpinner({ text = "Loading...", size = "md" }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className={`animate-spin ${SIZE_CLASS[size]}`}>⏳</div>
      {text && <p className="text-[var(--muted)] font-medium">{text}</p>}
    </div>
  );
}
