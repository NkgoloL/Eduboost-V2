"use client";

/**
 * Privacy & Data Controls — EduBoost SA V2
 *
 * Place at:
 *   app/frontend/src/app/settings/privacy/page.tsx
 *
 * Covers:
 *   - Toggle switches: analytics, AI improvement, marketing, leaderboard
 *   - Data retention selector (90d / 1yr / 2yr / unlimited)
 *   - POPIA right-of-access: request data export
 *   - POPIA right-to-erasure: request account deletion (with confirm modal)
 */

import { useState, useEffect } from "react";

type ApiDetail = { detail?: string };

interface PrivacyState {
  analytics_enabled:     boolean;
  ai_improvement:        boolean;
  marketing_emails:      boolean;
  data_retention_days:   number;
  show_leaderboard:      boolean;
  export_requested_at:   string | null;
  deletion_requested_at: string | null;
}

const RETENTION_OPTIONS = [
  { label: "90 days",   value: 90 },
  { label: "1 year",    value: 365 },
  { label: "2 years",   value: 730 },
  { label: "Unlimited", value: 0 },
];

export default function PrivacySettingsPage() {
  const [settings,      setSettings]      = useState<PrivacyState | null>(null);
  const [saving,        setSaving]         = useState(false);
  const [saved,         setSaved]          = useState(false);
  const [error,         setError]          = useState<string | null>(null);
  const [exportLoading, setExportLoading]  = useState(false);
  const [deleteLoading, setDeleteLoading]  = useState(false);
  const [deleteConfirm, setDeleteConfirm]  = useState(false);

  useEffect(() => {
    fetch("/api/v2/auth/privacy", { credentials: "include" })
      .then(r => r.json())
      .then(setSettings)
      .catch(() => setError("Could not load privacy settings."));
  }, []);

  // ── Save preferences ──────────────────────────────────────────────────────
  async function save() {
    if (!settings) return;
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const res = await fetch("/api/v2/auth/privacy", {
        method:      "PATCH",
        credentials: "include",
        headers:     { "Content-Type": "application/json" },
        body: JSON.stringify({
          analytics_enabled:   settings.analytics_enabled,
          ai_improvement:      settings.ai_improvement,
          marketing_emails:    settings.marketing_emails,
          data_retention_days: settings.data_retention_days,
          show_leaderboard:    settings.show_leaderboard,
        }),
      });
      if (!res.ok) {
        const data: ApiDetail = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? "Save failed.");
      }
      const updated = await res.json();
      setSettings(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed.");
    } finally {
      setSaving(false);
    }
  }

  // ── Request data export ───────────────────────────────────────────────────
  async function requestExport() {
    setExportLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v2/auth/privacy/request-export", {
        method: "POST", credentials: "include",
      });
      if (!res.ok) {
        const data: ApiDetail = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Export request failed");
      }
      setSettings(prev =>
        prev ? { ...prev, export_requested_at: new Date().toISOString() } : prev
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export request failed");
    } finally {
      setExportLoading(false);
    }
  }

  // ── Request account deletion ──────────────────────────────────────────────
  async function requestDeletion() {
    setDeleteLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v2/auth/privacy/request-deletion", {
        method: "POST", credentials: "include",
      });
      if (!res.ok) {
        const data: ApiDetail = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Deletion request failed");
      }
      setSettings(prev =>
        prev ? { ...prev, deletion_requested_at: new Date().toISOString() } : prev
      );
      setDeleteConfirm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Deletion request failed");
    } finally {
      setDeleteLoading(false);
    }
  }

  function toggle(key: keyof PrivacyState) {
    setSettings(prev => prev ? { ...prev, [key]: !(prev[key] as boolean) } : prev);
  }

  // Loading spinner
  if (!settings) {
    return (
      <div style={s.page}>
        <div style={s.spinnerWrap}><div style={s.spinner} /></div>
      </div>
    );
  }

  return (
    <div style={s.page}>
      <div style={s.container}>

        {/* ── Page header ──────────────────────────────────────────── */}
        <div style={s.header}>
          <h1 style={s.pageTitle}>🔒 Privacy & Data Controls</h1>
          <p style={s.pageSubtitle}>
            EduBoost SA is POPIA-compliant. You control how your data is used.
          </p>
        </div>

        {error && <div style={s.errorBox}>{error}</div>}

        {/* ── Data Usage ───────────────────────────────────────────── */}
        <Section title="Data usage" icon="📊">
          <Toggle
            label="Performance analytics"
            description="Allow anonymised learning analytics to be shared with teachers and parents."
            checked={settings.analytics_enabled}
            onChange={() => toggle("analytics_enabled")}
            testId="toggle-analytics"
          />
          <Toggle
            label="AI improvement"
            description="Contribute anonymised interaction data to improve EduBoost AI lesson quality."
            checked={settings.ai_improvement}
            onChange={() => toggle("ai_improvement")}
            testId="toggle-ai-improvement"
          />
          <Toggle
            label="Marketing emails"
            description="Receive news, tips, and product updates from EduBoost SA."
            checked={settings.marketing_emails}
            onChange={() => toggle("marketing_emails")}
            testId="toggle-marketing"
          />
          <Toggle
            label="Show on leaderboard"
            description="Allow the learner&apos;s name to appear on the classroom leaderboard."
            checked={settings.show_leaderboard}
            onChange={() => toggle("show_leaderboard")}
            testId="toggle-leaderboard"
          />
        </Section>

        {/* ── Data Retention ───────────────────────────────────────── */}
        <Section title="Data retention" icon="🗂️">
          <p style={s.sectionNote}>
            Choose how long EduBoost SA keeps the learner&apos;s activity data.
            After this period, data is automatically deleted.
          </p>
          <div style={s.retentionGrid}>
            {RETENTION_OPTIONS.map(opt => (
              <button
                key={opt.value}
                data-testid={`retention-${opt.value}`}
                style={{
                  ...s.retentionBtn,
                  ...(settings.data_retention_days === opt.value ? s.retentionBtnActive : {}),
                }}
                onClick={() =>
                  setSettings(prev =>
                    prev ? { ...prev, data_retention_days: opt.value } : prev
                  )
                }
              >
                {opt.label}
              </button>
            ))}
          </div>
        </Section>

        {/* ── Save button ──────────────────────────────────────────── */}
        <div style={s.saveRow}>
          {saved && <span style={s.savedTag}>✅ Saved</span>}
          <button
            style={s.saveBtn}
            disabled={saving}
            onClick={save}
            data-testid="save-privacy-btn"
          >
            {saving ? "Saving…" : "Save preferences"}
          </button>
        </div>

        {/* ── POPIA Rights ─────────────────────────────────────────── */}
        <Section title="Your POPIA rights" icon="⚖️">
          <p style={s.sectionNote}>
            Under the Protection of Personal Information Act (POPIA), you have the right
            to access your data and request its deletion.
          </p>

          {/* Right to access */}
          <div style={s.rightCard}>
            <div style={{ flex: 1 }}>
              <strong style={s.rightTitle}>Right to access your data</strong>
              <p style={s.rightDesc}>
                Request a full export of all data EduBoost SA holds about you.
              </p>
              {settings.export_requested_at && (
                <p style={s.requestedTag}>
                  ✅ Requested on{" "}
                  {new Date(settings.export_requested_at).toLocaleDateString("en-ZA")}
                </p>
              )}
            </div>
            <button
              style={s.rightBtn}
              disabled={exportLoading || !!settings.export_requested_at}
              onClick={requestExport}
              data-testid="request-export-btn"
            >
              {exportLoading
                ? "Requesting…"
                : settings.export_requested_at
                ? "Requested"
                : "Request export"}
            </button>
          </div>

          {/* Right to erasure */}
          <div style={{ ...s.rightCard, borderColor: "#fca5a5" }}>
            <div style={{ flex: 1 }}>
              <strong style={{ ...s.rightTitle, color: "#dc2626" }}>
                Right to erasure
              </strong>
              <p style={s.rightDesc}>
                Permanently delete your account and all associated data. This cannot be undone.
              </p>
              {settings.deletion_requested_at && (
                <p style={{ ...s.requestedTag, color: "#dc2626" }}>
                  ⚠️ Deletion requested on{" "}
                  {new Date(settings.deletion_requested_at).toLocaleDateString("en-ZA")}
                </p>
              )}
            </div>
            {!settings.deletion_requested_at && (
              <button
                style={{
                  ...s.rightBtn,
                  background: "#fee2e2",
                  color: "#dc2626",
                  border: "1.5px solid #fca5a5",
                }}
                onClick={() => setDeleteConfirm(true)}
                data-testid="request-deletion-btn"
              >
                Request deletion
              </button>
            )}
          </div>
        </Section>

        {/* ── Delete confirm modal ─────────────────────────────────── */}
        {deleteConfirm && (
          <div style={s.modalBackdrop}>
            <div style={s.modal} data-testid="delete-confirm-modal">
              <h3 style={{ color: "#dc2626", marginTop: 0 }}>⚠️ Are you absolutely sure?</h3>
              <p style={{ color: "#374151", fontSize: 14, lineHeight: 1.7 }}>
                This will schedule your account and all learner data for permanent deletion
                within 30 days. This action <strong>cannot be undone</strong>.
              </p>
              <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
                <button
                  style={{ ...s.saveBtn, background: "#dc2626", flex: 1 }}
                  disabled={deleteLoading}
                  onClick={requestDeletion}
                  data-testid="confirm-delete-btn"
                >
                  {deleteLoading ? "Processing…" : "Yes, delete my account"}
                </button>
                <button
                  style={{ ...s.saveBtn, background: "#6b7280", flex: 1 }}
                  onClick={() => setDeleteConfirm(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

function Section({
  title, icon, children,
}: {
  title: string; icon: string; children: React.ReactNode;
}) {
  return (
    <div style={s.section}>
      <h2 style={s.sectionTitle}>{icon} {title}</h2>
      {children}
    </div>
  );
}

function Toggle({
  label, description, checked, onChange, testId,
}: {
  label: string; description: string; checked: boolean;
  onChange: () => void; testId: string;
}) {
  return (
    <div style={s.toggleRow}>
      <div style={{ flex: 1 }}>
        <div style={s.toggleLabel}>{label}</div>
        <div style={s.toggleDesc}>{description}</div>
      </div>
      <button
        data-testid={testId}
        style={{ ...s.toggleSwitch, background: checked ? "#0d6e4c" : "#d1d5db" }}
        onClick={onChange}
        role="switch"
        aria-checked={checked}
      >
        <span
          style={{
            ...s.toggleThumb,
            transform: checked ? "translateX(20px)" : "translateX(0)",
          }}
        />
      </button>
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const s: Record<string, React.CSSProperties> = {
  page:              { minHeight: "100vh", background: "#f0f4f8", padding: "40px 16px", fontFamily: "'Segoe UI', Arial, sans-serif" },
  container:         { maxWidth: 680, margin: "0 auto" },
  header:            { marginBottom: 28 },
  pageTitle:         { fontSize: 26, fontWeight: 700, color: "#111827", margin: "0 0 8px" },
  pageSubtitle:      { fontSize: 14, color: "#6b7280", margin: 0 },
  section:           { background: "#fff", borderRadius: 16, padding: "28px 32px", marginBottom: 20, boxShadow: "0 2px 12px rgba(0,0,0,.06)" },
  sectionTitle:      { fontSize: 16, fontWeight: 700, color: "#1a3c5e", margin: "0 0 20px" },
  sectionNote:       { fontSize: 13, color: "#6b7280", lineHeight: 1.7, margin: "0 0 16px" },
  toggleRow:         { display: "flex", alignItems: "center", gap: 16, padding: "12px 0", borderBottom: "1px solid #f3f4f6" },
  toggleLabel:       { fontSize: 14, fontWeight: 600, color: "#111827", marginBottom: 2 },
  toggleDesc:        { fontSize: 12, color: "#9ca3af", lineHeight: 1.5 },
  toggleSwitch:      { width: 44, height: 24, borderRadius: 12, border: "none", cursor: "pointer", flexShrink: 0, position: "relative", transition: "background .2s" },
  toggleThumb:       { position: "absolute", top: 2, left: 2, width: 20, height: 20, background: "#fff", borderRadius: "50%", transition: "transform .2s", display: "block" },
  retentionGrid:     { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginTop: 8 },
  retentionBtn:      { padding: "10px 0", border: "1.5px solid #d1d5db", borderRadius: 8, background: "#fff", fontSize: 13, cursor: "pointer", fontWeight: 500, color: "#374151", transition: "all .15s" },
  retentionBtnActive:{ borderColor: "#0d6e4c", background: "#ecfdf5", color: "#0d6e4c", fontWeight: 700 },
  saveRow:           { display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 14, marginBottom: 20 },
  saveBtn:           { padding: "11px 28px", background: "#0d6e4c", color: "#fff", border: "none", borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: "pointer" },
  savedTag:          { fontSize: 13, color: "#16a34a", fontWeight: 600 },
  rightCard:         { display: "flex", alignItems: "flex-start", gap: 20, padding: "16px 0", borderBottom: "1px solid #f3f4f6" },
  rightTitle:        { fontSize: 14, color: "#111827" },
  rightDesc:         { fontSize: 12, color: "#9ca3af", lineHeight: 1.6, margin: "4px 0 0" },
  requestedTag:      { fontSize: 12, color: "#16a34a", marginTop: 4 },
  rightBtn:          { padding: "8px 16px", background: "#f0fdf4", border: "1.5px solid #86efac", color: "#15803d", borderRadius: 7, fontSize: 13, fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap", flexShrink: 0 },
  errorBox:          { background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8, padding: "12px 16px", color: "#dc2626", fontSize: 13, marginBottom: 20 },
  spinnerWrap:       { display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" },
  spinner:           { width: 40, height: 40, border: "4px solid #e5e7eb", borderTopColor: "#0d6e4c", borderRadius: "50%", animation: "spin 0.8s linear infinite" },
  modalBackdrop:     { position: "fixed", inset: 0, background: "rgba(0,0,0,.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 },
  modal:             { background: "#fff", borderRadius: 16, padding: "36px 40px", maxWidth: 440, width: "90%", boxShadow: "0 16px 64px rgba(0,0,0,.2)" },
};
