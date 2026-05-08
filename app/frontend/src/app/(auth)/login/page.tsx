"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "../../../components/ui/Card";
import { Button } from "../../../components/ui/Button";
import { AuthService } from "../../../lib/api/services";
import { useLearner } from "../../../context/LearnerContext";
import { decodeJwtPayload, extractErrorMessage } from "../../../lib/api/client";
import { getFrontendEnv } from "../../../lib/env";

export default function LoginPage() {
  const router = useRouter();
  const { setLearner } = useLearner();
  const [isParent, setIsParent] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const devSessionEnabled = getFrontendEnv().devSessionEnabled;

  const bootstrapDevSession = async (target: "learner" | "parent") => {
    setError("");
    setLoading(true);
    try {
      const res = await AuthService.createDevSession();
      localStorage.setItem("guardian_id", res.guardian_id);
      setLearner(res.learner);
      router.push(target === "parent" ? "/parent-dashboard" : "/dashboard");
    } catch (err) {
      setError(extractErrorMessage(err, "Failed to create a dev session"));
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isParent) {
        const res = await AuthService.loginGuardian({ email, password });
        const payload = decodeJwtPayload(res.access_token);
        if (payload?.sub) localStorage.setItem("guardian_id", String(payload.sub));
        router.push("/parent-dashboard");
      } else {
        await bootstrapDevSession("learner");
      }
    } catch (err) {
      setError(extractErrorMessage(err, "Failed to log in"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-8 shadow-xl bg-white">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-['Baloo_2'] text-[var(--text)] mb-2">Welcome Back</h1>
        <p className="text-[var(--muted)]">Log in to continue learning</p>
      </div>

      <div className="flex bg-gray-100 p-1 rounded-lg mb-6" role="tablist" aria-label="Choose login type">
        <button type="button" role="tab" aria-selected={!isParent} className={`flex-1 py-2 text-sm font-bold rounded-md ${!isParent ? "bg-white shadow" : "text-gray-500"}`} onClick={() => setIsParent(false)}>
          Learner
        </button>
        <button type="button" role="tab" aria-selected={isParent} className={`flex-1 py-2 text-sm font-bold rounded-md ${isParent ? "bg-white shadow" : "text-gray-500"}`} onClick={() => setIsParent(true)}>
          Parent / Guardian
        </button>
      </div>

      {error && <div role="alert" className="bg-red-50 text-red-700 p-3 rounded-md mb-4 text-sm">{error}</div>}

      <form onSubmit={handleLogin} className="space-y-4" noValidate>
        {isParent ? (
          <>
            <div>
              <label htmlFor="login-email" className="block text-sm font-bold text-gray-700 mb-1">Email</label>
              <input id="login-email" type="email" required autoComplete="email" className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div>
              <label htmlFor="login-password" className="block text-sm font-bold text-gray-700 mb-1">Password</label>
              <input id="login-password" type="password" required autoComplete="current-password" className="w-full border-2 border-gray-200 rounded-lg p-3 outline-none focus:border-[var(--gold)]" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Password reset and email verification UX pending backend endpoints.</span>
            </div>
          </>
        ) : (
          <div className="text-center py-4 text-gray-600 flex flex-col gap-3">
            <p>Learner access is created through a guardian account and consented learner profile.</p>
            <Button type="button" onClick={() => router.push("/register")} variant="secondary" className="bg-blue-50 text-blue-700 border-blue-200">
              Create Guardian + Learner Profile
            </Button>
            {devSessionEnabled && (
              <Button type="button" onClick={() => void bootstrapDevSession("learner")} variant="secondary" className="bg-green-50 text-green-700 border-green-200" disabled={loading}>
                {loading ? "Preparing dev learner..." : "Use Dev Learner Session"}
              </Button>
            )}
          </div>
        )}

        {isParent && (
          <Button type="submit" fullWidth disabled={loading} aria-busy={loading}>
            {loading ? "Logging in..." : "Log In"}
          </Button>
        )}
      </form>

      {isParent && devSessionEnabled && (
        <div className="mt-4">
          <Button type="button" onClick={() => void bootstrapDevSession("parent")} variant="secondary" fullWidth className="bg-yellow-50 text-yellow-700 border-yellow-200" disabled={loading}>
            {loading ? "Preparing dev parent..." : "Use Dev Parent Session"}
          </Button>
        </div>
      )}

      {isParent && (
        <p className="text-center mt-4 text-sm text-gray-600">
          Don&apos;t have an account? <button type="button" onClick={() => router.push("/register")} className="text-blue-600 font-bold hover:underline">Register</button>
        </p>
      )}
    </Card>
  );
}
