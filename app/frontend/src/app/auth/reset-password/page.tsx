"use client";

/**
 * Password Reset Page — EduBoost SA V2
 *
 * Place at:
 *   app/frontend/src/app/auth/reset-password/page.tsx
 *
 * Routes:
 *   /auth/reset-password           → "forgot password" email request form
 *   /auth/reset-password?token=X  → new-password form (token from email link)
 *
 * Design tokens: #1a3c5e (navy), #0d6e4c (green), #f59e0b (amber)
 */

import { useState, useEffect, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";

type Step = "request" | "sent" | "reset" | "success";

const RESET_TTL_MIN = 30;

const meterColors   = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#16a34a"];
const strengthLabel = ["", "Weak", "Fair", "Good", "Strong", "Very Strong"];

export default function ResetPasswordPage() {
  const params = useSearchParams();
  const router = useRouter();
  const token  = params.get("token");

  const [step,     setStep]     = useState<Step>(token ? "reset" : "request");
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [confirm,  setConfirm]  = useState("");
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState<string | null>(null);
  const [strength, setStrength] = useState(0);
  const [showPass, setShowPass] = useState(false);

  // ── Password strength score ────────────────────────────────────────────────
  useEffect(() => {
    let score = 0;
    if (password.length >= 8)           score++;
    if (password.length >= 12)          score++;
    if (/[A-Z]/.test(password))        score++;
    if (/[0-9]/.test(password))        score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    setStrength(score);
  }, [password]);

  // ── Step 1: request reset email ────────────────────────────────────────────
  const handleRequest = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await fetch("/api/v2/auth/forgot-password", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ email }),
      });
      // Always advance — API returns 202 regardless (anti-enumeration)
      setStep("sent");
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [email]);

  // ── Step 3: submit new password ────────────────────────────────────────────
  const handleReset = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) { setError("Passwords do not match."); return; }
    if (strength < 3)          { setError("Please choose a stronger password."); return; }

    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v2/auth/reset-password", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ token, new_password: password }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError((data as { detail?: string }).detail ?? "Reset failed. Please request a new link.");
        return;
      }
      setStep("success");
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [password, confirm, strength, token]);

  const passwordsMatch = !confirm || password === confirm;

  return (
    <div style={s.page}>
      <div style={s.card}>

        {/* Header */}
        <div style={s.header}>
          <span style={s.lion}>🦁</span>
          <div>
            <h1 style={s.brand}>EduBoost SA</h1>
            <p style={s.brandTag}>Personalised learning for every learner</p>
          </div>
        </div>

        <div style={s.body}>

          {/* ── Step: request ──────────────────────────────────────── */}
          {step === "request" && (
            <>
              <h2 style={s.title}>Forgot your password?</h2>
              <p style={s.subtitle}>Enter your email and we&apos;ll send you a reset link.</p>
              <form onSubmit={handleRequest} data-testid="forgot-form" noValidate>
                <label style={s.label} htmlFor="email-input">Email address</label>
                <input
                  id="email-input"
                  data-testid="email-input"
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  style={s.input}
                />
                {error && <p role="alert" style={s.error}>{error}</p>}
                <button
                  data-testid="submit-btn"
                  type="submit"
                  disabled={loading || !email}
                  style={{ ...s.btn, opacity: loading || !email ? 0.7 : 1 }}
                >
                  {loading ? "Sending…" : "Send reset link"}
                </button>
              </form>
              <a href="/auth/login" style={s.back}>← Back to login</a>
            </>
          )}

          {/* ── Step: sent ─────────────────────────────────────────── */}
          {step === "sent" && (
            <div data-testid="sent-message" style={{ textAlign: "center" }}>
              <div style={s.bigIcon}>📬</div>
              <h2 style={s.title}>Check your inbox</h2>
              <p style={s.subtitle}>
                If <strong>{email}</strong> is registered, you&apos;ll receive a reset link
                shortly. It expires in {RESET_TTL_MIN} minutes.
              </p>
              <p style={{ ...s.subtitle, fontSize: 12, color: "#9ca3af" }}>
                Don&apos;t see it? Check your spam or junk folder.
              </p>
              <button onClick={() => setStep("request")} style={s.btnOutline}>
                Use a different email
              </button>
            </div>
          )}

          {/* ── Step: reset ────────────────────────────────────────── */}
          {step === "reset" && (
            <>
              <h2 style={s.title}>Choose a new password</h2>
              <p style={s.subtitle}>Make it strong and memorable.</p>
              <form onSubmit={handleReset} data-testid="reset-form" noValidate>

                <label style={s.label} htmlFor="password-input">New password</label>
                <div style={{ position: "relative" }}>
                  <input
                    id="password-input"
                    data-testid="password-input"
                    type={showPass ? "text" : "password"}
                    required
                    autoComplete="new-password"
                    placeholder="Min 8 chars, 1 uppercase, 1 number"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    style={{ ...s.input, paddingRight: 44 }}
                  />
                  <button
                    type="button"
                    aria-label={showPass ? "Hide password" : "Show password"}
                    onClick={() => setShowPass(p => !p)}
                    style={s.eyeBtn}
                  >
                    {showPass ? "🙈" : "👁️"}
                  </button>
                </div>

                {/* Strength meter */}
                {password && (
                  <div style={s.meterWrap} aria-label={`Password strength: ${strengthLabel[strength]}`}>
                    {[1, 2, 3, 4, 5].map(i => (
                      <div
                        key={i}
                        style={{
                          ...s.meterBar,
                          background: strength >= i ? meterColors[strength - 1] : "#e5e7eb",
                        }}
                      />
                    ))}
                    <span style={{ ...s.meterLabel, color: meterColors[strength - 1] ?? "#9ca3af" }}>
                      {strengthLabel[strength]}
                    </span>
                  </div>
                )}

                <label style={{ ...s.label, marginTop: 16 }} htmlFor="confirm-input">
                  Confirm password
                </label>
                <input
                  id="confirm-input"
                  data-testid="confirm-input"
                  type={showPass ? "text" : "password"}
                  required
                  autoComplete="new-password"
                  placeholder="Re-enter your new password"
                  value={confirm}
                  onChange={e => setConfirm(e.target.value)}
                  aria-invalid={!passwordsMatch}
                  style={{
                    ...s.input,
                    borderColor: !passwordsMatch ? "#ef4444" : undefined,
                  }}
                />
                {!passwordsMatch && (
                  <p style={s.fieldError}>Passwords do not match</p>
                )}

                {error && <p role="alert" style={s.error}>{error}</p>}
                <button
                  data-testid="reset-btn"
                  type="submit"
                  disabled={loading || !password || !confirm || !passwordsMatch}
                  style={{
                    ...s.btn,
                    opacity: loading || !password || !confirm || !passwordsMatch ? 0.7 : 1,
                  }}
                >
                  {loading ? "Updating…" : "Update password"}
                </button>
              </form>
            </>
          )}

          {/* ── Step: success ──────────────────────────────────────── */}
          {step === "success" && (
            <div data-testid="success-message" style={{ textAlign: "center" }}>
              <div style={s.bigIcon}>✅</div>
              <h2 style={s.title}>Password updated!</h2>
              <p style={s.subtitle}>Your password has been changed successfully.</p>
              <button onClick={() => router.push("/auth/login")} style={s.btn}>
                Log in
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

// ── Inline styles (EduBoost SA brand tokens) ──────────────────────────────────
const s: Record<string, React.CSSProperties> = {
  page:       { minHeight: "100vh", background: "#f0f4f8", display: "flex", alignItems: "center", justifyContent: "center", padding: 24, fontFamily: "'Segoe UI', Arial, sans-serif" },
  card:       { width: "100%", maxWidth: 440, background: "#fff", borderRadius: 16, overflow: "hidden", boxShadow: "0 8px 32px rgba(0,0,0,.10)" },
  header:     { background: "linear-gradient(135deg, #1a3c5e 0%, #0d6e4c 100%)", padding: "24px 36px", display: "flex", alignItems: "center", gap: 14 },
  lion:       { fontSize: 36 },
  brand:      { color: "#fff", margin: "0 0 2px", fontSize: 20, fontWeight: 700, letterSpacing: "-0.5px" },
  brandTag:   { color: "rgba(255,255,255,.7)", margin: 0, fontSize: 11 },
  body:       { padding: "32px 36px" },
  title:      { fontSize: 20, fontWeight: 700, color: "#111827", margin: "0 0 8px" },
  subtitle:   { fontSize: 14, color: "#6b7280", margin: "0 0 24px", lineHeight: 1.6 },
  label:      { display: "block", fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 6 },
  input:      { width: "100%", padding: "10px 14px", border: "1.5px solid #d1d5db", borderRadius: 8, fontSize: 15, outline: "none", boxSizing: "border-box", transition: "border-color .15s", background: "#fff" },
  eyeBtn:     { position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", fontSize: 16, padding: 4 },
  btn:        { marginTop: 20, width: "100%", padding: "12px 0", background: "#0d6e4c", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: "pointer", transition: "background .15s" },
  btnOutline: { marginTop: 16, padding: "10px 24px", background: "transparent", border: "1.5px solid #0d6e4c", color: "#0d6e4c", borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: "pointer" },
  error:      { margin: "12px 0 0", fontSize: 13, color: "#dc2626", background: "#fef2f2", padding: "8px 12px", borderRadius: 6, border: "1px solid #fecaca" },
  fieldError: { fontSize: 12, color: "#dc2626", margin: "4px 0 0" },
  back:       { display: "block", textAlign: "center", marginTop: 20, fontSize: 13, color: "#6b7280", textDecoration: "none" },
  bigIcon:    { fontSize: 48, margin: "0 auto 16px" },
  meterWrap:  { display: "flex", alignItems: "center", gap: 4, marginTop: 8 },
  meterBar:   { flex: 1, height: 4, borderRadius: 2, transition: "background .2s" },
  meterLabel: { fontSize: 12, fontWeight: 600, marginLeft: 6, minWidth: 64 },
};
