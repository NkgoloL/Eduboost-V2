import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { assertNoPublicSecretEnv, getFrontendEnv } from "../lib/env";

const sourcePath = (...parts: string[]) => join(process.cwd(), "src", ...parts);

function read(...parts: string[]) {
  return readFileSync(sourcePath(...parts), "utf8");
}

describe("PR-007 frontend accessibility and flow contracts", () => {
  it("rejects secret-like NEXT_PUBLIC environment names", () => {
    process.env.NEXT_PUBLIC_API_SECRET = "bad";
    expect(() => assertNoPublicSecretEnv()).toThrow("NEXT_PUBLIC_API_SECRET");
    delete process.env.NEXT_PUBLIC_API_SECRET;
    expect(getFrontendEnv().publicApiUrl).toContain("/api/v2");
  });

  it("uses route-level error/loading boundaries and skip links", () => {
    expect(read("app", "layout.tsx")).toContain("SkipLink");
    expect(read("app", "layout.tsx")).toContain("ErrorBoundary");
    expect(read("app", "error.tsx")).toContain("RootError");
    expect(read("app", "loading.tsx")).toContain("role=\"status\"");
  });

  it("protects learner and parent route groups", () => {
    expect(read("app", "(learner)", "layout.tsx")).toContain("RouteGuard required=\"learner\"");
    expect(read("app", "(parent)", "parent-dashboard", "page.tsx")).toContain("RouteGuard required=\"parent\"");
  });

  it("keeps auth forms accessible and consent-aware", () => {
    const login = read("app", "(auth)", "login", "page.tsx");
    const register = read("app", "(auth)", "register", "page.tsx");
    expect(
      login.includes("role=\"alert\"") ||
      login.includes("<ValidationMessage")
    ).toBe(true);
    expect(login).toContain("aria-label={showPassword ? \"Hide password\" : \"Show password\"}");
    expect(login).toContain("autoComplete=\"email\"");
    expect(register).toContain("guardian-consent");
    expect(register).toContain("aria-invalid");
    expect(register).toContain("ConsentService.grant");
  });

  it("keeps diagnostics keyboard and screen-reader friendly", () => {
    const diagnostic = read("components", "eduboost", "InteractiveDiagnostic.tsx");
    expect(diagnostic).toContain("role=\"progressbar\"");
    expect(diagnostic).toContain("role=\"radiogroup\"");
    expect(diagnostic).toContain("role=\"radio\"");
    expect(diagnostic).toContain("type=\"button\"");
  });

  it("exposes parent privacy controls and avoids hard-coded chart colors", () => {
    const parent = read("components", "eduboost", "ParentDashboard.tsx");
    expect(parent).toContain("Request export");
    expect(parent).toContain("Restrict processing");
    expect(parent).toContain("Request erasure");
    expect(parent).not.toContain("fill=\"#60a5fa\"");
  });
});
