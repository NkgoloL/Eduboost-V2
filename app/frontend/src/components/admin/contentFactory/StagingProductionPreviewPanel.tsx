import { useCallback, useEffect, useState } from "react";
import {
  fetchStagingPreview,
  fetchProductionPreview,
  fetchProductionPreviewByCapsRef,
  type ContentScope,
  type StagingPreviewReport,
  type LearnerScopeContentSummary,
  type LearnerDiagnosticItem,
  type LearnerLesson,
} from "@/lib/api/contentFactory";

interface Props {
  scopes: ContentScope[];
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-950 p-3">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="text-lg font-semibold text-slate-100">{value}</div>
    </div>
  );
}

export default function StagingProductionPreviewPanel({ scopes }: Props) {
  const [scopeId, setScopeId] = useState(scopes[0]?.scope_id ?? "");
  const [capsRef, setCapsRef] = useState("");
  const [stagingReport, setStagingReport] = useState<StagingPreviewReport | null>(null);
  const [productionSummary, setProductionSummary] = useState<LearnerScopeContentSummary | null>(null);
  const [productionItems, setProductionItems] = useState<{ diagnostic_items: LearnerDiagnosticItem[]; lessons: LearnerLesson[] } | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<"summary" | "caps">("summary");

  const refreshStaging = useCallback(async () => {
    if (!scopeId) return;
    setLoading(true);
    setMessage(null);
    try {
      const report = await fetchStagingPreview(scopeId);
      setStagingReport(report);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to fetch staging preview");
    } finally {
      setLoading(false);
    }
  }, [scopeId]);

  const refreshProduction = useCallback(async () => {
    if (!scopeId) return;
    setLoading(true);
    setMessage(null);
    try {
      if (view === "summary") {
        const summary = await fetchProductionPreview(scopeId);
        setProductionSummary(summary);
        setProductionItems(null);
      } else {
        const items = await fetchProductionPreviewByCapsRef(scopeId, capsRef);
        setProductionItems(items);
        setProductionSummary(null);
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to fetch production preview");
    } finally {
      setLoading(false);
    }
  }, [capsRef, scopeId, view]);

  useEffect(() => {
    setScopeId(scopes[0]?.scope_id ?? "");
  }, [scopes]);

  useEffect(() => {
    if (scopeId) {
      void refreshStaging();
      void refreshProduction();
    }
  }, [refreshProduction, refreshStaging, scopeId]);

  useEffect(() => {
    if (scopeId && capsRef && view === "caps") {
      void refreshProduction();
    }
  }, [capsRef, refreshProduction, scopeId, view]);

  const stagingCount = stagingReport?.total_artifacts_count ?? 0;
  const stagingActive = stagingReport?.active_artifacts_count ?? 0;
  const stagingPending = stagingReport?.pending_artifacts_count ?? 0;
  const productionCount = productionSummary?.total_artifacts_count ?? 0;
  const productionDiagnostic = productionSummary?.diagnostic_items_count ?? 0;
  const productionLessons = productionSummary?.lessons_count ?? 0;

  return (
    <section className="rounded border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Staging vs Production Preview</h2>
          <div className="text-sm text-slate-400">{scopeId || "No scope selected"}</div>
        </div>
        <div className="flex flex-wrap gap-2">
          <select className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" value={scopeId} onChange={(event) => setScopeId(event.target.value)}>
            {scopes.map((scope) => <option key={scope.scope_id} value={scope.scope_id}>{scope.scope_id}</option>)}
          </select>
          <button disabled={!scopeId || loading} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => void refreshStaging()}>
            Refresh staging
          </button>
          <button disabled={!scopeId || loading} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => void refreshProduction()}>
            Refresh production
          </button>
        </div>
      </div>

      {message && <div className="mb-4 rounded border border-amber-700 bg-amber-950 p-3 text-sm text-amber-100">{message}</div>}

      <div className="mb-4 flex gap-2">
        <button className={`px-3 py-2 text-sm font-semibold ${view === "summary" ? "bg-cyan-500 text-slate-950" : "bg-slate-800 text-slate-300"}`} onClick={() => setView("summary")}>
          Summary
        </button>
        <button className={`px-3 py-2 text-sm font-semibold ${view === "caps" ? "bg-cyan-500 text-slate-950" : "bg-slate-800 text-slate-300"}`} onClick={() => setView("caps")}>
          By CAPS Ref
        </button>
      </div>

      {view === "summary" && (
        <>
          <div className="mb-4 grid gap-3 md:grid-cols-3">
            <div className="rounded border border-slate-800 bg-slate-950 p-3">
              <h3 className="mb-2 text-sm font-semibold text-slate-300">Staging</h3>
              <div className="grid gap-2 md:grid-cols-2">
                <Metric label="Total" value={stagingCount} />
                <Metric label="Active" value={stagingActive} />
                <Metric label="Pending" value={stagingPending} />
                <Metric label="Learner visible" value={stagingReport?.learner_visible_count ?? 0} />
              </div>
            </div>
            <div className="rounded border border-slate-800 bg-slate-950 p-3">
              <h3 className="mb-2 text-sm font-semibold text-slate-300">Production</h3>
              <div className="grid gap-2 md:grid-cols-2">
                <Metric label="Total" value={productionCount} />
                <Metric label="Diagnostic items" value={productionDiagnostic} />
                <Metric label="Lessons" value={productionLessons} />
                <Metric label="Last promotion" value={productionSummary?.last_promotion_at ? new Date(productionSummary.last_promotion_at).toLocaleDateString() : "Never"} />
              </div>
            </div>
            <div className="rounded border border-slate-800 bg-slate-950 p-3">
              <h3 className="mb-2 text-sm font-semibold text-slate-300">Comparison</h3>
              <div className="space-y-2 text-sm text-slate-400">
                <div>Staging artifacts are <span className="font-semibold text-amber-400">not learner-visible</span></div>
                <div>Production artifacts are <span className="font-semibold text-emerald-400">learner-visible</span></div>
                <div>Staging count: {stagingCount}</div>
                <div>Production count: {productionCount}</div>
                <div>Delta: {stagingCount - productionCount}</div>
              </div>
            </div>
          </div>

          {stagingReport?.artifacts.length ? (
            <div className="rounded border border-slate-800 bg-slate-950 p-3">
              <h3 className="mb-3 text-sm font-semibold text-slate-300">Staging artifacts (not learner-visible)</h3>
              <div className="max-h-64 overflow-auto space-y-1">
                {stagingReport.artifacts.slice(0, 20).map((artifact, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded border border-slate-800 bg-slate-900 px-3 py-2 text-sm">
                    <div className="flex-1">
                      <div className="font-mono text-xs text-slate-400">{artifact.artifact_id}</div>
                      <div className="text-slate-300">{artifact.caps_ref || "No CAPS ref"} · {artifact.layer}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`rounded px-2 py-1 text-xs font-semibold ${artifact.staging_status === "active" ? "bg-emerald-900 text-emerald-100" : "bg-slate-800 text-slate-300"}`}>
                        {artifact.staging_status}
                      </span>
                      <span className="rounded bg-amber-900 px-2 py-1 text-xs font-semibold text-amber-100">
                        Not visible
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </>
      )}

      {view === "caps" && (
        <>
          <div className="mb-4">
            <label className="mb-2 block text-xs uppercase text-slate-500">CAPS Reference</label>
            <input
              type="text"
              className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm font-mono"
              placeholder="e.g., 8.1.1"
              value={capsRef}
              onChange={(event) => setCapsRef(event.target.value)}
            />
          </div>

          {productionItems && (
            <div className="grid gap-4 xl:grid-cols-2">
              <div className="rounded border border-slate-800 bg-slate-950 p-3">
                <h3 className="mb-3 text-sm font-semibold text-slate-300">Production diagnostic items (learner-visible)</h3>
                <div className="max-h-64 overflow-auto space-y-1">
                  {productionItems.diagnostic_items.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between rounded border border-slate-800 bg-slate-900 px-3 py-2 text-sm">
                      <div className="flex-1">
                        <div className="font-mono text-xs text-slate-400">{item.artifact_id}</div>
                        <div className="text-slate-300">{item.title || "No title"}</div>
                      </div>
                      <span className="rounded bg-emerald-900 px-2 py-1 text-xs font-semibold text-emerald-100">
                        Visible
                      </span>
                    </div>
                  ))}
                  {!productionItems.diagnostic_items.length && <div className="text-center text-sm text-slate-500 py-4">No diagnostic items found</div>}
                </div>
              </div>

              <div className="rounded border border-slate-800 bg-slate-950 p-3">
                <h3 className="mb-3 text-sm font-semibold text-slate-300">Production lessons (learner-visible)</h3>
                <div className="max-h-64 overflow-auto space-y-1">
                  {productionItems.lessons.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between rounded border border-slate-800 bg-slate-900 px-3 py-2 text-sm">
                      <div className="flex-1">
                        <div className="font-mono text-xs text-slate-400">{item.artifact_id}</div>
                        <div className="text-slate-300">{item.title || "No title"}</div>
                      </div>
                      <span className="rounded bg-emerald-900 px-2 py-1 text-xs font-semibold text-emerald-100">
                        Visible
                      </span>
                    </div>
                  ))}
                  {!productionItems.lessons.length && <div className="text-center text-sm text-slate-500 py-4">No lessons found</div>}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
