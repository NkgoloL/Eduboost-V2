"use client";

import type { ReviewBundle } from "@/lib/api/contentFactory";

export default function ReviewBundleDrawer({ bundle, onClose }: { bundle: ReviewBundle | null; onClose: () => void }) {
  if (!bundle) return null;
  return (
    <aside className="fixed inset-y-0 right-0 z-40 w-full max-w-xl overflow-y-auto border-l border-slate-800 bg-slate-950 p-5 shadow-2xl">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Review Evidence</h2>
        <button className="rounded border border-slate-700 px-3 py-1 text-sm" onClick={onClose}>Close</button>
      </div>
      <Evidence title="Risk" value={`${bundle.review_risk.level} (${bundle.review_risk.score})`} />
      <Evidence title="Validation" value={String(bundle.validation_report?.passed ?? "missing")} />
      <Evidence title="Provenance" value={String(bundle.provenance.passed ?? false)} />
      <section className="mt-4">
        <h3 className="mb-2 text-sm font-semibold text-slate-300">Sources</h3>
        <div className="space-y-2">
          {bundle.sources.map((source, index) => (
            <div key={index} className="rounded border border-slate-800 bg-slate-900 p-3 text-sm">
              <div>{String(source.source_document_id ?? "source")}</div>
              <div className="text-slate-400">{String(source.source_chunk_id ?? "chunk")}</div>
              <div className="mt-2 text-slate-300">{String(source.citation_text ?? "No citation text")}</div>
            </div>
          ))}
        </div>
      </section>
      <section className="mt-4">
        <h3 className="mb-2 text-sm font-semibold text-slate-300">Artifact</h3>
        <pre className="max-h-80 overflow-auto rounded bg-slate-900 p-3 text-xs text-slate-300">{JSON.stringify(bundle.artifact, null, 2)}</pre>
      </section>
    </aside>
  );
}

function Evidence({ title, value }: { title: string; value: string }) {
  return <div className="mb-2 flex justify-between rounded border border-slate-800 bg-slate-900 p-3 text-sm"><span className="text-slate-400">{title}</span><span>{value}</span></div>;
}
