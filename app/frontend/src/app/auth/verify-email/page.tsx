"use client";

/**
 * Email Verification Page — EduBoost SA V2
 *
 * Place at:
 *   app/frontend/src/app/auth/verify-email/page.tsx
 *
 * Routes:
 *   /auth/verify-email?token=X  → auto-verifies on mount
 *   /auth/verify-email          → error + resend button
 */

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";

type ApiDetail = { detail?: string };

type Status = "verifying" | "success" | "error" | "resent";

export default function VerifyEmailPage() {
  const params = useSearchParams();
  const router = useRouter();
  const token  = params.get("token");

  const [status,  setStatus]  = useState<Status>(token ? "verifying" : "error");
  const [message, setMessage] = useState(
    token ? "" : "No verification token found. Please use the link from your email."
  );
  const [loading, setLoading] = useState(false);

  // ── Auto-verify on mount when token present ───────────────────────────────
  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await fetch(
          `/api/v2/auth/verify-email?token=${encodeURIComponent(token)}`
        );
        if (res.ok) {
          setStatus("success");
        } else {
          const data: ApiDetail = await res.json().catch(() => ({}));
          setStatus("error");
          setMessage(data.detail ?? "This link is invalid or has expired.");
        }
      } catch {
        setStatus("error");
        setMessage("Network error — please try again.");
      }
    })();
  }, [token]);

  // ── Resend verification email ─────────────────────────────────────────────
  async function handleResend() {
    setLoading(true);
    try {
      const res = await fetch("/api/v2/auth/send-verification", {
        method:      "POST",
        credentials: "include",
      });
      if (res.ok) {
        setStatus("resent");
      } else {
        const data: ApiDetail = await res.json().catch(() => ({}));
        setMessage(data.detail ?? "Could not resend. Please try again.");
      }
    } catch {
      setMessage("Network error — please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={s.page}>
      <div style={s.card}>
        <div style={s.header}>
          <span style={s.lion}>🦁</span>
          <h1 style={s.brand}>EduBoost SA</h1>
        </div>

        <div style={s.body} data-testid="verify-page">

          {/* Verifying spinner */}
          {status === "verifying" && (
            <div style={s.center}>
              <div style={s.spinner} />
              <p style={s.subtitle}>Verifying your email…</p>
            </div>
          )}

          {/* Success */}
          {status === "success" && (
            <div style={s.center} data-testid="verify-success">
              <div style={s.bigIcon}>✅</div>
              <h2 style={s.title}>Email verified!</h2>
              <p style={s.subtitle}>
                Your email address has been confirmed. You&apos;re one step closer to
                your personalised learning journey.
              </p>
              <button
                onClick={() => router.push("/onboarding")}
                style={s.btn}
                data-testid="continue-btn"
              >
                Continue onboarding →
              </button>
            </div>
          )}

          {/* Error */}
          {status === "error" && (
            <div style={s.center} data-testid="verify-error">
              <div style={s.bigIcon}>❌</div>
              <h2 style={s.title}>Verification failed</h2>
              <p style={s.subtitle}>{message}</p>
              <button
                onClick={handleResend}
                disabled={loading}
                style={s.btn}
                data-testid="resend-btn"
              >
                {loading ? "Sending…" : "Resend verification email"}
              </button>
              <a href="/auth/login" style={s.back}>Back to login</a>
            </div>
          )}

          {/* Resent confirmation */}
          {status === "resent" && (
            <div style={s.center} data-testid="resent-message">
              <div style={s.bigIcon}>📬</div>
              <h2 style={s.title}>Email sent!</h2>
              <p style={s.subtitle}>
                A new verification link has been sent. Check your inbox and spam folder.
              </p>
              <a href="/auth/login" style={s.back}>Back to login</a>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const s: Record<string, React.CSSProperties> = {
  page:    { minHeight: "100vh", background: "#f0f4f8", display: "flex", alignItems: "center", justifyContent: "center", padding: 24, fontFamily: "'Segoe UI', Arial, sans-serif" },
  card:    { width: "100%", maxWidth: 420, background: "#fff", borderRadius: 16, overflow: "hidden", boxShadow: "0 8px 32px rgba(0,0,0,.10)" },
  header:  { background: "linear-gradient(135deg, #1a3c5e 0%, #0d6e4c 100%)", padding: "28px 36px", display: "flex", alignItems: "center", gap: 12 },
  lion:    { fontSize: 32 },
  brand:   { color: "#fff", margin: 0, fontSize: 22, fontWeight: 700 },
  body:    { padding: "40px 36px" },
  center:  { textAlign: "center" },
  bigIcon: { fontSize: 52, marginBottom: 16 },
  title:   { fontSize: 22, fontWeight: 700, color: "#111827", margin: "0 0 10px" },
  subtitle:{ fontSize: 14, color: "#6b7280", lineHeight: 1.7, margin: "0 0 24px" },
  btn:     { width: "100%", padding: "12px 0", background: "#0d6e4c", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: "pointer" },
  back:    { display: "block", marginTop: 16, fontSize: 13, color: "#6b7280", textDecoration: "none" },
  spinner: {
    width: 40, height: 40, border: "4px solid #e5e7eb", borderTopColor: "#0d6e4c",
    borderRadius: "50%", margin: "0 auto 16px",
    animation: "spin 0.8s linear infinite",
  },
};
