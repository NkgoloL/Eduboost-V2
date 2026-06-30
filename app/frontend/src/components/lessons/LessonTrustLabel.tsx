// app/frontend/src/components/lessons/LessonTrustLabel.tsx
//
// L5-11 — EduBoost SA Phase 5
// AI transparency UI: visible lesson trust label on every generated lesson.
//
// Displays:
//   ✅ CAPS-linked
//   ✅/⚠️ Answer-checked
//   ✅ AI-generated (with provider badge)
//   ✅/⬜ Teacher-reviewed
//
// Includes a "Report a content problem" button wired to the review queue
// API (POST /api/v2/lessons/{id}/report).
//
// Usage:
//   <LessonTrustLabel lesson={lesson} />

import React, { useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type ReviewStatus =
  | "ai_generated"
  | "human_reviewed"
  | "approved"
  | "rejected"
  | "retired";

export type SafetyClassification = "safe" | "requires_review" | "rejected";

export interface LessonTrustInfo {
  lesson_id: string;
  caps_ref: string;
  answer_key_verified: boolean;
  safety_classification: SafetyClassification;
  pii_check_passed: boolean;
  review_status: ReviewStatus;
  reviewer_id: string | null;
  provider: string;
  prompt_template_version: string;
  quality_score: number | null;
}

interface LessonTrustLabelProps {
  lesson: LessonTrustInfo;
  /** Called after a report is successfully submitted. */
  onReportSubmitted?: (lessonId: string) => void;
}

// ---------------------------------------------------------------------------
// Report modal
// ---------------------------------------------------------------------------

interface ReportModalProps {
  lessonId: string;
  capsRef: string;
  onClose: () => void;
  onSubmitted: () => void;
}

const REPORT_REASONS = [
  "Incorrect answer or worked example",
  "Not aligned with CAPS curriculum",
  "Inappropriate or unsafe content",
  "Language too difficult for Grade 4",
  "Culturally insensitive content",
  "Personal information included",
  "Other",
] as const;

function ReportModal({ lessonId, capsRef, onClose, onSubmitted }: ReportModalProps) {
  const [selectedReason, setSelectedReason] = useState<string>("");
  const [details, setDetails] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!selectedReason) {
      setError("Please select a reason.");
      return;
    }
    setSubmitting(true);
    setError(null);

    try {
      const res = await fetch(`/api/v2/lessons/${lessonId}/report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reason: selectedReason,
          details: details.trim() || undefined,
          caps_ref: capsRef,
        }),
      });
      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }
      onSubmitted();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not submit report. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      data-testid="report-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="report-modal-title"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0,0,0,0.5)",
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: 8,
          padding: 24,
          maxWidth: 480,
          width: "100%",
          boxShadow: "0 8px 32px rgba(0,0,0,0.18)",
        }}
      >
        <h2 id="report-modal-title" style={{ marginTop: 0, fontSize: 18, fontWeight: 600 }}>
          Report a content problem
        </h2>
        <p style={{ fontSize: 14, color: "#555", marginBottom: 16 }}>
          Your report will be reviewed by an EduBoost educator. Thank you for
          helping keep our lessons accurate and safe.
        </p>

        <label style={{ display: "block", fontWeight: 500, marginBottom: 6, fontSize: 14 }}>
          What is the problem?
        </label>
        <select
          value={selectedReason}
          onChange={(e) => setSelectedReason(e.target.value)}
          style={{
            width: "100%",
            padding: "8px 12px",
            borderRadius: 4,
            border: "1px solid #ccc",
            marginBottom: 12,
            fontSize: 14,
          }}
          aria-label="Select report reason"
        >
          <option value="">— Select a reason —</option>
          {REPORT_REASONS.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>

        <label style={{ display: "block", fontWeight: 500, marginBottom: 6, fontSize: 14 }}>
          Additional details (optional)
        </label>
        <textarea
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          rows={3}
          maxLength={500}
          placeholder="Describe the problem in more detail…"
          style={{
            width: "100%",
            padding: "8px 12px",
            borderRadius: 4,
            border: "1px solid #ccc",
            marginBottom: 16,
            fontSize: 14,
            resize: "vertical",
            boxSizing: "border-box",
          }}
        />

        {error && (
          <p style={{ color: "#c00", fontSize: 13, marginBottom: 12 }}>{error}</p>
        )}

        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button
            data-testid="report-modal-close"
            onClick={onClose}
            disabled={submitting}
            style={{
              padding: "8px 16px",
              borderRadius: 4,
              border: "1px solid #ccc",
              background: "#fff",
              cursor: "pointer",
              fontSize: 14,
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || !selectedReason}
            style={{
              padding: "8px 16px",
              borderRadius: 4,
              border: "none",
              background: submitting || !selectedReason ? "#999" : "#1a56db",
              color: "#fff",
              cursor: submitting || !selectedReason ? "not-allowed" : "pointer",
              fontSize: 14,
            }}
          >
            {submitting ? "Submitting…" : "Submit Report"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Trust pill
// ---------------------------------------------------------------------------

interface TrustPillProps {
  icon: string;
  label: string;
  verified: boolean;
  tooltip?: string;
}

function TrustPill({ icon, label, verified, tooltip }: TrustPillProps) {
  const bg = verified ? "#e6f4ea" : "#fff8e1";
  const color = verified ? "#1e7e34" : "#856404";
  const borderColor = verified ? "#a8d5b0" : "#ffe082";

  return (
    <span
      title={tooltip}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: "2px 8px",
        borderRadius: 12,
        fontSize: 12,
        fontWeight: 500,
        background: bg,
        color,
        border: `1px solid ${borderColor}`,
        whiteSpace: "nowrap",
      }}
    >
      <span aria-hidden="true">{icon}</span>
      {label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function LessonTrustLabel({ lesson, onReportSubmitted }: LessonTrustLabelProps) {
  const [reportOpen, setReportOpen] = useState(false);
  const [reportSubmitted, setReportSubmitted] = useState(false);

  const isTeacherReviewed =
    lesson.review_status === "approved" && lesson.reviewer_id !== null;

  const handleReportSubmitted = () => {
    setReportOpen(false);
    setReportSubmitted(true);
    onReportSubmitted?.(lesson.lesson_id);
  };

  return (
    <>
      <div
        data-testid="lesson-trust-label"
        aria-label="AI lesson trust information"
        style={{
          display: "flex",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 6,
          padding: "8px 12px",
          background: "#f8f9fa",
          borderRadius: 6,
          border: "1px solid #e0e0e0",
          marginBottom: 12,
        }}
      >
        {/* CAPS-linked */}
        <TrustPill
          icon="📚"
          label={`CAPS: ${lesson.caps_ref}`}
          verified={true}
          tooltip="This lesson is aligned to the South African CAPS curriculum."
        />

        {/* Answer-checked */}
        <TrustPill
          icon={lesson.answer_key_verified ? "✅" : "⚠️"}
          label={lesson.answer_key_verified ? "Answer-checked" : "Answer-check pending"}
          verified={lesson.answer_key_verified}
          tooltip={
            lesson.answer_key_verified
              ? "All answers were independently verified by a second AI check."
              : "This lesson's answers are awaiting independent verification."
          }
        />

        {/* AI-generated + provider badge */}
        <TrustPill
          icon="🤖"
          label={`AI-generated (${lesson.provider})`}
          verified={true}
          tooltip={`Generated by ${lesson.provider} using prompt template ${lesson.prompt_template_version}.`}
        />

        {/* Teacher-reviewed */}
        <TrustPill
          icon={isTeacherReviewed ? "👩‍🏫" : "⬜"}
          label={isTeacherReviewed ? "Teacher-reviewed" : "Awaiting teacher review"}
          verified={isTeacherReviewed}
          tooltip={
            isTeacherReviewed
              ? "An EduBoost educator has reviewed and approved this lesson."
              : "This lesson is awaiting review by an EduBoost educator."
          }
        />

        {/* Spacer + Report button */}
        <span style={{ flex: 1 }} />

        {reportSubmitted ? (
          <span style={{ fontSize: 12, color: "#1e7e34" }}>
            ✓ Report submitted — thank you!
          </span>
        ) : (
          <button
            data-testid="lesson-report-btn"
            onClick={() => setReportOpen(true)}
            aria-label="Report a content problem with this lesson"
            style={{
              fontSize: 12,
              color: "#555",
              background: "transparent",
              border: "1px solid #ccc",
              borderRadius: 4,
              padding: "3px 10px",
              cursor: "pointer",
              textDecoration: "none",
            }}
          >
            ⚑ Report a problem
          </button>
        )}
      </div>

      {/* Report modal */}
      {reportOpen && (
        <ReportModal
          lessonId={lesson.lesson_id}
          capsRef={lesson.caps_ref}
          onClose={() => setReportOpen(false)}
          onSubmitted={handleReportSubmitted}
        />
      )}
    </>
  );
}

export default LessonTrustLabel;
