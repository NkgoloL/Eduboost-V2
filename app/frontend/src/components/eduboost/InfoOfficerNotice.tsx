"use client";

import React from "react";

interface InfoOfficerNoticeProps {
  variant?: "card" | "inline";
  className?: string;
}

export function InfoOfficerNotice({ variant = "card", className = "" }: InfoOfficerNoticeProps) {
  const content = (
    <div className={`flex items-start gap-3 ${className}`}>
      <div className="text-2xl flex-shrink-0">⚖️</div>
      <div className="flex-1">
        <h4 className="font-bold text-sm mb-1">POPIA Information Officer</h4>
        <p className="text-xs opacity-90 leading-relaxed">
          For questions about your data rights, consent, or to exercise your POPIA rights under the Protection of Personal Information Act, contact our Information Officer.
        </p>
        <div className="mt-2 text-xs font-medium">
          <span className="opacity-70">Email:</span>{" "}
          <a href="mailto:info.officer@eduboost.sa" className="underline hover:no-underline">
            info.officer@eduboost.sa
          </a>
        </div>
      </div>
    </div>
  );

  if (variant === "inline") {
    return <div className="py-3 px-4 bg-blue-50/50 border border-blue-100 rounded-lg">{content}</div>;
  }

  return (
    <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
      {content}
    </div>
  );
}
