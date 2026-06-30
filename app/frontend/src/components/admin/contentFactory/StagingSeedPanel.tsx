"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  dryRunStagingSeed,
  fetchStagingSeedRunItems,
  fetchStagingSeedRuns,
  rollbackStagingSeedRun,
  seedStaging,
  verifyStagingSeedRun,
  verifyScopeStagingRead,
  type ContentScope,
  type StagingReadVerification,
  type StagingSeedItem,
  type StagingSeedPlan,
  type StagingSeedRun,
} from "@/lib/api/contentFactory";

type Props = {
  scopes: ContentScope[];
};

export default function StagingSeedPanel({ scopes }: Props) {
  const [scopeId, setScopeId] = useState(scopes[0]?.scope_id ?? "");
  const [plan, setPlan] = useState<StagingSeedPlan | null>(null);
  const [runs, setRuns] = useState<StagingSeedRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState("");
  const [items, setItems] = useState<StagingSeedItem[]>([]);
  const [verification, setVerification] = useState<StagingReadVerification | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const selectedRun = useMemo(() => runs.find((run) => run.seed_run_id === selectedRunId) ?? runs[0], [runs, selectedRunId]);
  const blockers = plan?.skipped ?? [];

  const refreshRuns = useCallback(async (nextScopeId: string) => {
    const page = await fetchStagingSeedRuns(nextScopeId || undefined);
    setRuns(page.items);
    const nextRunId = page.items[0]?.seed_run_id ?? "";
    setSelectedRunId((current) => current || nextRunId);
    if (nextRunId) setItems(await fetchStagingSeedRunItems(nextRunId));
  }, []);

  async function runAction(action: () => Promise<void>) {
    setLoading(true);
    setMessage(null);
    try {
      await action();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Staging seed action failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setScopeId(scopes[0]?.scope_id ?? "");
  }, [scopes]);

  useEffect(() => {
    if (scopeId) void refreshRuns(scopeId).catch(() => undefined);
  }, [refreshRuns, scopeId]);

  useEffect(() => {
    if (!selectedRunId) return;
    void fetchStagingSeedRunItems(selectedRunId).then(setItems).catch(() => setItems([]));
  }, [selectedRunId]);

  return (
    <section className="rounded border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Staging Seed</h2>
          <div className="text-sm text-slate-400">{scopeId || "No scope selected"}</div>
        </div>
        <div className="flex flex-wrap gap-2">
          <select className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" value={scopeId} onChange={(event) => setScopeId(event.target.value)}>
            {scopes.map((scope) => <option key={scope.scope_id} value={scope.scope_id}>{scope.scope_id}</option>)}
          </select>
          <button disabled={!scopeId || loading} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => void runAction(async () => setPlan(await dryRunStagingSeed(scopeId)))}>
            Dry run seed
          </button>
          <button disabled={!scopeId || loading} className="rounded bg-emerald-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => void runAction(async () => { await seedStaging(scopeId, true); await refreshRuns(scopeId); })}>
            Seed staging
          </button>
          <button disabled className="rounded border border-slate-700 px-3 py-2 text-sm text-slate-500">
            Production promotion blocked
          </button>
        </div>
      </div>

      {message && <div className="mb-4 rounded border border-amber-700 bg-amber-950 p-3 text-sm text-amber-100">{message}</div>}

      <div className="mb-4 grid gap-3 md:grid-cols-4">
        <Metric label="Seedable" value={plan?.seedable_count ?? 0} />
        <Metric label="Skipped" value={plan?.skipped_count ?? 0} />
        <Metric label="Runs" value={runs.length} />
        <Metric label="Verification" value={verification ? (verification.passed ? "passed" : "failed") : "not run"} />
      </div>

      {blockers.length > 0 && (
        <div className="mb-4 rounded border border-slate-800 bg-slate-950 p-3">
          <h3 className="mb-2 text-sm font-semibold text-slate-300">Blockers and skips</h3>
          <div className="space-y-1 text-sm text-slate-400">
            {blockers.slice(0, 8).map((item) => <div key={item.artifact_id}>{item.artifact_id}: {item.reason}</div>)}
          </div>
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <div className="rounded border border-slate-800 bg-slate-950 p-3">
          <h3 className="mb-3 text-sm font-semibold text-slate-300">Seed run history</h3>
          <div className="space-y-2">
            {runs.map((run) => (
              <button key={run.seed_run_id} className={`w-full rounded border px-3 py-2 text-left text-sm ${selectedRun?.seed_run_id === run.seed_run_id ? "border-cyan-500 bg-slate-900" : "border-slate-800 bg-slate-950"}`} onClick={() => setSelectedRunId(run.seed_run_id)}>
                <div className="truncate">{run.seed_run_id}</div>
                <div className="mt-1 text-slate-400">{run.status} · {run.seeded_count} seeded · {run.skipped_count} skipped</div>
              </button>
            ))}
            {!runs.length && <div className="text-sm text-slate-500">No staging seed runs yet.</div>}
          </div>
        </div>

        <div className="overflow-x-auto rounded border border-slate-800 bg-slate-950 p-3">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-300">Seed items</h3>
            <div className="flex gap-2">
              <button disabled={!selectedRun || loading} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => selectedRun && void runAction(async () => setVerification(await verifyStagingSeedRun(selectedRun.seed_run_id)))}>
                Verify run
              </button>
              <button disabled={!scopeId || loading} className="rounded border border-slate-700 px-3 py-2 text-sm" onClick={() => void runAction(async () => setVerification(await verifyScopeStagingRead(scopeId)))}>
                Verify scope
              </button>
              <button disabled={!selectedRun || loading} className="rounded bg-red-500 px-3 py-2 text-sm font-semibold text-white disabled:bg-slate-700 disabled:text-slate-400" onClick={() => selectedRun && void runAction(async () => { await rollbackStagingSeedRun(selectedRun.seed_run_id, "admin rollback from staging seed panel"); await refreshRuns(scopeId); })}>
                Rollback
              </button>
            </div>
          </div>
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-slate-800 text-slate-400"><tr><th className="py-2 pr-4">Artifact</th><th className="py-2 pr-4">Layer</th><th className="py-2 pr-4">CAPS</th><th className="py-2 pr-4">Status</th><th className="py-2 pr-4">Target</th><th className="py-2 pr-4">Skip reason</th></tr></thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-b border-slate-900">
                  <td className="py-2 pr-4 font-mono text-xs">{item.artifact_id}</td>
                  <td className="py-2 pr-4">{item.layer}</td>
                  <td className="py-2 pr-4">{item.caps_ref ?? "-"}</td>
                  <td className="py-2 pr-4">{item.status}</td>
                  <td className="py-2 pr-4 font-mono text-xs">{item.target_record_id ?? "-"}</td>
                  <td className="py-2 pr-4 text-slate-400">{item.skip_reason ?? "-"}</td>
                </tr>
              ))}
              {!items.length && <tr><td colSpan={6} className="py-6 text-center text-slate-500">No seed items selected.</td></tr>}
            </tbody>
          </table>
          {verification?.errors.length ? <pre className="mt-3 max-h-32 overflow-auto rounded bg-red-950 p-3 text-xs text-red-100">{verification.errors.join("\n")}</pre> : null}
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return <div className="rounded border border-slate-800 bg-slate-950 p-3"><div className="text-xs uppercase text-slate-500">{label}</div><div className="mt-1 text-xl font-semibold">{value}</div></div>;
}
