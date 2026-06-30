"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  dryRunProductionPromotion,
  fetchProductionGate,
  fetchPromotionEvents,
  fetchPromotionEvent,
  fetchPromotionEventItems,
  promoteProduction,
  rollbackPromotionEvent,
  verifyPromotionEvent,
  verifyScopeProductionRead,
  type ContentScope,
  type ProductionGateBlocker,
  type ProductionGateReport,
  type ProductionPromotionPlan,
  type ProductionPromotionResult,
  type ProductionReadVerificationReport,
  type ScopeProductionReadReport,
} from "@/lib/api/contentFactory";

type Props = {
  scopes: ContentScope[];
};

type PromotionEventItem = {
  artifact_id: string | number;
  layer?: string;
  caps_ref?: string | null;
  artifact_type?: string;
  production_status?: string;
};

function toPromotionEventItems(rawItems: Array<Record<string, unknown>>): PromotionEventItem[] {
  return rawItems.map((item) => ({
    artifact_id: typeof item.artifact_id === "string" || typeof item.artifact_id === "number" ? item.artifact_id : "",
    layer: typeof item.layer === "string" ? item.layer : undefined,
    caps_ref: typeof item.caps_ref === "string" ? item.caps_ref : null,
    artifact_type: typeof item.artifact_type === "string" ? item.artifact_type : undefined,
    production_status: typeof item.production_status === "string" ? item.production_status : undefined,
  }));
}

export default function ProductionPromotionPanel({ scopes }: Props) {
  const [scopeId, setScopeId] = useState(scopes[0]?.scope_id ?? "");
  const [gateReport, setGateReport] = useState<ProductionGateReport | null>(null);
  const [plan, setPlan] = useState<ProductionPromotionPlan | null>(null);
  const [events, setEvents] = useState<ProductionPromotionResult[]>([]);
  const [selectedEventId, setSelectedEventId] = useState("");
  const [selectedEvent, setSelectedEvent] = useState<ProductionPromotionResult | null>(null);
  const [eventItems, setEventItems] = useState<PromotionEventItem[]>([]);
  const [verification, setVerification] = useState<ProductionReadVerificationReport | null>(null);
  const [scopeVerification, setScopeVerification] = useState<ScopeProductionReadReport | null>(null);
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const blockers = gateReport?.blockers ?? [];
  const expectedConfirmation = `PROMOTE ${scopeId} TO PRODUCTION`;
  const canPromote = gateReport?.status === "promotable" && confirmation === expectedConfirmation;

  const refreshEvents = useCallback(async (nextScopeId: string) => {
    const page = await fetchPromotionEvents(nextScopeId || undefined);
    setEvents(page.items);
    const nextEventId = page.items[0]?.promotion_event_id ?? "";
    setSelectedEventId((current) => current || nextEventId);
    if (nextEventId) {
      const event = await fetchPromotionEvent(nextEventId);
      setSelectedEvent(event);
      const items = await fetchPromotionEventItems(nextEventId);
      setEventItems(toPromotionEventItems(items.items));
    }
  }, []);

  async function runAction(action: () => Promise<void>) {
    setLoading(true);
    setMessage(null);
    try {
      await action();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Production promotion action failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setScopeId(scopes[0]?.scope_id ?? "");
  }, [scopes]);

  useEffect(() => {
    if (scopeId) {
      void fetchProductionGate(scopeId).then(setGateReport).catch(() => setGateReport(null));
      void verifyScopeProductionRead(scopeId).then(setScopeVerification).catch(() => setScopeVerification(null));
      void refreshEvents(scopeId).catch(() => undefined);
    }
  }, [refreshEvents, scopeId]);

  useEffect(() => {
    if (!selectedEventId) return;
    void fetchPromotionEvent(selectedEventId).then(setSelectedEvent).catch(() => setSelectedEvent(null));
    void fetchPromotionEventItems(selectedEventId)
      .then((items) => setEventItems(toPromotionEventItems(items.items)))
      .catch(() => setEventItems([]));
  }, [selectedEventId]);

  return (
    <section className="rounded border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Production Promotion</h2>
          <div className="text-sm text-slate-400">{scopeId || "No scope selected"}</div>
        </div>
        <div className="flex flex-wrap gap-2">
          <select className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" value={scopeId} onChange={(event) => setScopeId(event.target.value)}>
            {scopes.map((scope) => <option key={scope.scope_id} value={scope.scope_id}>{scope.scope_id}</option>)}
          </select>
          <button disabled={!scopeId || loading} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => void runAction(async () => setGateReport(await fetchProductionGate(scopeId)))}>
            Check gate
          </button>
          <button disabled={!scopeId || loading} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => void runAction(async () => setPlan(await dryRunProductionPromotion(scopeId)))}>
            Dry run promotion
          </button>
        </div>
      </div>

      {message && <div className="mb-4 rounded border border-amber-700 bg-amber-950 p-3 text-sm text-amber-100">{message}</div>}

      <div className="mb-4 grid gap-3 md:grid-cols-4">
        <Metric label="Gate status" value={gateReport?.status ?? "not checked"} />
        <Metric label="Promotable" value={plan?.promotable_count ?? 0} />
        <Metric label="Skipped" value={plan?.skipped_count ?? 0} />
        <Metric label="Production verification" value={scopeVerification ? (scopeVerification.passed ? "passed" : "failed") : "not run"} />
      </div>

      {blockers.length > 0 && (
        <div className="mb-4 rounded border border-slate-800 bg-slate-950 p-3">
          <h3 className="mb-2 text-sm font-semibold text-slate-300">Blockers</h3>
          <div className="space-y-1 text-sm text-slate-400">
            {blockers.slice(0, 8).map((item, idx) => <div key={idx}>{item.type}: {item.message}</div>)}
          </div>
        </div>
      )}

      <div className="mb-4 rounded border border-slate-800 bg-slate-950 p-3">
        <h3 className="mb-3 text-sm font-semibold text-slate-300">Promote to production</h3>
        <div className="mb-3">
          <label className="mb-2 block text-xs uppercase text-slate-500">Confirmation</label>
          <input
            type="text"
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm font-mono"
            placeholder={expectedConfirmation}
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
          />
          <div className="mt-1 text-xs text-slate-500">Type exactly: {expectedConfirmation}</div>
        </div>
        <button
          disabled={!canPromote || loading}
          className="rounded bg-emerald-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400"
          onClick={() => void runAction(async () => {
            await promoteProduction(scopeId, { confirmation });
            setConfirmation("");
            await refreshEvents(scopeId);
          })}
        >
          Promote production
        </button>
      </div>

      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <div className="rounded border border-slate-800 bg-slate-950 p-3">
          <h3 className="mb-3 text-sm font-semibold text-slate-300">Promotion event history</h3>
          <div className="space-y-2">
            {events.map((event) => (
              <button key={event.promotion_event_id} className={`w-full rounded border px-3 py-2 text-left text-sm ${selectedEvent?.promotion_event_id === event.promotion_event_id ? "border-cyan-500 bg-slate-900" : "border-slate-800 bg-slate-950"}`} onClick={() => setSelectedEventId(event.promotion_event_id)}>
                <div className="truncate">{event.promotion_event_id}</div>
                <div className="mt-1 text-slate-400">{event.status} · {event.promoted_count} promoted</div>
              </button>
            ))}
            {!events.length && <div className="text-sm text-slate-500">No promotion events yet.</div>}
          </div>
        </div>

        <div className="overflow-x-auto rounded border border-slate-800 bg-slate-950 p-3">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-300">Promotion items</h3>
            <div className="flex gap-2">
              <button disabled={!selectedEvent || loading} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => selectedEvent && void runAction(async () => setVerification(await verifyPromotionEvent(selectedEvent.promotion_event_id)))}>
                Verify event
              </button>
              <button disabled={!selectedEvent || loading} className="rounded bg-red-500 px-3 py-2 text-sm font-semibold text-white disabled:bg-slate-700 disabled:text-slate-400" onClick={() => selectedEvent && void runAction(async () => { await rollbackPromotionEvent(selectedEvent.promotion_event_id, "admin rollback from production promotion panel"); await refreshEvents(scopeId); })}>
                Rollback
              </button>
            </div>
          </div>
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-slate-800 text-slate-400"><tr><th className="py-2 pr-4">Artifact</th><th className="py-2 pr-4">Layer</th><th className="py-2 pr-4">CAPS</th><th className="py-2 pr-4">Type</th><th className="py-2 pr-4">Status</th></tr></thead>
            <tbody>
              {eventItems.map((item: Record<string, unknown>, idx) => (
                <tr key={idx} className="border-b border-slate-900">
                  <td className="py-2 pr-4 font-mono text-xs">{String(item.artifact_id)}</td>
                  <td className="py-2 pr-4">{String(item.layer)}</td>
                  <td className="py-2 pr-4">{String(item.caps_ref ?? "-")}</td>
                  <td className="py-2 pr-4">{String(item.artifact_type)}</td>
                  <td className="py-2 pr-4">{String(item.production_status)}</td>
                </tr>
              ))}
              {!eventItems.length && <tr><td colSpan={5} className="py-6 text-center text-slate-500">No promotion items selected.</td></tr>}
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
