import { useEffect, useState } from "react";
import {
  planFullGeneration,
  startFullGeneration,
  listFullGenerationRuns,
  getFullGenerationRun,
  cancelFullGenerationRun,
  resumeFullGenerationRun,
  type FullGenerationPlanResponse,
  type FullGenerationRunsResponse,
  type GenerationRun,
} from "@/lib/api/contentFactory";

interface Props {
  scopes: Array<{ scope_id: string }>;
}

export default function FullGenerationPanel({ scopes }: Props) {
  const [plan, setPlan] = useState<FullGenerationPlanResponse | null>(null);
  const [runs, setRuns] = useState<GenerationRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<GenerationRun | null>(null);
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const expectedConfirmation = "GENERATE OUTSTANDING CONTENT FOR ALL CONFIGURED SCOPES";

  async function refreshRuns() {
    setLoading(true);
    setMessage(null);
    try {
      const page = await listFullGenerationRuns();
      setRuns(page.items);
      if (page.items[0]) {
        setSelectedRun(page.items[0]);
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to fetch runs");
    } finally {
      setLoading(false);
    }
  }

  async function runAction(action: () => Promise<void>) {
    setLoading(true);
    setMessage(null);
    try {
      await action();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Full generation action failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshRuns();
  }, []);

  return (
    <section className="rounded border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Full Generation</h2>
          <div className="text-sm text-slate-400">Overnight-safe batch generation for all scopes</div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            disabled={loading}
            className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400"
            onClick={() => void runAction(async () => setPlan(await planFullGeneration()))}
          >
            Plan full generation
          </button>
          <button
            disabled={!plan || loading}
            className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400"
            onClick={() => void runAction(async () => {
              if (!plan) return;
              await startFullGeneration(plan.run_id, confirmation);
              setConfirmation("");
              await refreshRuns();
            })}
          >
            Start full generation
          </button>
        </div>
      </div>

      {message && <div className="mb-4 rounded border border-amber-700 bg-amber-950 p-3 text-sm text-amber-100">{message}</div>}

      {plan && (
        <div className="mb-4 rounded border border-slate-800 bg-slate-950 p-3">
          <h3 className="mb-2 text-sm font-semibold text-slate-300">Plan Result</h3>
          <div className="grid gap-2 text-sm text-slate-400">
            <div>Run ID: {plan.run_id}</div>
            <div>Tasks to create: {plan.created_task_ids.length}</div>
            <div>Skipped targets: {plan.skipped.length}</div>
            <div>Missing content: {plan.missing.length}</div>
          </div>
        </div>
      )}

      <div className="mb-4 rounded border border-slate-800 bg-slate-950 p-3">
        <h3 className="mb-3 text-sm font-semibold text-slate-300">Start Full Generation</h3>
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
          disabled={!plan || confirmation !== expectedConfirmation || loading}
          className="rounded bg-emerald-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400"
          onClick={() => {
            if (!plan) return;
            void runAction(async () => {
              await startFullGeneration(plan.run_id, confirmation);
              setConfirmation("");
              await refreshRuns();
            });
          }}
        >
          Start generation
        </button>
      </div>

      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <div className="rounded border border-slate-800 bg-slate-950 p-3">
          <h3 className="mb-3 text-sm font-semibold text-slate-300">Generation runs</h3>
          <div className="space-y-2">
            {runs.map((run) => (
              <button
                key={run.run_id}
                className={`w-full rounded border px-3 py-2 text-left text-sm ${selectedRun?.run_id === run.run_id ? "border-cyan-500 bg-slate-900" : "border-slate-800 bg-slate-950"}`}
                onClick={() => setSelectedRun(run)}
              >
                <div className="truncate">{run.run_id}</div>
                <div className="mt-1 text-slate-400">{run.status}</div>
              </button>
            ))}
            {!runs.length && <div className="text-sm text-slate-500">No generation runs yet.</div>}
          </div>
        </div>

        <div className="rounded border border-slate-800 bg-slate-950 p-3">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-300">Run details</h3>
            <div className="flex gap-2">
              <button
                disabled={!selectedRun || loading}
                className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400"
                onClick={() => void runAction(async () => {
                  if (selectedRun) {
                    await cancelFullGenerationRun(selectedRun.run_id);
                    await refreshRuns();
                  }
                })}
              >
                Cancel
              </button>
              <button
                disabled={!selectedRun || loading}
                className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400"
                onClick={() => void runAction(async () => {
                  if (selectedRun) {
                    await resumeFullGenerationRun(selectedRun.run_id);
                    await refreshRuns();
                  }
                })}
              >
                Resume
              </button>
            </div>
          </div>
          {selectedRun ? (
            <div className="space-y-2 text-sm text-slate-400">
              <div>Run ID: {selectedRun.run_id}</div>
              <div>Scope: {selectedRun.scope_id}</div>
              <div>Status: {selectedRun.status}</div>
              <div>Requested by: {selectedRun.requested_by || "N/A"}</div>
            </div>
          ) : (
            <div className="text-sm text-slate-500">No run selected.</div>
          )}
        </div>
      </div>
    </section>
  );
}
