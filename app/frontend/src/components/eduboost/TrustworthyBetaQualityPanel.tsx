"use client";

export type TrustworthyBetaQualityPanelProps = {
  context?: string;
  supportEmail?: string;
};

const DEFAULT_SUPPORT_EMAIL = "support@eduboost.co.za";

function encodedMailto(supportEmail: string, context: string) {
  const subject = encodeURIComponent(`EduBoost beta quality issue - ${context}`);
  const body = encodeURIComponent([
    "Please describe the issue:",
    "",
    "Where did it happen?",
    "What did you expect?",
    "What did you see instead?",
    "",
    "Do not include learner ID numbers, passwords, medical details, or other sensitive personal information.",
  ].join("\n"));
  return `mailto:${supportEmail}?subject=${subject}&body=${body}`;
}

export function TrustworthyBetaQualityPanel({
  context = "general beta journey",
  supportEmail = DEFAULT_SUPPORT_EMAIL,
}: TrustworthyBetaQualityPanelProps) {
  const href = encodedMailto(supportEmail, context);
  return (
    <section
      aria-labelledby="trustworthy-beta-quality-title"
      className="rounded-2xl border border-slate-700 bg-slate-900/70 p-4 text-slate-100 shadow-sm"
      data-testid="trustworthy-beta-quality-panel"
    >
      <div className="flex flex-col gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-300">
            Trustworthy beta quality
          </p>
          <h2 id="trustworthy-beta-quality-title" className="text-lg font-bold">
            Report issues, correct content, and route reviews safely
          </h2>
        </div>

        <a
          className="inline-flex w-fit items-center rounded-lg border border-emerald-400 px-3 py-2 text-sm font-semibold text-emerald-100 hover:bg-emerald-400/10"
          href={href}
          aria-label={`Report issue for ${context}`}
          data-testid="rr018-report-issue-button"
        >
          Report issue
        </a>

        <dl className="grid gap-3 text-sm md:grid-cols-3">
          <div className="rounded-xl border border-slate-700 p-3" data-testid="rr018-content-correction-workflow">
            <dt className="font-semibold">Content correction workflow</dt>
            <dd className="mt-1 text-slate-300">
              Learner, guardian, or educator reports are triaged, corrected, reviewed, and closed with an audit trail.
            </dd>
          </div>
          <div className="rounded-xl border border-slate-700 p-3" data-testid="rr018-human-review-queue">
            <dt className="font-semibold">Human review queue</dt>
            <dd className="mt-1 text-slate-300">
              Safety, CAPS, POPIA, and billing-sensitive issues are routed to a human reviewer before closure.
            </dd>
          </div>
          <div className="rounded-xl border border-slate-700 p-3" data-testid="rr018-educator-caps-priority-review">
            <dt className="font-semibold">Educator CAPS priority review</dt>
            <dd className="mt-1 text-slate-300">
              Priority Grade 4 Mathematics topics require educator review before public-beta quality claims.
            </dd>
          </div>
        </dl>

        <p className="text-xs text-slate-400" data-testid="rr018-feedback-privacy-boundary">
          Privacy boundary: reports must not include learner ID numbers, passwords, medical details, payment card data, or raw AI prompts/output.
        </p>
      </div>
    </section>
  );
}
