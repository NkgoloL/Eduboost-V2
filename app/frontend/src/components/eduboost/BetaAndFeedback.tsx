"use client";

interface FeedbackButtonProps {
  context?: string;
}

export function BetaLabel() {
  return (
    <span className="inline-flex items-center rounded-full border border-yellow-400/60 bg-yellow-400/10 px-3 py-1 text-xs font-black uppercase tracking-wide text-yellow-200" aria-label="Private beta, limited CAPS coverage">
      Private beta · limited CAPS scope
    </span>
  );
}

export function FeedbackButton({ context = "general" }: FeedbackButtonProps) {
  const href = `mailto:support@eduboost.co.za?subject=EduBoost%20beta%20feedback%20-%20${encodeURIComponent(context)}`;
  return (
    <a className="btn-secondary inline-flex items-center justify-center gap-2" href={href} aria-label={`Report feedback or content issue for ${context}`}>
      <span aria-hidden="true">🐞</span>
      Report issue
    </a>
  );
}
