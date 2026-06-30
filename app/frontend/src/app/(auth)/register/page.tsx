"use client";

import React, { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Card } from "../../../components/ui/Card-legacy";
import { Button } from "../../../components/ui/Button-legacy";
import { AuthService, ConsentService, LearnerService } from "../../../lib/api/services";
import { extractErrorMessage } from "../../../lib/api/client";
import { useLearner } from "../../../context/LearnerContext";
import {
  ValidationMessage,
  ValidationSummary,
} from "@/components/forms/ValidationMessage";
import type { SummaryItem } from "@/components/forms/ValidationMessage";

const passwordHint = "Use at least 12 characters with upper/lowercase letters, a number, and a symbol.";

const FIELD_IDS = {
  fullName: "guardian-name",
  email: "guardian-email",
  password: "guardian-password",
  learnerName: "learner-name",
  consent: "guardian-consent",
} as const;

const FIELD_LABELS = {
  fullName: "Guardian full name",
  email: "Guardian email",
  password: "Guardian password",
  learnerName: "Learner display name",
  consent: "Guardian consent",
} as const;

type FieldKey = keyof typeof FIELD_IDS;

const errorId = (field: FieldKey) => `${FIELD_IDS[field]}-error`;

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
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
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<FieldKey, string>>>({});

  const validate = () => {
    const nextErrors: Partial<Record<FieldKey, string>> = {};
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
      await AuthService.registerGuardian({ email, password, display_name: fullName });
      const learner = await LearnerService.registerLearner({ display_name: learnerName, grade, language });
      await ConsentService.grant(learner.id || learner.learner_id);
      setLearner({ ...learner, nickname: learner.nickname || learner.display_name || learnerName, avatar: 0 });
      const redirect = searchParams?.get("redirect") || "/diagnostic";
      router.push(redirect);
    } catch (err) {
      setError(extractErrorMessage(err, "Registration failed"));
    } finally {
      setLoading(false);
    }
  };

  const summaryItems: SummaryItem[] = useMemo(
    () => Object.entries(fieldErrors)
      .flatMap(([key, message]) => {
        if (!message) return [];
        const typedKey = key as FieldKey;
        const id = FIELD_IDS[typedKey];
        if (!id) return [];
        return [{
          id,
          label: FIELD_LABELS[typedKey] ?? typedKey,
          description: message,
        } satisfies SummaryItem];
      }),
    [fieldErrors]
  );

  return (
    <Card className="p-8 shadow-xl bg-white">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-['Baloo_2'] text-[var(--text)] mb-2">Create Account</h1>
        <p className="text-[var(--muted)]">Guardian registration, learner setup, and POPIA consent</p>
      </div>

      {error && (
        <ValidationMessage
          title={error}
          tone="error"
          className="mb-4"
          autoFocus
        />
      )}

      <form onSubmit={handleRegister} className="space-y-4" noValidate>
        <ValidationSummary
          items={summaryItems}
          heading="Please review these details"
          description="All information is required to create a guardian and learner profile."
          className="mb-2"
          autoFocus={Boolean(summaryItems.length)}
        />
        <fieldset className="space-y-4">
          <legend className="font-black text-gray-800">Guardian details</legend>
          <div>
            <label htmlFor="guardian-name" className="block text-sm font-bold text-gray-700 mb-1">Full name</label>
            <input id="guardian-name" type="text" required minLength={2} autoComplete="name" aria-invalid={Boolean(fieldErrors.fullName)} aria-describedby={fieldErrors.fullName ? errorId("fullName") : undefined} className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            {fieldErrors.fullName && (
              <ValidationMessage id={errorId("fullName")} title={fieldErrors.fullName} tone="error" />
            )}
          </div>
          <div>
            <label htmlFor="guardian-email" className="block text-sm font-bold text-gray-700 mb-1">Email</label>
            <input id="guardian-email" type="email" required autoComplete="email" aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? errorId("email") : undefined} className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={email} onChange={(e) => setEmail(e.target.value)} />
            {fieldErrors.email && (
              <ValidationMessage id={errorId("email")} title={fieldErrors.email} tone="error" />
            )}
          </div>
          <div>
            <label htmlFor="guardian-password" className="block text-sm font-bold text-gray-700 mb-1">Password</label>
            <input id="guardian-password" type="password" required minLength={12} autoComplete="new-password" aria-invalid={Boolean(fieldErrors.password)} aria-describedby={fieldErrors.password ? `password-hint ${errorId("password")}` : "password-hint"} className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={password} onChange={(e) => setPassword(e.target.value)} />
            <p id="password-hint" className="form-hint">{passwordHint}</p>
            {fieldErrors.password && (
              <ValidationMessage id={errorId("password")} title={fieldErrors.password} tone="error" />
            )}
          </div>
        </fieldset>

        <fieldset className="space-y-4 pt-4 border-t border-gray-200">
          <legend className="font-black text-gray-800">Learner setup</legend>
          <div>
            <label htmlFor="learner-name" className="block text-sm font-bold text-gray-700 mb-1">Learner display name</label>
            <input id="learner-name" type="text" required minLength={2} autoComplete="off" aria-invalid={Boolean(fieldErrors.learnerName)} aria-describedby={fieldErrors.learnerName ? errorId("learnerName") : undefined} className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={learnerName} onChange={(e) => setLearnerName(e.target.value)} />
            {fieldErrors.learnerName && (
              <ValidationMessage id={errorId("learnerName")} title={fieldErrors.learnerName} tone="error" />
            )}
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
            <input
              id="guardian-consent"
              type="checkbox"
              className="mt-1 h-5 w-5"
              checked={consentAccepted}
              onChange={(e) => setConsentAccepted(e.target.checked)}
              aria-invalid={Boolean(fieldErrors.consent)}
              aria-describedby={fieldErrors.consent ? `consent-help ${errorId("consent")}` : "consent-help"}
            />
            <span>
              I am the learner&apos;s guardian and consent to EduBoost processing this learner&apos;s information for diagnostics, lessons, progress tracking, and parent reporting.
            </span>
          </label>
          <p id="consent-help" className="form-hint">You can export, restrict, or request erasure of learner data from the parent dashboard.</p>
          {fieldErrors.consent && (
            <ValidationMessage id={errorId("consent")} title={fieldErrors.consent} tone="error" />
          )}
        </div>

        <Button type="submit" fullWidth disabled={loading} aria-busy={loading}>
          {loading ? "Creating account and consent..." : "Create Account & Start Diagnostic"}
        </Button>
      </form>

      <p className="text-center mt-4 text-sm text-gray-600">
        Already have an account? <button type="button" onClick={() => router.push(`/login${searchParams?.get("redirect") ? `?redirect=${encodeURIComponent(searchParams.get("redirect") as string)}` : ""}`)} className="text-blue-600 font-bold hover:underline">Log In</button>
      </p>
    </Card>
  );
}
