"use client";

import { useState } from "react";

export default function BulkReviewToolbar({ selectedCount, onApprove, onReject, onQuarantine, onAssign }: { selectedCount: number; onApprove: (notes: string) => Promise<void>; onReject: (reason: string) => Promise<void>; onQuarantine: (reason: string) => Promise<void>; onAssign: (reviewerId: string) => Promise<void>; }) {
  const [notes, setNotes] = useState("");
  const [reviewerId, setReviewerId] = useState("");
  const disabled = selectedCount === 0;
  return (
    <div className="flex flex-col gap-3 rounded border border-slate-800 bg-slate-950 p-3 lg:flex-row lg:items-center">
      <div className="text-sm text-slate-300">{selectedCount} selected</div>
      <input className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm" placeholder="Reviewer notes or reason" value={notes} onChange={(event) => setNotes(event.target.value)} />
      <input className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm" placeholder="Reviewer ID" value={reviewerId} onChange={(event) => setReviewerId(event.target.value)} />
      <button disabled={disabled || !notes} className="rounded bg-emerald-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => onApprove(notes)}>Bulk approve</button>
      <button disabled={disabled || !notes} className="rounded bg-red-500 px-3 py-2 text-sm font-semibold text-white disabled:bg-slate-700 disabled:text-slate-400" onClick={() => onReject(notes)}>Reject</button>
      <button disabled={disabled || !notes} className="rounded bg-amber-400 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => onQuarantine(notes)}>Quarantine</button>
      <button disabled={disabled || !reviewerId} className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:bg-slate-700 disabled:text-slate-400" onClick={() => onAssign(reviewerId)}>Assign</button>
    </div>
  );
}
