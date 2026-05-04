"use client";

import React from "react";
import { Button } from "./Button";

interface ErrorMessageProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({ title = "Oops! Something went wrong.", message, onRetry, className = "" }: ErrorMessageProps) {
  return (
    <div className={`bg-red-50 border-2 border-red-200 rounded-[var(--radius)] p-6 text-center max-w-md mx-auto ${className}`}>
      <div className="text-4xl mb-4">⚠️</div>
      <h3 className="font-['Baloo_2'] text-xl text-red-800 mb-2">{title}</h3>
      <p className="text-red-600 mb-6">{message || "We couldn't load the data. Please try again."}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="secondary" className="bg-white hover:bg-red-50 text-red-700 border-red-200">
          Try Again
        </Button>
      )}
    </div>
  );
}
