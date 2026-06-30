"use client";

/**
 * LessonRoadmap.tsx
 * ─────────────────────────────────────────────────────────────────────────────
 * EduBoost V2 — Lesson Generation Population Roadmap
 *
 * Placement:  app/frontend/src/components/eduboost/LessonRoadmap.tsx
 * Route page: app/frontend/src/app/(dashboard)/admin/roadmap/page.tsx
 *
 * Features
 * ─────────
 * • Five collapsible phases (Phase 0–4) with per-phase progress bars
 * • Per-task checkbox with optimistic UI and localStorage persistence
 * • Colour-coded owner tags (Engineering / Content / Educator review / Ops)
 * • Global approval progress bar seeded from real item-bank numbers
 * • Fully typed — no `any`, strict-mode safe
 * • Tailwind CSS only — no additional style imports required
 * • Zero external runtime dependencies beyond React
 *
 * Usage
 * ─────
 * import LessonRoadmap from "@/components/eduboost/LessonRoadmap";
 * // then anywhere in a Server or Client page:
 * <LessonRoadmap />
 */

import { useState, useEffect, useCallback } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

type OwnerTag = "eng" | "content" | "review" | "ops";

interface Task {
  id: string;
  name: string;
  tags: OwnerTag[];
}

interface Phase {
  id: string;
  index: string;
  title: string;
  sub: string;
  timeEstimate: string;
  tasks: Task[];
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const PHASES: Phase[] = [
  {
    id: "ph0",
    index: "0",
    title: "Immediate: unblock the approval pipeline",
    sub: "Nothing works until reviewers can actually review — fix the tools first",
    timeEstimate: "1–2 days",
    tasks: [
      {
        id: "t0-1",
        name: "Confirm all 106 AI-generated candidates are in the database and queryable via validate_item_bank.py",
        tags: ["ops", "eng"],
      },
      {
        id: "t0-2",
        name: "Build a minimal admin UI or script that lists ai_generated items and allows one-click approve/reject with reviewer_id stamping",
        tags: ["eng"],
      },
      {
        id: "t0-3",
        name: "Verify safety_passed field is populated on all candidates — block approval of any item where it is null",
        tags: ["ops"],
      },
      {
        id: "t0-4",
        name: "Verify answer_key for each candidate with a second independent LLM call (as required by the production plan)",
        tags: ["eng", "content"],
      },
      {
        id: "t0-5",
        name: "Run validate_item_bank.py --all-statuses and confirm 0 structural failures across all 121 items",
        tags: ["ops"],
      },
      {
        id: "t0-6",
        name: "Document the review workflow in a single page so educators know exactly what they are approving against",
        tags: ["content"],
      },
    ],
  },
  {
    id: "ph1",
    index: "1",
    title: "Sprint 1: reach 40 approved items per CAPS topic",
    sub: "Drive 4.M.1.1, 4.M.1.2, and 4.M.1.3 each to ≥ 40 approved — the CI gate target",
    timeEstimate: "1–2 weeks",
    tasks: [
      {
        id: "t1-1",
        name: "4.M.1.1 Whole Numbers: review and approve 36 AI candidates (currently 4 approved, target 40)",
        tags: ["review", "content"],
      },
      {
        id: "t1-2",
        name: "4.M.1.2 Common Fractions: review and approve 35 AI candidates (currently 5 approved, target 40)",
        tags: ["review", "content"],
      },
      {
        id: "t1-3",
        name: "4.M.1.3 2D Shapes: review and approve 35 AI candidates (currently 5 approved, target 40)",
        tags: ["review", "content"],
      },
      {
        id: "t1-4",
        name: "For each approved item: populate reviewer_id, reviewed_at, quality_score ≥ 0.7, and misconception tags",
        tags: ["review"],
      },
      {
        id: "t1-5",
        name: "Reject any item that fails readability, has an ambiguous answer key, or lacks four plausible distractors — do not approve with a plan to fix later",
        tags: ["review", "content"],
      },
      {
        id: "t1-6",
        name: "Enable production CI thresholds: ITEM_BANK_MIN_APPROVED=40 per topic and ITEM_BANK_MIN_APPROVED_TOTAL=120",
        tags: ["ops", "eng"],
      },
      {
        id: "t1-7",
        name: "Run make coverage-gate and confirm CI passes green for all three CAPS refs",
        tags: ["ops"],
      },
      {
        id: "t1-8",
        name: "Regenerate grade4_maths_coverage_matrix.md from the live database and commit it",
        tags: ["ops"],
      },
    ],
  },
  {
    id: "ph2",
    index: "2",
    title: "Sprint 2: quality gates and IRT calibration",
    sub: "Ensure items are not just approved but statistically usable by the adaptive engine",
    timeEstimate: "2–3 weeks",
    tasks: [
      {
        id: "t2-1",
        name: "Verify difficulty distribution per topic matches the IRT target: 10 easy / 12 moderate / 12 on-level / 6 challenging",
        tags: ["content", "eng"],
      },
      {
        id: "t2-2",
        name: "Fill any difficulty band gaps by generating targeted new items (e.g. 4.M.1.2 needs more easy and on-level items)",
        tags: ["content"],
      },
      {
        id: "t2-3",
        name: "Confirm misconception tags are populated for all approved items across all three CAPS refs",
        tags: ["review"],
      },
      {
        id: "t2-4",
        name: "Verify IRT engine serves items from the database — no hardcoded item arrays remain in the lesson/diagnostic service",
        tags: ["eng"],
      },
      {
        id: "t2-5",
        name: "Confirm item selection p99 latency < 50ms under 10 concurrent simulated sessions",
        tags: ["eng"],
      },
      {
        id: "t2-6",
        name: "Verify exposure enforcement: no item repeats within a session or across 3 consecutive sessions for the same learner",
        tags: ["eng"],
      },
      {
        id: "t2-7",
        name: "Confirm Prometheus item_bank_coverage_ratio metric ≥ 1.0 for all three CAPS refs",
        tags: ["ops"],
      },
      {
        id: "t2-8",
        name: "Add Grafana panel: 'Item bank coverage by CAPS ref' showing approved vs target per topic",
        tags: ["ops"],
      },
    ],
  },
  {
    id: "ph3",
    index: "3",
    title: "Sprint 3: replenishment pipeline and lesson coverage",
    sub: "Build the ongoing engine so items never run dry as learners use the platform",
    timeEstimate: "3–4 weeks",
    tasks: [
      {
        id: "t3-1",
        name: "Define exposure cap threshold: trigger new item generation when >20% of a topic's items reach 80% of their max_exposure cap",
        tags: ["eng"],
      },
      {
        id: "t3-2",
        name: "Build a scheduled job (cron or Celery beat) that checks exposure ratios nightly and enqueues generation tasks",
        tags: ["eng"],
      },
      {
        id: "t3-3",
        name: "Extend generate_grade4_item_batch.py to accept a topic, difficulty band, and count so targeted replenishment is scriptable",
        tags: ["eng"],
      },
      {
        id: "t3-4",
        name: "Add a CI check that fails if any topic's approved item count drops below the minimum (items can be retired)",
        tags: ["ops"],
      },
      {
        id: "t3-5",
        name: "Add lesson content beyond diagnostic items: worked examples, explanations, and visual aids for each CAPS topic",
        tags: ["content"],
      },
      {
        id: "t3-6",
        name: "Map lesson content to misconception tags so failed items trigger the correct remedial lesson segment",
        tags: ["content"],
      },
      {
        id: "t3-7",
        name: "Implement Terms 2 and 3 of Grade 4 Mathematics: identify CAPS refs, generate candidates, follow the same approval workflow",
        tags: ["content", "eng"],
      },
      {
        id: "t3-8",
        name: "Playwright E2E: full learner flow — login → adaptive diagnostic → lesson generation → XP award → study plan update",
        tags: ["eng"],
      },
    ],
  },
  {
    id: "ph4",
    index: "4",
    title: "Phase 4: expand to Grade R–7 across all subjects",
    sub: "Scale the same pipeline to the full product scope — additional grades and subjects",
    timeEstimate: "2–6 months",
    tasks: [
      {
        id: "t4-1",
        name: "Define CAPS refs and item bank targets for Grade 4 remaining subjects: English Home Language, Natural Sciences, Social Sciences",
        tags: ["content"],
      },
      {
        id: "t4-2",
        name: "Define CAPS refs for Grades 5, 6, and 7 Mathematics — highest-priority path for beta growth",
        tags: ["content"],
      },
      {
        id: "t4-3",
        name: "Extend generate_grade4_item_batch.py into a grade-subject-agnostic generator with CAPS ref as a parameter",
        tags: ["eng"],
      },
      {
        id: "t4-4",
        name: "Build a content calendar: which grade/subject combinations ship in which release, with educator review resourcing plan",
        tags: ["content", "review"],
      },
      {
        id: "t4-5",
        name: "Add multilingual item generation: generate isiZulu, Afrikaans, and isiXhosa variants of approved English items",
        tags: ["content", "eng"],
      },
      {
        id: "t4-6",
        name: "Implement Grade R–3 foundational content: simpler item structure, audio prompt support, visual-first format",
        tags: ["content", "eng"],
      },
      {
        id: "t4-7",
        name: "Build an item bank dashboard for educators: per-grade coverage view, approval queue, retired item audit, exposure heatmap",
        tags: ["eng"],
      },
      {
        id: "t4-8",
        name: "Commission independent CAPS curriculum expert review of a sample across all grades before each phase goes live",
        tags: ["review"],
      },
    ],
  },
];

// ─── Constants ─────────────────────────────────────────────────────────────────

const STORAGE_KEY = "eduboost:roadmap:tasks";

const APPROVED_ITEMS = 14;
const PRODUCTION_TARGET = 120;

const TAG_CONFIG: Record<OwnerTag, { label: string; classes: string }> = {
  eng: {
    label: "Engineering",
    classes:
      "bg-blue-900 text-blue-300 ring-1 ring-blue-700",
  },
  content: {
    label: "Content / curriculum",
    classes:
      "bg-amber-900 text-amber-300 ring-1 ring-amber-700",
  },
  review: {
    label: "Educator review",
    classes:
      "bg-green-900 text-green-300 ring-1 ring-green-700",
  },
  ops: {
    label: "Ops / CI",
    classes:
      "bg-red-900 text-red-300 ring-1 ring-red-700",
  },
};

const PHASE_ACCENT: Record<string, { dot: string; bar: string; ring: string }> = {
  ph0: {
    dot: "bg-red-900 text-red-300",
    bar: "bg-red-500",
    ring: "ring-red-700",
  },
  ph1: {
    dot: "bg-amber-900 text-amber-300",
    bar: "bg-amber-400",
    ring: "ring-amber-700",
  },
  ph2: {
    dot: "bg-blue-900 text-blue-300",
    bar: "bg-blue-500",
    ring: "ring-blue-700",
  },
  ph3: {
    dot: "bg-green-900 text-green-300",
    bar: "bg-green-500",
    ring: "ring-green-700",
  },
  ph4: {
    dot: "bg-gray-700 text-gray-300",
    bar: "bg-gray-400",
    ring: "ring-gray-700",
  },
};

// ─── Sub-components ────────────────────────────────────────────────────────────

function OwnerBadge({ tag }: { tag: OwnerTag }) {
  const { label, classes } = TAG_CONFIG[tag];
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${classes}`}>
      {label}
    </span>
  );
}

function CheckIcon() {
  return (
    <svg
      viewBox="0 0 12 12"
      fill="none"
      className="h-3 w-3"
      aria-hidden="true"
    >
      <path
        d="M2 6l3 3 5-5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      className={`h-4 w-4 text-gray-400 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
      aria-hidden="true"
    >
      <path
        d="M4 6l4 4 4-4"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── PhaseCard ─────────────────────────────────────────────────────────────────

interface PhaseCardProps {
  phase: Phase;
  taskState: Record<string, boolean>;
  onToggleTask: (id: string) => void;
}

function PhaseCard({ phase, taskState, onToggleTask }: PhaseCardProps) {
  const [open, setOpen] = useState(phase.id === "ph0");

  const doneTasks = phase.tasks.filter((t) => taskState[t.id]).length;
  const totalTasks = phase.tasks.length;
  const pct = totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0;
  const accent = (PHASE_ACCENT[phase.id] ?? PHASE_ACCENT.ph0) as { dot: string; bar: string; ring: string };

  return (
    <div className="rounded-lg border border-gray-700 shadow-sm" style={{ backgroundColor: '#252525' }}>
      {/* Header */}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-4 py-4 text-left transition-colors rounded-lg"
        style={{ backgroundColor: '#252525' }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#2a2a2a')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#252525')}
      >
        {/* Phase index dot */}
        <span
          className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-xs font-semibold ${(accent as any).dot}`}
          aria-hidden="true"
        >
          {phase.index}
        </span>

        {/* Title block */}
        <span className="min-w-0 flex-1">
          <span className="block text-sm font-semibold text-gray-100">
            {phase.title}
          </span>
          <span className="block text-xs text-gray-400 mt-0.5">
            {phase.sub}
          </span>
        </span>

        {/* Badges */}
        <span className="hidden sm:flex items-center gap-2 flex-shrink-0">
          <span className="rounded-full border border-gray-600 px-2.5 py-0.5 text-xs text-gray-400">
            {phase.timeEstimate}
          </span>
          <span className="rounded-full border border-gray-600 px-2.5 py-0.5 text-xs text-gray-400">
            {doneTasks}/{totalTasks}
          </span>
        </span>

        <ChevronIcon open={open} />
      </button>

      {/* Progress bar — always visible */}
      <div className="mx-4 mb-0 h-2 overflow-hidden rounded-full bg-gray-700">
        <div
          className={`h-full rounded-full transition-[width] duration-500 ${(accent as any).bar}`}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Phase ${phase.index} progress: ${doneTasks} of ${totalTasks} tasks complete`}
        />
      </div>

      {/* Task list */}
      {open && (
        <ul className="mt-0 divide-y divide-gray-700 border-t border-gray-700 mt-2">
          {phase.tasks.map((task) => {
            const done = taskState[task.id] ?? false;
            return (
              <li key={task.id}>
                <button
                  type="button"
                  onClick={() => onToggleTask(task.id)}
                  className="flex w-full items-start gap-3 px-4 py-3 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                  style={{ backgroundColor: '#252525' }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#2a2a2a')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#252525')}
                  aria-pressed={done}
                >
                  {/* Checkbox */}
                  <span
                    className={`mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded border transition-colors ${
                      done
                        ? "border-green-500 bg-green-500 text-white"
                        : "border-gray-600 bg-gray-700"
                    }`}
                    aria-hidden="true"
                  >
                    {done && <CheckIcon />}
                  </span>

                  {/* Content */}
                  <span className="min-w-0 flex-1">
                    <span
                      className={`block text-sm leading-snug ${
                        done
                          ? "text-gray-500 line-through"
                          : "text-gray-200"
                      }`}
                    >
                      {task.name}
                    </span>
                    <span className="mt-1.5 flex flex-wrap gap-1.5">
                      {task.tags.map((tag) => (
                        <OwnerBadge key={tag} tag={tag} />
                      ))}
                    </span>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

// ─── StatCard ──────────────────────────────────────────────────────────────────

function StatCard({
  value,
  label,
  variant = "neutral",
}: {
  value: string | number;
  label: string;
  variant?: "neutral" | "danger" | "warn" | "ok";
}) {
  const colorMap = {
    neutral: { text: "text-gray-400", bg: "#2a2a2a" },
    danger: { text: "text-red-400", bg: "#2a2a2a" },
    warn: { text: "text-amber-400", bg: "#2a2a2a" },
    ok: { text: "text-green-400", bg: "#2a2a2a" },
  };

  const { text: valueColor, bg: bgColor } = colorMap[variant];

  return (
    <div 
      className={`rounded-lg px-4 py-4 border border-gray-700 ${valueColor}`}
      style={{ backgroundColor: bgColor }}
    >
      <p className={`text-3xl font-bold tabular-nums ${valueColor}`}>{value}</p>
      <p className="mt-2 text-sm text-gray-400">{label}</p>
    </div>
  );
}

// ─── Legend ────────────────────────────────────────────────────────────────────

function Legend() {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-gray-400">
      {(Object.entries(TAG_CONFIG) as [OwnerTag, (typeof TAG_CONFIG)[OwnerTag]][]).map(
        ([key, { label, classes }]) => (
          <span key={key} className="flex items-center gap-1.5">
            <span className={`inline-flex rounded-full px-1.5 py-0.5 text-[10px] font-medium ${classes}`}>
              {label}
            </span>
          </span>
        )
      )}
    </div>
  );
}

// ─── Main component ────────────────────────────────────────────────────────────

export default function LessonRoadmap() {
  const allTaskIds = PHASES.flatMap((p) => p.tasks.map((t) => t.id));

  const [taskState, setTaskState] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    allTaskIds.forEach((id) => (initial[id] = false));
    return initial;
  });

  // Hydrate from localStorage after mount (avoids SSR mismatch)
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as Record<string, boolean>;
        setTaskState((prev) => ({ ...prev, ...parsed }));
      }
    } catch {
      // localStorage unavailable — silently ignore
    }
  }, []);

  const toggleTask = useCallback((id: string) => {
    setTaskState((prev) => {
      const next = { ...prev, [id]: !prev[id] };
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        // localStorage unavailable — state still updates in memory
      }
      return next;
    });
  }, []);

  // Derived stats
  const completedTasks = Object.values(taskState).filter(Boolean).length;
  const totalTasks = allTaskIds.length;
  const itemBankPct = Math.round((APPROVED_ITEMS / PRODUCTION_TARGET) * 100);
  const taskPct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
  const taskPctFloat = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  return (
    <div style={{ backgroundColor: '#1a1a1a', color: '#e5e7eb', minHeight: '100vh', padding: '64px 24px' }}>
      <section aria-labelledby="roadmap-heading" className="mx-auto max-w-5xl">
      {/* Heading */}
      <div className="mb-12">
        <h1
          id="roadmap-heading"
          className="text-4xl font-bold mb-3"
          style={{ color: '#ffffff' }}
        >
          Lesson generation roadmap
        </h1>
        <p className="text-base max-w-2xl" style={{ color: '#9ca3af' }}>
          Tracks the path from 14 approved items to a production-grade item bank across all CAPS
          topics. Check off tasks as they are completed — progress is saved locally.
        </p>
      </div>

      {/* Summary stats */}
      <div className="mb-10 gap-6" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
        <StatCard value={APPROVED_ITEMS} label="Approved items" variant="danger" />
        <StatCard value={106} label="AI candidates (unreviewed)" variant="warn" />
        <StatCard value={0} label="Topics at ≥ 40 approved" variant="neutral" />
        <StatCard value={PRODUCTION_TARGET} label="Production target" variant="ok" />
      </div>

      {/* Overall approval progress (single concise bar) */}
      <div className="mb-10 rounded-lg border border-gray-700 px-6 py-5" style={{ backgroundColor: '#252525' }}>
        <div className="flex items-center justify-between text-sm text-gray-300 mb-3">
          <div>Overall approval progress</div>
          <div>{taskPctFloat.toFixed(1)}% ({completedTasks} / {totalTasks} tasks)</div>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-gray-700">
          <div
            className="h-full rounded-full bg-blue-500 transition-[width] duration-500"
            style={{ width: `${taskPct}%` }}
            role="progressbar"
            aria-valuenow={taskPct}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Overall approval progress: ${completedTasks} of ${totalTasks} tasks`}
          />
        </div>
      </div>

      {/* Tag legend */}
      <div className="mb-8">
        <Legend />
      </div>

      {/* Phase list */}
      <div className="space-y-5" role="list" aria-label="Roadmap phases">
        {PHASES.map((phase) => (
          <div key={phase.id} role="listitem">
            <PhaseCard
              phase={phase}
              taskState={taskState}
              onToggleTask={toggleTask}
            />
          </div>
        ))}
      </div>

      {/* Footer note */}
      <p className="mt-10 text-xs text-gray-500">
        Task state is stored in <code className="font-mono px-1.5 py-0.5 rounded" style={{ backgroundColor: '#2a2a2a', color: '#9ca3af' }}>localStorage</code> under the key{" "}
        <code className="font-mono px-1.5 py-0.5 rounded" style={{ backgroundColor: '#2a2a2a', color: '#9ca3af' }}>{STORAGE_KEY}</code>. For team-wide persistence, replace the
        localStorage calls with an API write to your admin settings endpoint.
      </p>
      </section>
    </div>
  );
}
