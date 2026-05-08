"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "../../../components/ui/Card";
import { Button } from "../../../components/ui/Button";
import { AuthService, ConsentService, LearnerService } from "../../../lib/api/services";
import { decodeJwtPayload, extractErrorMessage } from "../../../lib/api/client";
import { useLearner } from "../../../context/LearnerContext";

const passwordHint = "Use at least 12 characters with upper/lowercase letters, a number, and a symbol.";

export default function RegisterPage() {
  const router = useRouter();
  const { setLearner } = useLearner();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [learnerName, setLearnerName] = useState("");
  const [grade, setGrade] = useState(4);
  const [language, setLanguage] = useState("en");
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const nextErrors: Record<string, string> = {};
    if (fullName.trim().length < 2) nextErrors.fullName = "Enter the guardian's full name.";
    if (!email.includes("@")) nextErrors.email = "Enter a valid email address.";
    if (password.length < 12) nextErrors.password = passwordHint;
    if (learnerName.trim().length < 2) nextErrors.learnerName = "Enter the learner's display name.";
    if (!consentAccepted) nextErrors.consent = "Guardian consent is required before EduBoost can process learner data.";
    setFieldErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setLoading(true);

    try {
      const auth = await AuthService.registerGuardian({ email, password, display_name: fullName });
      const payload = decodeJwtPayload(auth.access_token);
      if (payload?.sub) localStorage.setItem("guardian_id", String(payload.sub));

      const learner = await LearnerService.registerLearner({ display_name: learnerName, grade, language });
      await ConsentService.grant(learner.id || learner.learner_id);
      setLearner({ ...learner, nickname: learner.nickname || learner.display_name || learnerName, avatar: 0 });
      router.push("/diagnostic");
    } catch (err) {
      setError(extractErrorMessage(err, "Registration failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-8 shadow-xl bg-white">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-['Baloo_2'] text-[var(--text)] mb-2">Create Account</h1>
        <p className="text-[var(--muted)]">Guardian registration, learner setup, and POPIA consent</p>
      </div>

      {error && <div role="alert" className="bg-red-50 text-red-700 p-3 rounded-md mb-4 text-sm">{error}</div>}

      <form onSubmit={handleRegister} className="space-y-4" noValidate>
        <fieldset className="space-y-4">
          <legend className="font-black text-gray-800">Guardian details</legend>
          <div>
            <label htmlFor="guardian-name" className="block text-sm font-bold text-gray-700 mb-1">Full name</label>
            <input id="guardian-name" type="text" required minLength={2} autoComplete="name" aria-invalid={Boolean(fieldErrors.fullName)} aria-describedby={fieldErrors.fullName ? "guardian-name-error" : undefined} className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            {fieldErrors.fullName && <p id="guardian-name-error" className="form-error">{fieldErrors.fullName}</p>}
          </div>
          <div>
            <label htmlFor="guardian-email" className="block text-sm font-bold text-gray-700 mb-1">Email</label>
            <input id="guardian-email" type="email" required autoComplete="email" aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? "guardian-email-error" : undefined} className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={email} onChange={(e) => setEmail(e.target.value)} />
            {fieldErrors.email && <p id="guardian-email-error" className="form-error">{fieldErrors.email}</p>}
          </div>
          <div>
            <label htmlFor="guardian-password" className="block text-sm font-bold text-gray-700 mb-1">Password</label>
            <input id="guardian-password" type="password" required minLength={12} autoComplete="new-password" aria-invalid={Boolean(fieldErrors.password)} aria-describedby="password-hint guardian-password-error" className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={password} onChange={(e) => setPassword(e.target.value)} />
            <p id="password-hint" className="form-hint">{passwordHint}</p>
            {fieldErrors.password && <p id="guardian-password-error" className="form-error">{fieldErrors.password}</p>}
          </div>
        </fieldset>

        <fieldset className="space-y-4 pt-4 border-t border-gray-200">
          <legend className="font-black text-gray-800">Learner setup</legend>
          <div>
            <label htmlFor="learner-name" className="block text-sm font-bold text-gray-700 mb-1">Learner display name</label>
            <input id="learner-name" type="text" required minLength={2} autoComplete="off" aria-invalid={Boolean(fieldErrors.learnerName)} aria-describedby={fieldErrors.learnerName ? "learner-name-error" : undefined} className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={learnerName} onChange={(e) => setLearnerName(e.target.value)} />
            {fieldErrors.learnerName && <p id="learner-name-error" className="form-error">{fieldErrors.learnerName}</p>}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="learner-grade" className="block text-sm font-bold text-gray-700 mb-1">Grade</label>
              <select id="learner-grade" className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={grade} onChange={(e) => setGrade(Number(e.target.value))}>
                {[0, 1, 2, 3, 4, 5, 6, 7].map((value) => <option key={value} value={value}>{value === 0 ? "Grade R" : `Grade ${value}`}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="learner-language" className="block text-sm font-bold text-gray-700 mb-1">Learning language</label>
              <select id="learner-language" className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="en">English</option>
                <option value="af">Afrikaans</option>
                <option value="zu">isiZulu</option>
                <option value="xh">isiXhosa</option>
              </select>
            </div>
          </div>
        </fieldset>

        <div className="rounded-xl border border-blue-100 bg-blue-50 p-4">
          <label htmlFor="guardian-consent" className="flex items-start gap-3 text-sm text-blue-950">
            <input id="guardian-consent" type="checkbox" className="mt-1 h-5 w-5" checked={consentAccepted} onChange={(e) => setConsentAccepted(e.target.checked)} aria-invalid={Boolean(fieldErrors.consent)} aria-describedby="consent-help consent-error" />
            <span>
              I am the learner&apos;s guardian and consent to EduBoost processing this learner&apos;s information for diagnostics, lessons, progress tracking, and parent reporting.
            </span>
          </label>
          <p id="consent-help" className="form-hint">You can export, restrict, or request erasure of learner data from the parent dashboard.</p>
          {fieldErrors.consent && <p id="consent-error" className="form-error">{fieldErrors.consent}</p>}
        </div>

        <Button type="submit" fullWidth disabled={loading} aria-busy={loading}>
          {loading ? "Creating account and consent..." : "Create Account & Start Diagnostic"}
        </Button>
      </form>

      <p className="text-center mt-4 text-sm text-gray-600">
        Already have an account? <button type="button" onClick={() => router.push("/login")} className="text-blue-600 font-bold hover:underline">Log In</button>
      </p>
    </Card>
  );
}
