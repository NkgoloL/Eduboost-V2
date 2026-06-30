"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { assignReviewBatch, bulkApproveReview, bulkQuarantineReview, bulkRejectReview, fetchContentFactoryReviewQueue, fetchReviewBundle, type ReviewBundle, type ReviewQueueItem } from "@/lib/api/contentFactory";
import BulkReviewToolbar from "./BulkReviewToolbar";
import ReviewBundleDrawer from "./ReviewBundleDrawer";

export default function ReviewQueuePanel() {
  const [items, setItems] = useState<ReviewQueueItem[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [risk, setRisk] = useState("");
  const [scope, setScope] = useState("");
  const [bundle, setBundle] = useState<ReviewBundle | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async (filters?: { risk?: string; scope?: string }) => {
    const params: Record<string, string> = {};
    const riskFilter = filters?.risk ?? "";
    const scopeFilter = filters?.scope ?? "";
    if (riskFilter) params.risk_level = riskFilter;
    if (scopeFilter) params.scope_id = scopeFilter;
    const page = await fetchContentFactoryReviewQueue(params);
    setItems(page.items);
  }, []);

  const loadCurrentFilters = useCallback(() => load({ risk, scope }), [load, risk, scope]);

  useEffect(() => { void load(); }, [load]);
  const selectedItems = useMemo(() => items.filter((item) => selected.includes(item.artifact_id)), [items, selected]);

  async function run(action: () => Promise<unknown>) {
    setMessage(null);
    try {
      const result = await action();
      setMessage(JSON.stringify(result));
      setSelected([]);
      await loadCurrentFilters();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Review action failed");
    }
  }

  return (
    <section className="rounded border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Human Review Queue</h2>
          <div className="text-sm text-slate-400">Bulk actions require explicit reviewer input and keep human review in the loop.</div>
        </div>
        <div className="flex gap-2">
          <input className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" placeholder="Scope" value={scope} onChange={(event) => setScope(event.target.value)} />
          <select className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" value={risk} onChange={(event) => setRisk(event.target.value)}>
            <option value="">All risk</option><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option>
          </select>
          <button className="rounded bg-slate-700 px-3 py-2 text-sm" onClick={() => void loadCurrentFilters()}>Filter</button>
        </div>
      </div>

      <BulkReviewToolbar selectedCount={selected.length} onApprove={(notes) => run(() => bulkApproveReview(selected, notes))} onReject={(reason) => run(() => bulkRejectReview(selected, reason))} onQuarantine={(reason) => run(() => bulkQuarantineReview(selected, reason))} onAssign={(reviewerId) => run(() => assignReviewBatch(selected, reviewerId))} />
      {message && <div className="mt-3 rounded border border-slate-700 bg-slate-950 p-3 text-sm text-slate-300">{message}</div>}

      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[800px] text-left text-sm">
          <thead className="border-b border-slate-800 text-slate-400"><tr><th className="py-2 pr-4">Select</th><th className="py-2 pr-4">Scope</th><th className="py-2 pr-4">Layer</th><th className="py-2 pr-4">CAPS</th><th className="py-2 pr-4">Risk</th><th className="py-2 pr-4">Validation</th><th className="py-2 pr-4">Provenance</th><th className="py-2 pr-4">Evidence</th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.artifact_id} className="border-b border-slate-800">
                <td className="py-2 pr-4"><input type="checkbox" checked={selected.includes(item.artifact_id)} onChange={(event) => setSelected(event.target.checked ? [...selected, item.artifact_id] : selected.filter((id) => id !== item.artifact_id))} /></td>
                <td className="py-2 pr-4">{item.scope_id}</td><td className="py-2 pr-4">{item.content_layer}</td><td className="py-2 pr-4">{item.caps_ref}</td>
                <td className="py-2 pr-4"><Badge value={item.risk_level} /></td><td className="py-2 pr-4">{item.validation_status}</td><td className="py-2 pr-4">{item.provenance_status}</td>
                <td className="py-2 pr-4"><button className="text-cyan-300" onClick={() => void run(async () => { const next = await fetchReviewBundle(item.artifact_id); setBundle(next); return "bundle loaded"; })}>Open</button></td>
              </tr>
            ))}
          </tbody>
        </table>
        {!items.length && <p className="mt-3 text-sm text-slate-400">No pending review artifacts match the current filters.</p>}
      </div>
      <ReviewBundleDrawer bundle={bundle} onClose={() => setBundle(null)} />
    </section>
  );
}

function Badge({ value }: { value: string }) {
  const color = value === "low" ? "bg-emerald-500 text-slate-950" : value === "medium" ? "bg-amber-400 text-slate-950" : "bg-red-500 text-white";
  return <span className={`rounded px-2 py-1 text-xs font-semibold ${color}`}>{value}</span>;
}
