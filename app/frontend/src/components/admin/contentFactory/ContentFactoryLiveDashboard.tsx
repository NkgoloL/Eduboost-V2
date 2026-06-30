"use client";

import { useEffect, useMemo, useState } from "react";
import GenerationRunsPanel from "./GenerationRunsPanel";
import ReviewQueuePanel from "./ReviewQueuePanel";
import StagingReadinessPanel from "./StagingReadinessPanel";
import StagingSeedPanel from "./StagingSeedPanel";
import ProductionPromotionPanel from "./ProductionPromotionPanel";
import StagingProductionPreviewPanel from "./StagingProductionPreviewPanel";
import FullGenerationPanel from "./FullGenerationPanel";
import {
  fetchAdminEtlStatus,
  fetchContentFactoryCoverage,
  fetchContentFactoryReviewQueue,
  fetchContentFactoryRuns,
  fetchContentFactoryScopes,
  type ReviewQueuePage,
  type ContentScope,
  type EtlStatus,
  type GenerationRun,
  type ScopeCoverageReport,
} from "@/lib/api/contentFactory";

type DashboardState = {
  scopes: ContentScope[];
  coverage: ScopeCoverageReport | null;
  runs: GenerationRun[];
  reviewQueue: ReviewQueuePage | null;
  etlStatus: EtlStatus | null;
};

const emptyState: DashboardState = {
  scopes: [],
  coverage: null,
  runs: [],
  reviewQueue: null,
  etlStatus: null,
};

export default function ContentFactoryLiveDashboard() {
  const [state, setState] = useState<DashboardState>(emptyState);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const scopes = await fetchContentFactoryScopes();
        const primaryScope = scopes[0]?.scope_id;
        const [coverage, runs, reviewQueue, etlStatus] = await Promise.all([
          primaryScope ? fetchContentFactoryCoverage(primaryScope) : Promise.resolve(null),
          fetchContentFactoryRuns(),
          fetchContentFactoryReviewQueue(),
          fetchAdminEtlStatus(),
        ]);
        if (!cancelled) setState({ scopes, coverage, runs, reviewQueue, etlStatus });
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Unable to load Content Factory data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const layerRows = useMemo(() => Object.entries(state.coverage?.layers ?? {}), [state.coverage]);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="flex flex-col gap-2 border-b border-slate-800 pb-5">
          <p className="text-sm uppercase tracking-wide text-cyan-300">Admin</p>
          <h1 className="text-3xl font-semibold">Content Factory Control Plane</h1>
        </header>

        {loading && <div className="rounded border border-slate-800 bg-slate-900 p-4">Loading live admin data...</div>}
        {error && <div className="rounded border border-red-700 bg-red-950 p-4 text-red-100">{error}</div>}

        <section className="grid gap-4 md:grid-cols-4">
          <Metric label="Scopes" value={state.scopes.length} />
          <Metric label="Runs" value={state.runs.length} />
          <Metric label="Review Queue" value={state.reviewQueue?.total ?? 0} />
          <Metric label="ETL" value={state.etlStatus?.status ?? "unknown"} />
        </section>

        <StagingReadinessPanel />

        <StagingSeedPanel scopes={state.scopes} />

        <ProductionPromotionPanel scopes={state.scopes} />

        <StagingProductionPreviewPanel scopes={state.scopes} />

        <FullGenerationPanel scopes={state.scopes} />

        <GenerationRunsPanel runs={state.runs} />

        <ReviewQueuePanel />

        <section className="grid gap-6 lg:grid-cols-2">
          <Panel title="Scope Coverage">
            <div className="space-y-3">
              <div className="text-sm text-slate-300">{state.coverage?.scope_id ?? "No scope selected"}</div>
              {layerRows.map(([layer, summary]) => (
                <div key={layer} className="flex items-center justify-between border-b border-slate-800 py-2 text-sm">
                  <span>{layer}</span>
                  <span>{summary.approved_total}/{summary.target_total} approved</span>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Recent Runs">
            <div className="space-y-2">
              {state.runs.slice(0, 8).map((run) => (
                <div key={run.run_id} className="flex items-center justify-between text-sm">
                  <span className="truncate pr-4">{run.run_id}</span>
                  <span className="rounded bg-slate-800 px-2 py-1">{run.status}</span>
                </div>
              ))}
              {!state.runs.length && <p className="text-sm text-slate-400">No generation runs yet.</p>}
            </div>
          </Panel>
        </section>
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-900 p-4">
      <div className="text-sm text-slate-400">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded border border-slate-800 bg-slate-900 p-5">
      <h2 className="mb-4 text-lg font-semibold">{title}</h2>
      {children}
    </section>
  );
}
