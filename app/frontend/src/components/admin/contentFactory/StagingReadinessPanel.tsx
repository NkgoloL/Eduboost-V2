"use client";

import { useMemo, useState } from "react";
import { runAllScopeStagingVerification, type AllScopeStagingVerificationReport } from "@/lib/api/contentFactory";

type Props = {
  initialReport?: AllScopeStagingVerificationReport | null;
};

export default function StagingReadinessPanel({ initialReport = null }: Props) {
  const [report, setReport] = useState<AllScopeStagingVerificationReport | null>(initialReport);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runVerification() {
    setLoading(true);
    setError(null);
    try {
      setReport(await runAllScopeStagingVerification());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to run staging verification");
    } finally {
      setLoading(false);
    }
  }

  const scopes = useMemo(() => report?.scopes ?? [], [report]);

  return (
    <section className="rounded border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Staging Readiness</h2>
          <div className="text-sm text-slate-400">{report ? `${scopes.length} scopes checked` : "No verification run loaded"}</div>
        </div>
        <button
          type="button"
          onClick={runVerification}
          disabled={loading}
          className="rounded bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
        >
          {loading ? "Running..." : "Run all-scope verification"}
        </button>
      </div>

      {error && <div className="mb-4 rounded border border-red-700 bg-red-950 p-3 text-sm text-red-100">{error}</div>}

      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-slate-800 text-slate-400">
            <tr>
              <th className="py-2 pr-4 font-medium">Scope</th>
              <th className="py-2 pr-4 font-medium">Status</th>
              <th className="py-2 pr-4 font-medium">Blockers</th>
              <th className="py-2 pr-4 font-medium">Stageable</th>
              <th className="py-2 pr-4 font-medium">Layers</th>
              <th className="py-2 pr-4 font-medium">Coverage</th>
            </tr>
          </thead>
          <tbody>
            {scopes.map((scope) => (
              <tr key={scope.scope_id} className="border-b border-slate-800">
                <td className="py-3 pr-4 text-slate-100">{scope.scope_id}</td>
                <td className="py-3 pr-4"><StatusBadge status={scope.status} /></td>
                <td className="py-3 pr-4">{scope.blockers.length}</td>
                <td className="py-3 pr-4">{scope.can_seed_staging ? "Yes" : "No"}</td>
                <td className="py-3 pr-4">
                  {scope.layers.slice(0, 3).map((layer) => (
                    <div key={`${layer.caps_ref}-${layer.layer}`} className="text-slate-300">
                      {layer.layer}: {layer.stageable}/{layer.target}
                    </div>
                  ))}
                </td>
                <td className="py-3 pr-4">
                  <a className="text-cyan-300 hover:text-cyan-200" href={`#coverage-${scope.scope_id}`}>Scope coverage</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!scopes.length && <p className="mt-4 text-sm text-slate-400">Run verification to populate scope readiness.</p>}
    </section>
  );
}

function StatusBadge({ status }: { status: string }) {
  const color = status === "ready_for_staging" ? "bg-emerald-500 text-slate-950" : status === "partially_stageable" ? "bg-amber-400 text-slate-950" : "bg-red-500 text-white";
  return <span className={`inline-flex rounded px-2 py-1 text-xs font-semibold ${color}`}>{status}</span>;
}
