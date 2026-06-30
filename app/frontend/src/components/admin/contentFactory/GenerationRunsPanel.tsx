"use client";

import { useMemo, useState } from "react";
import {
  executeGenerationRun,
  executeGenerationTask,
  fetchGenerationExecutionReport,
  fetchGenerationRunTasks,
  planMissingGenerationTasks,
  type GenerationExecutionReport,
  type GenerationExecutionResponse,
  type GenerationPlanResponse,
  type GenerationRun,
  type GenerationTask,
} from "@/lib/api/contentFactory";

type Props = {
  runs: GenerationRun[];
};

export default function GenerationRunsPanel({ runs }: Props) {
  const [selectedRunId, setSelectedRunId] = useState(runs[0]?.run_id ?? "");
  const [tasks, setTasks] = useState<GenerationTask[]>([]);
  const [plan, setPlan] = useState<GenerationPlanResponse | null>(null);
  const [execution, setExecution] = useState<GenerationExecutionResponse | null>(null);
  const [report, setReport] = useState<GenerationExecutionReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const queuedTasks = useMemo(() => tasks.filter((task) => task.status === "queued"), [tasks]);
  const firstQueuedTask = queuedTasks[0];

  async function refresh(runId = selectedRunId) {
    if (!runId) return;
    const [nextTasks, nextReport] = await Promise.all([
      fetchGenerationRunTasks(runId),
      fetchGenerationExecutionReport(runId).catch(() => null),
    ]);
    setTasks(nextTasks);
    if (nextReport) setReport(nextReport);
  }

  async function runAction(action: () => Promise<void>) {
    setLoading(true);
    setError(null);
    try {
      await action();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation action failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Controlled Generation</h2>
          <div className="text-sm text-slate-400">Generation is disabled by default until the server flag is enabled.</div>
        </div>
        <select
          value={selectedRunId}
          onChange={(event) => {
            setSelectedRunId(event.target.value);
            void refresh(event.target.value);
          }}
          className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
        >
          <option value="">Select run</option>
          {runs.map((run) => (
            <option key={run.run_id} value={run.run_id}>{run.scope_id} · {run.status}</option>
          ))}
        </select>
      </div>

      {error && <div className="mb-4 rounded border border-amber-700 bg-amber-950 p-3 text-sm text-amber-100">{error}</div>}

      <div className="mb-4 flex flex-wrap gap-2">
        <button disabled={!selectedRunId || loading} onClick={() => runAction(async () => { const next = await planMissingGenerationTasks(selectedRunId); setPlan(next); await refresh(); })} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-300">Plan tasks</button>
        <button disabled={!selectedRunId || loading} onClick={() => runAction(async () => { const next = await executeGenerationRun(selectedRunId); setExecution(next); await refresh(); })} className="rounded bg-slate-700 px-3 py-2 text-sm font-semibold text-slate-100 disabled:text-slate-400">Execute run</button>
        <button
          disabled={!firstQueuedTask || loading}
          onClick={() =>
            runAction(async () => {
              if (!firstQueuedTask) return;
              const next = await executeGenerationTask(firstQueuedTask.task_id);
              setExecution(next);
              await refresh();
            })
          }
          className="rounded bg-slate-700 px-3 py-2 text-sm font-semibold text-slate-100 disabled:text-slate-400"
        >
          Execute selected task
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Summary title="Missing targets" value={plan?.missing.length ?? 0} detail={`${plan?.created_task_ids.length ?? 0} tasks planned`} />
        <Summary title="Execution" value={execution?.status ?? "idle"} detail={`${execution?.artifact_ids.length ?? 0} artifacts`} />
        <Summary title="Report" value={report?.status ?? "none"} detail={report ? `${report.succeeded}/${report.tasks} tasks, ${report.artifacts} artifacts` : "No report"} />
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-slate-800 text-slate-400">
            <tr><th className="py-2 pr-4">Task</th><th className="py-2 pr-4">Layer</th><th className="py-2 pr-4">CAPS</th><th className="py-2 pr-4">Status</th><th className="py-2 pr-4">Artifacts</th></tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.task_id} className="border-b border-slate-800">
                <td className="py-2 pr-4 font-mono text-xs">{task.task_id.slice(0, 8)}</td>
                <td className="py-2 pr-4">{task.content_layer}</td>
                <td className="py-2 pr-4">{task.caps_ref}</td>
                <td className="py-2 pr-4">{task.status}</td>
                <td className="py-2 pr-4">{task.output_artifact_ids.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!tasks.length && <p className="mt-3 text-sm text-slate-400">Select a run to load planned tasks.</p>}
      </div>
    </section>
  );
}

function Summary({ title, value, detail }: { title: string; value: string | number; detail: string }) {
  return <div className="rounded border border-slate-800 bg-slate-950 p-3"><div className="text-sm text-slate-400">{title}</div><div className="mt-1 font-semibold">{value}</div><div className="mt-1 text-xs text-slate-500">{detail}</div></div>;
}
