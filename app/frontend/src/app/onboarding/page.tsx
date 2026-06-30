"use client";

/**
 * Onboarding Wizard — EduBoost SA V2
 *
 * Place at:
 *   app/frontend/src/app/onboarding/page.tsx
 *
 * Five-step onboarding:
 *   1. email_verified   — verify email address
 *   2. profile_complete — learner name, grade, home language (saved to DB)
 *   3. guardian_consent — POPIA parental consent
 *   4. diagnostic_done  — navigate to /diagnostic
 *   5. plan_accepted    — accept CAPS study plan → redirect /dashboard
 */

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

interface OnboardingState {
  email_verified:   boolean | null;
  profile_complete: boolean | null;
  guardian_consent: boolean | null;
  diagnostic_done:  boolean | null;
  plan_accepted:    boolean | null;
  is_complete:      boolean;
  progress_pct?:    number;
}

interface ProfileData {
  display_name:  string;
  grade:         string;
  home_language: string;
}

const STEPS = [
  { key: "email_verified",   icon: "📧", label: "Verify email",         desc: "Confirm your email address to secure your account." },
  { key: "profile_complete", icon: "👤", label: "Complete your profile", desc: "Tell us about the learner so we can personalise lessons." },
  { key: "guardian_consent", icon: "🔒", label: "Guardian consent",      desc: "POPIA requires parental/guardian consent for learners under 18." },
  { key: "diagnostic_done",  icon: "🧠", label: "Diagnostic assessment", desc: "A short assessment to find the learner&apos;s exact knowledge level." },
  { key: "plan_accepted",    icon: "📅", label: "Accept study plan",     desc: "Review and accept the personalised CAPS-aligned study plan." },
] as const;

type StepKey = typeof STEPS[number]["key"];

export default function OnboardingPage() {
  const router = useRouter();

  const [state,       setState]       = useState<OnboardingState | null>(null);
  const [activeStep,  setActiveStep]  = useState(0);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState<string | null>(null);
  const [profile,     setProfile]     = useState<ProfileData>({ display_name: "", grade: "4", home_language: "en" });
  const [consentTick, setConsentTick] = useState(false);
  const [resendSent,  setResendSent]  = useState(false);

  // ── Fetch onboarding state on mount ────────────────────────────────────────
  useEffect(() => {
    fetch("/api/v2/auth/onboarding", { credentials: "include" })
      .then(r => r.json())
      .then((data: OnboardingState) => {
        setState(data);
        const idx = STEPS.findIndex(s => !data[s.key]);
        setActiveStep(idx === -1 ? STEPS.length - 1 : idx);
      })
      .catch(() => setError("Could not load onboarding status. Please refresh."));
  }, []);

  // ── Generic step completion ────────────────────────────────────────────────
  const completeStep = useCallback(async (step: StepKey) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v2/auth/onboarding/step", {
        method:      "PATCH",
        credentials: "include",
        headers:     { "Content-Type": "application/json" },
        body:        JSON.stringify({ step, value: true }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error((data as { detail?: string }).detail ?? "Something went wrong.");
      }
      const updated: OnboardingState = await res.json();
      setState(updated);
      if (updated.is_complete) {
        router.push("/dashboard");
      } else {
        setActiveStep(prev => Math.min(prev + 1, STEPS.length - 1));
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }, [router]);

  // ── Save profile data (calls dedicated profile endpoint) ───────────────────
  const saveProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v2/auth/onboarding/profile", {
        method:      "PATCH",
        credentials: "include",
        headers:     { "Content-Type": "application/json" },
        body:        JSON.stringify(profile),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error((data as { detail?: string }).detail ?? "Could not save profile.");
      }
      const result = await res.json();
      setState(result.onboarding);
      setActiveStep(prev => Math.min(prev + 1, STEPS.length - 1));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Could not save profile.");
    } finally {
      setLoading(false);
    }
  }, [profile]);

  // ── Resend verification email ──────────────────────────────────────────────
  const resendVerification = useCallback(async () => {
    setLoading(true);
    try {
      await fetch("/api/v2/auth/send-verification", {
        method: "POST", credentials: "include",
      });
      setResendSent(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const stepDone = (key: StepKey) => !!state?.[key];
  const progress = state
    ? (STEPS.filter(s => stepDone(s.key)).length / STEPS.length) * 100
    : 0;

  // ── Loading skeleton ───────────────────────────────────────────────────────
  if (!state) {
    return (
      <div style={s.page}>
        {error
          ? <div style={{ ...s.errorBox, maxWidth: 480, margin: "0 auto" }}>{error}</div>
          : <div style={s.spinnerWrap}><div style={s.spinner} /></div>
        }
      </div>
    );
  }

  const currentStep = STEPS[activeStep] ?? STEPS[0];

  return (
    <div style={s.page}>
      <div style={s.container}>

        {/* ── Sidebar ──────────────────────────────────────────────── */}
        <aside style={s.sidebar}>
          <div style={s.sideHeader}>
            <span style={s.lion}>🦁</span>
            <div>
              <div style={s.brand}>EduBoost SA</div>
              <div style={s.brandSub}>Getting started</div>
            </div>
          </div>

          {/* Progress bar */}
          <div style={s.progressWrap}>
            <div style={{ ...s.progressBar, width: `${progress}%` }} />
          </div>
          <div style={s.progressLabel}>{Math.round(progress)}% complete</div>

          {/* Step list */}
          <ul style={s.stepList}>
            {STEPS.map((step, i) => {
              const done   = stepDone(step.key);
              const active = i === activeStep;
              return (
                <li
                  key={step.key}
                  style={{
                    ...s.stepItem,
                    ...(active ? s.stepItemActive : {}),
                    ...(done   ? s.stepItemDone  : {}),
                  }}
                  onClick={() => done && setActiveStep(i)}
                  data-testid={`step-nav-${step.key}`}
                  role="button"
                  tabIndex={done ? 0 : -1}
                  aria-current={active ? "step" : undefined}
                >
                  <span style={s.stepIcon}>{done ? "✅" : step.icon}</span>
                  <span>{step.label}</span>
                </li>
              );
            })}
          </ul>
        </aside>

        {/* ── Main panel ───────────────────────────────────────────── */}
        <main style={s.main}>
          <h2 style={s.stepTitle}>{currentStep.icon} {currentStep.label}</h2>
          <p style={s.stepDesc}>{currentStep.desc}</p>

          {error && <div role="alert" style={s.errorBox}>{error}</div>}

          {/* ── Email verified step ────────────────────────────────── */}
          {currentStep.key === "email_verified" && (
            stepDone("email_verified") ? (
              <CompleteBadge label="Email already verified" />
            ) : (
              <div>
                <p style={s.info}>
                  We sent a verification email when you registered. Click the link inside
                  to verify, then refresh this page.
                </p>
                {resendSent ? (
                  <div style={s.successBox}>📬 Verification email sent! Check your inbox and spam folder.</div>
                ) : (
                  <button
                    style={s.btn}
                    disabled={loading}
                    data-testid="resend-verify-btn"
                    onClick={resendVerification}
                  >
                    {loading ? "Sending…" : "Resend verification email"}
                  </button>
                )}
              </div>
            )
          )}

          {/* ── Profile step ──────────────────────────────────────── */}
          {currentStep.key === "profile_complete" && (
            <div>
              <label style={s.label} htmlFor="display-name">Learner&apos;s full name</label>
              <input
                id="display-name"
                data-testid="display-name-input"
                style={s.input}
                placeholder="e.g. Sipho Dlamini"
                value={profile.display_name}
                onChange={e => setProfile(p => ({ ...p, display_name: e.target.value }))}
              />

              <label style={{ ...s.label, marginTop: 14 }} htmlFor="grade-select">Grade</label>
              <select
                id="grade-select"
                data-testid="grade-select"
                style={s.input}
                value={profile.grade}
                onChange={e => setProfile(p => ({ ...p, grade: e.target.value }))}
              >
                {["R","1","2","3","4","5","6","7","8","9","10","11","12"].map(g => (
                  <option key={g} value={g}>Grade {g}</option>
                ))}
              </select>

              <label style={{ ...s.label, marginTop: 14 }} htmlFor="language-select">Home language</label>
              <select
                id="language-select"
                data-testid="language-select"
                style={s.input}
                value={profile.home_language}
                onChange={e => setProfile(p => ({ ...p, home_language: e.target.value }))}
              >
                <option value="en">English</option>
                <option value="zu">isiZulu</option>
                <option value="af">Afrikaans</option>
                <option value="xh">isiXhosa</option>
                <option value="st">Sesotho</option>
                <option value="tn">Setswana</option>
              </select>

              <button
                style={{ ...s.btn, opacity: loading || !profile.display_name.trim() ? 0.7 : 1 }}
                disabled={loading || !profile.display_name.trim()}
                onClick={saveProfile}
                data-testid="save-profile-btn"
              >
                {loading ? "Saving…" : "Save & continue"}
              </button>
            </div>
          )}

          {/* ── Guardian consent step ─────────────────────────────── */}
          {currentStep.key === "guardian_consent" && (
            <div>
              <div style={s.consentBox}>
                <h4 style={{ margin: "0 0 8px", color: "#1a3c5e" }}>POPIA Parental Consent</h4>
                <p style={{ margin: 0, fontSize: 13, lineHeight: 1.8, color: "#374151" }}>
                  EduBoost SA collects and processes your child&apos;s learning data to provide
                  personalised educational content aligned with the South African CAPS curriculum.
                  Data is pseudonymised and <strong>never shared with third parties</strong> without
                  explicit consent. You may request access to or deletion of all data at any time
                  under <strong>POPIA sections 23 and 24</strong>.
                </p>
              </div>
              <label style={s.checkLabel}>
                <input
                  data-testid="consent-checkbox"
                  type="checkbox"
                  checked={consentTick}
                  onChange={e => setConsentTick(e.target.checked)}
                  style={{ marginRight: 10, width: 16, height: 16 }}
                />
                I am the parent/guardian and I give consent for EduBoost SA to process
                the learner&apos;s data as described above.
              </label>
              <button
                style={{ ...s.btn, opacity: loading || !consentTick ? 0.7 : 1 }}
                disabled={loading || !consentTick}
                onClick={() => completeStep("guardian_consent")}
                data-testid="give-consent-btn"
              >
                {loading ? "Saving…" : "Give consent & continue"}
              </button>
            </div>
          )}

          {/* ── Diagnostic step ───────────────────────────────────── */}
          {currentStep.key === "diagnostic_done" && (
            <div>
              <p style={s.info}>
                The diagnostic assessment takes about 10–15 minutes and helps us find
                exactly where the learner is in each subject — even below their current grade.
                There are no wrong answers; it&apos;s just a starting point.
              </p>
              <button
                style={s.btn}
                onClick={() => router.push("/diagnostic")}
                data-testid="start-diagnostic-btn"
              >
                Start diagnostic assessment →
              </button>
            </div>
          )}

          {/* ── Plan acceptance step ──────────────────────────────── */}
          {currentStep.key === "plan_accepted" && (
            <div>
              <p style={s.info}>
                Based on the diagnostic, we&apos;ve built a personalised CAPS-aligned study plan.
                Review it below and confirm you&apos;re happy to begin.
              </p>
              <div style={s.planPreview}>
                <span style={{ fontSize: 24, marginBottom: 8, display: "block" }}>📅</span>
                <strong style={{ color: "#1a3c5e" }}>Your study plan is ready!</strong>
                <p style={{ margin: "6px 0 0", fontSize: 13, color: "#6b7280" }}>
                  Personalised lessons will start from where the learner is right now.
                </p>
              </div>
              <button
                style={{ ...s.btn, opacity: loading ? 0.7 : 1 }}
                disabled={loading}
                onClick={() => completeStep("plan_accepted")}
                data-testid="accept-plan-btn"
              >
                {loading ? "Confirming…" : "Accept my study plan 🎉"}
              </button>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}

function CompleteBadge({ label }: { label: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#16a34a", fontWeight: 600, marginTop: 8, fontSize: 15 }}>
      <span style={{ fontSize: 22 }}>✅</span> {label}
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const s: Record<string, React.CSSProperties> = {
  page:         { minHeight: "100vh", background: "#f0f4f8", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Segoe UI', Arial, sans-serif", padding: 16 },
  container:    { width: "100%", maxWidth: 860, display: "flex", background: "#fff", borderRadius: 20, overflow: "hidden", boxShadow: "0 8px 40px rgba(0,0,0,.12)", minHeight: 540 },
  sidebar:      { width: 290, background: "linear-gradient(180deg, #1a3c5e 0%, #0d2a44 100%)", padding: "36px 24px", flexShrink: 0 },
  sideHeader:   { display: "flex", alignItems: "center", gap: 12, marginBottom: 28 },
  lion:         { fontSize: 32 },
  brand:        { color: "#fff", fontWeight: 700, fontSize: 16 },
  brandSub:     { color: "#93c5fd", fontSize: 12, marginTop: 2 },
  progressWrap: { height: 6, background: "rgba(255,255,255,.2)", borderRadius: 3, marginBottom: 6, overflow: "hidden" },
  progressBar:  { height: "100%", background: "#f59e0b", borderRadius: 3, transition: "width .4s ease" },
  progressLabel:{ color: "#93c5fd", fontSize: 11, marginBottom: 20 },
  stepList:     { listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 4 },
  stepItem:     { display: "flex", alignItems: "center", gap: 10, padding: "10px 12px", borderRadius: 8, color: "rgba(255,255,255,.6)", fontSize: 13, transition: "background .15s" },
  stepItemActive:{ background: "rgba(255,255,255,.12)", color: "#fff", fontWeight: 600 },
  stepItemDone: { color: "#86efac", cursor: "pointer" },
  stepIcon:     { fontSize: 18, width: 22, textAlign: "center" },
  main:         { flex: 1, padding: "40px 44px", overflowY: "auto" },
  stepTitle:    { fontSize: 22, fontWeight: 700, color: "#111827", margin: "0 0 8px" },
  stepDesc:     { fontSize: 14, color: "#6b7280", margin: "0 0 28px", lineHeight: 1.7 },
  label:        { display: "block", fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 6 },
  input:        { width: "100%", padding: "10px 14px", border: "1.5px solid #d1d5db", borderRadius: 8, fontSize: 15, boxSizing: "border-box", outline: "none", background: "#fff" },
  btn:          { marginTop: 20, padding: "12px 28px", background: "#0d6e4c", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: "pointer", transition: "background .15s" },
  info:         { fontSize: 14, color: "#374151", lineHeight: 1.7, marginBottom: 0 },
  consentBox:   { background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: 10, padding: "16px 18px", marginBottom: 16 },
  checkLabel:   { display: "flex", alignItems: "flex-start", fontSize: 13, color: "#374151", lineHeight: 1.6, cursor: "pointer", marginTop: 8 },
  errorBox:     { background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8, padding: "10px 14px", color: "#dc2626", fontSize: 13, marginBottom: 20 },
  successBox:   { background: "#f0fdf4", border: "1px solid #86efac", borderRadius: 8, padding: "10px 14px", color: "#15803d", fontSize: 13, marginTop: 16 },
  planPreview:  { background: "#f0f9ff", border: "1px solid #bae6fd", borderRadius: 10, padding: "20px 24px", marginBottom: 4, textAlign: "center" },
  spinnerWrap:  { display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" },
  spinner:      { width: 40, height: 40, border: "4px solid #e5e7eb", borderTopColor: "#0d6e4c", borderRadius: "50%", animation: "spin 0.8s linear infinite" },
};
