"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Eye, EyeOff, Loader2, Zap, CheckCircle2, ArrowRight,
  BookOpen, BarChart2, ShieldCheck, Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form, FormControl, FormField, FormItem, FormLabel,
} from "@/components/ui/form";
import { cn } from "@/lib/utils";
import { useRouter, useSearchParams } from "next/navigation";
import { AuthService, ParentService } from "@/lib/api/services";
import { extractErrorMessage } from "@/lib/api/client";
import { useLearner } from "@/context/LearnerContext";
import {
  ValidationMessage,
  ValidationSummary,
} from "@/components/forms/ValidationMessage";
import type { SummaryItem } from "@/components/forms/ValidationMessage";

// ── Schema ───────────────────────────────────────────────────────────────────
const loginSchema = z.object({
  email:    z.string().email("Please enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  remember: z.boolean().optional(),
});
type LoginFormValues = z.infer<typeof loginSchema>;

const FIELD_IDS = {
  email: "login-email",
  password: "login-password",
} as const;

// ── Feature list for the left panel ──────────────────────────────────────────
const PANEL_FEATURES = [
  { icon: BookOpen,   text: "CAPS-aligned lessons for Grades 4–7",     tag: "New" },
  { icon: BarChart2,  text: "Real-time progress dashboards & reports",  tag: null  },
  { icon: ShieldCheck, text: "POPIA compliant & safe for all learners", tag: null  },
  { icon: Sparkles,   text: "AI-powered adaptive learning paths",       tag: "Beta" },
];

// ── Social button ─────────────────────────────────────────────────────────────
function SocialButton({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      className={cn(
        "flex h-10 items-center justify-center gap-2 rounded-xl border px-4 text-sm font-medium",
        "border-navy-600/70 bg-navy-800/60 text-cream-muted/80",
        "transition-all duration-200",
        "hover:border-navy-500 hover:bg-navy-700/60 hover:text-cream hover:shadow-card",
        "active:scale-[0.98]"
      )}
      {...props}
    >
      {children}
    </button>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setLearner } = useLearner();
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess]           = useState(false);
  const [error, setError]               = useState("");

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "", remember: false },
  });

  const { isSubmitting, errors } = form.formState;

  async function onSubmit(values: LoginFormValues) {
    setError("");
    try {
      await AuthService.loginGuardian({
        email: values.email,
        password: values.password,
      });
      const dashboard = await ParentService.getDashboard();
      const active = dashboard.learners?.[0];
      if (!active) {
        setError("Signed in, but no learner profile is linked to this account yet.");
        return;
      }

      const learnerId = String(active.learner_id);
      setLearner({
        learner_id: learnerId,
        id: learnerId,
        display_name: active.display_name,
        nickname: active.display_name,
        grade: Number(active.grade_level) || 4,
        language: "en",
        archetype: active.archetype ?? null,
      });
      setSuccess(true);
      const redirect = searchParams?.get("redirect") || "/dashboard";
      router.push(redirect);
    } catch (err) {
      setError(extractErrorMessage(err, "Sign in failed. Please check your details and try again."));
    }
  }

  const summaryItems: SummaryItem[] = useMemo(
    () => Object.entries(errors)
      .flatMap(([name, detail]) => {
        const id = FIELD_IDS[name as keyof typeof FIELD_IDS];
        if (!id || !detail?.message) return [];
        return [{ id, label: detail.message } satisfies SummaryItem];
      }),
    [errors]
  );

  return (
    <div className="flex min-h-screen bg-navy-900">

      {/* ── Left: decorative panel ─────────────────────────────────────── */}
      <div className="hidden lg:flex lg:w-[45%] relative overflow-hidden bg-navy-950 flex-col justify-between p-12">

        {/* Multi-layer backgrounds */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_40%_50%_at_25%_25%,rgba(13,127,192,0.22),transparent)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_40%_at_80%_75%,rgba(0,207,209,0.12),transparent)]" />
        <div className="absolute inset-0 grid-pattern opacity-40" />

        {/* Floating orbs */}
        <div className="pointer-events-none absolute -top-12 -right-12 h-72 w-72 rounded-full bg-gradient-to-br from-electric-500/12 to-aqua-500/8 blur-3xl animate-float" />
        <div className="pointer-events-none absolute bottom-0 -left-16 h-64 w-64 rounded-full bg-gradient-to-br from-aqua-500/8 to-teal-500/6 blur-3xl animate-float-slow" />
        <div className="pointer-events-none absolute top-1/2 left-1/3 h-32 w-32 -translate-y-1/2 rounded-full bg-electric-400/6 blur-2xl animate-pulse-glow" />

        {/* Top edge gradient */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-electric-500/25 to-transparent" />
        {/* Right edge gradient */}
        <div className="pointer-events-none absolute inset-y-0 right-0 w-px bg-gradient-to-b from-transparent via-aqua-500/12 to-transparent" />

        {/* ── Logo ───────────────────────────────────────────────────── */}
        <div className="relative z-10 flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-electric-500 to-aqua-500 shadow-glow">
            <Zap className="h-5 w-5 text-white" strokeWidth={2.5} />
          </div>
          <span className="font-display text-xl font-bold tracking-tight text-cream">
            Edu<span className="text-gradient">Boost</span>
            <span className="ml-0.5 font-normal text-cream-muted">SA</span>
          </span>
        </div>

        {/* ── Centre content ──────────────────────────────────────────── */}
        <div className="relative z-10 space-y-8">
          <div>
            <p className="mb-3 text-2xs font-bold uppercase tracking-[0.14em] text-aqua-400/60">
              Trusted by 50,000+ learners
            </p>
            <blockquote className="font-display text-2xl font-bold leading-snug text-cream">
              &ldquo;Empowering South African learners, one lesson at a time.&rdquo;
            </blockquote>
            <p className="mt-3 text-sm leading-relaxed text-cream-muted/60">
              Join thousands of students building confidence and achieving results with EduBoost SA.
            </p>
          </div>

          {/* Features */}
          <ul className="space-y-3.5">
            {PANEL_FEATURES.map(({ icon: Icon, text, tag }) => (
              <li key={text} className="flex items-center gap-3.5 group">
                <div
                  className={cn(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-xl",
                    "border border-aqua-500/20 bg-aqua-500/8",
                    "transition-all duration-300 group-hover:bg-aqua-500/15 group-hover:border-aqua-500/35"
                  )}
                >
                  <Icon className="h-3.5 w-3.5 text-aqua-400" />
                </div>
                <span className="flex-1 text-sm text-cream-muted/75">{text}</span>
                {tag && (
                  <span className="rounded-full border border-electric-700/50 bg-electric-900/40 px-2 py-0.5 text-2xs font-bold text-electric-300">
                    {tag}
                  </span>
                )}
              </li>
            ))}
          </ul>

          {/* Social proof mini-bar */}
          <div className="flex items-center gap-3 rounded-xl border border-navy-700/60 bg-navy-800/40 px-4 py-3">
            <div className="flex -space-x-2">
              {["JM", "TN", "KV", "AM"].map((initials) => (
                <div
                  key={initials}
                  className="flex h-7 w-7 items-center justify-center rounded-full border-2 border-navy-800 bg-gradient-to-br from-electric-900 to-navy-700 text-[0.6rem] font-bold text-aqua-300"
                >
                  {initials}
                </div>
              ))}
            </div>
            <p className="text-xs text-cream-muted/60">
              <span className="font-semibold text-cream">2,400+</span> learners joined this month
            </p>
          </div>
        </div>

        {/* ── Bottom badges ───────────────────────────────────────────── */}
        <div className="relative z-10 space-y-3">
          <div className="flex flex-wrap gap-2">
            <span className="badge-aqua text-2xs">POPIA Compliant</span>
            <span className="badge-electric text-2xs">CAPS Aligned</span>
            <span className="badge-teal text-2xs">Grade 4–7</span>
          </div>
          <p className="text-xs text-cream-muted/35">Proudly South African 🇿🇦</p>
        </div>
      </div>

      {/* ── Right: login form ───────────────────────────────────────────── */}
      <div className="relative flex flex-1 items-center justify-center p-8">
        {/* Subtle ambient */}
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_50%_0%,rgba(13,127,192,0.05),transparent)]" />

        <div className="relative w-full max-w-[400px] animate-fade-in">

          {/* Mobile logo */}
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-electric-500 to-aqua-500 shadow-glow-sm">
              <Zap className="h-4 w-4 text-white" strokeWidth={2.5} />
            </div>
            <span className="font-display text-lg font-bold tracking-tight text-cream">
              Edu<span className="text-gradient">Boost</span>
              <span className="ml-0.5 font-normal text-cream-muted">SA</span>
            </span>
          </div>

          {/* Success state */}
          {success ? (
            <div className="flex flex-col items-center gap-4 py-12 text-center animate-scale-in">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-success/10 border border-success/20">
                <CheckCircle2 className="h-8 w-8 text-success" />
              </div>
              <div>
                <h2 className="font-display text-xl font-bold text-cream mb-1.5">Welcome back!</h2>
                <p className="text-sm text-cream-muted/60">Redirecting you to your dashboard…</p>
              </div>
              <div className="h-1 w-32 overflow-hidden rounded-full bg-navy-700">
                <div className="h-full animate-shimmer bg-gradient-to-r from-transparent via-aqua-400/60 to-transparent" />
              </div>
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="mb-7">
                <h1 className="font-display text-2xl font-bold text-cream mb-1.5">Welcome back</h1>
                <p className="text-sm text-cream-muted/60">Sign in to continue your learning journey</p>
              </div>

              {error && (
                <ValidationMessage
                  title={error}
                  tone="error"
                  autoFocus
                  className="mb-4"
                />
              )}

              <ValidationSummary
                items={summaryItems}
                tone="error"
                heading="Please review the highlighted fields"
                description="All fields are required to continue signing in."
                className="mb-5"
                autoFocus={Boolean(summaryItems.length)}
              />

              {/* Social login */}
              <div className="mb-5 grid grid-cols-2 gap-3">
                <SocialButton>
                  <svg className="h-4 w-4 shrink-0" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  Google
                </SocialButton>
                <SocialButton>
                  <svg className="h-4 w-4 shrink-0" viewBox="0 0 23 23" aria-hidden="true">
                    <path fill="#f3f3f3" d="M0 0h23v23H0z"/><path fill="#f35325" d="M1 1h10v10H1z"/>
                    <path fill="#81bc06" d="M12 1h10v10H12z"/><path fill="#05a6f0" d="M1 12h10v10H1z"/>
                    <path fill="#ffba08" d="M12 12h10v10H12z"/>
                  </svg>
                  Microsoft
                </SocialButton>
              </div>

              {/* Divider */}
              <div className="mb-5 flex items-center gap-3">
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-navy-600 to-transparent" />
                <span className="shrink-0 text-xs text-cream-muted/35">or sign in with email</span>
                <div className="h-px flex-1 bg-gradient-to-r from-navy-600 via-navy-600/0 to-transparent" />
              </div>

              {/* Form */}
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">

                  {/* Email */}
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium text-cream-muted/80">Email address</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            id={FIELD_IDS.email}
                            type="email"
                            placeholder="you@example.co.za"
                            autoComplete="email"
                            className={cn(
                              "h-11 text-sm",
                              "bg-navy-800/70 border-navy-600/70 text-cream placeholder:text-cream-muted/30",
                              "focus-visible:ring-0 focus-visible:border-aqua-500/50 focus-visible:bg-navy-800",
                              "focus-visible:shadow-[0_0_0_3px_rgba(0,207,209,0.06)]",
                              "transition-all duration-200"
                            )}
                            aria-invalid={Boolean(form.formState.errors.email)}
                            aria-describedby={form.formState.errors.email ? `${FIELD_IDS.email}-error` : undefined}
                          />
                        </FormControl>
                        {errors.email?.message && (
                          <ValidationMessage
                            id={`${FIELD_IDS.email}-error`}
                            title={errors.email.message}
                            tone="error"
                          />
                        )}
                      </FormItem>
                    )}
                  />

                  {/* Password */}
                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <div className="mb-1.5 flex items-center justify-between">
                          <FormLabel className="text-sm font-medium text-cream-muted/80">Password</FormLabel>
                          <Link
                            href="/forgot-password"
                            className="text-xs font-medium text-electric-400 hover:text-aqua-300 transition-colors"
                          >
                            Forgot password?
                          </Link>
                        </div>
                        <FormControl>
                          <div className="relative">
                            <Input
                              {...field}
                              id={FIELD_IDS.password}
                              type={showPassword ? "text" : "password"}
                              placeholder="••••••••"
                              autoComplete="current-password"
                              className={cn(
                                "h-11 pr-11 text-sm",
                                "bg-navy-800/70 border-navy-600/70 text-cream placeholder:text-cream-muted/30",
                                "focus-visible:ring-0 focus-visible:border-aqua-500/50 focus-visible:bg-navy-800",
                                "focus-visible:shadow-[0_0_0_3px_rgba(0,207,209,0.06)]",
                                "transition-all duration-200"
                              )}
                              aria-invalid={Boolean(form.formState.errors.password)}
                              aria-describedby={form.formState.errors.password ? `${FIELD_IDS.password}-error` : undefined}
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-cream-muted/30 hover:text-cream-muted/70 transition-colors"
                              aria-label={showPassword ? "Hide password" : "Show password"}
                            >
                              {showPassword
                                ? <EyeOff className="h-4 w-4" />
                                : <Eye className="h-4 w-4" />
                              }
                            </button>
                          </div>
                        </FormControl>
                        {errors.password?.message && (
                          <ValidationMessage
                            id={`${FIELD_IDS.password}-error`}
                            title={errors.password.message}
                            tone="error"
                          />
                        )}
                      </FormItem>
                    )}
                  />

                  {/* Remember me */}
                  <FormField
                    control={form.control}
                    name="remember"
                    render={({ field }) => (
                      <FormItem className="flex items-center gap-2.5 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                            className="border-navy-500 data-[state=checked]:bg-electric-500 data-[state=checked]:border-electric-500"
                          />
                        </FormControl>
                        <FormLabel className="cursor-pointer text-sm font-normal text-cream-muted/65">
                          Remember me for 30 days
                        </FormLabel>
                      </FormItem>
                    )}
                  />

                  {/* Submit */}
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className={cn(
                      "group relative mt-2 h-11 w-full overflow-hidden font-semibold text-white",
                      "bg-gradient-to-r from-electric-500 to-aqua-500",
                      "shadow-glow-sm hover:shadow-glow transition-all duration-300",
                      "hover:opacity-95 active:scale-[0.99]",
                      "disabled:opacity-60 disabled:cursor-not-allowed"
                    )}
                  >
                    {/* Hover shimmer */}
                    <span className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/12 to-transparent transition-transform duration-700 group-hover:translate-x-full" />

                    {isSubmitting ? (
                      <span className="relative z-10 flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Signing in…
                      </span>
                    ) : (
                      <span className="relative z-10 flex items-center gap-2">
                        Sign In
                        <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
                      </span>
                    )}
                  </Button>
                </form>
              </Form>

              {/* Sign up link */}
              <p className="mt-6 text-center text-sm text-cream-muted/50">
                Don&apos;t have an account?{" "}
                <Link
                  href="/register"
                  className="font-semibold text-aqua-400 hover:text-aqua-300 transition-colors"
                >
                  Sign up free
                </Link>
              </p>

              {/* Security note */}
              <div className="mt-5 flex items-center justify-center gap-1.5 text-2xs text-cream-muted/30">
                <CheckCircle2 className="h-3 w-3 shrink-0" />
                <span>256-bit encrypted · POPIA compliant · No ads</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
