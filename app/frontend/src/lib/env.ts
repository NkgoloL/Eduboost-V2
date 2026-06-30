import { z } from "zod";

const PUBLIC_ENV_ALLOWLIST = new Set(["NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_APP_ENV", "NEXT_PUBLIC_ENABLE_DEV_SESSION"]);
const SECRET_NAME_PATTERN = /(SECRET|TOKEN|KEY|PASSWORD|PRIVATE|DATABASE_URL|REDIS_URL)/i;

function normalizeFrontendApiUrl(value: string) {
  const trimmed = value.trim().replace(/\/+$/, "");
  if (trimmed.endsWith("/api/v2")) return trimmed;
  return `${trimmed}/api/v2`;
}

const frontendEnvSchema = z.object({
  NEXT_PUBLIC_API_URL: z
    .string()
    .min(1, "NEXT_PUBLIC_API_URL is required")
    .default("http://localhost:8000/api/v2"),
  NEXT_PUBLIC_APP_ENV: z
    .enum(["development", "staging", "production"])
    .default("development"),
  NEXT_PUBLIC_ENABLE_DEV_SESSION: z
    .string()
    .optional()
    .default("false"),
  NEXT_PUBLIC_SITE_URL: z
    .string()
    .url("NEXT_PUBLIC_SITE_URL must be a valid URL")
    .optional(),
});

export type ValidatedFrontendEnv = z.infer<typeof frontendEnvSchema>;

export function getValidatedEnv(): ValidatedFrontendEnv {
  const result = frontendEnvSchema.safeParse({
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV,
    NEXT_PUBLIC_ENABLE_DEV_SESSION: process.env.NEXT_PUBLIC_ENABLE_DEV_SESSION,
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
  });

  if (!result.success) {
    const issues = result.error.issues
      .map((i) => `  - ${i.path.join(".")}: ${i.message}`)
      .join("\n");
    throw new Error(`Frontend environment validation failed:\n${issues}`);
  }

  return result.data;
}

export interface FrontendEnvReport {
  publicApiUrl: string;
  appEnv: string;
  devSessionEnabled: boolean;
  exposedSecretLikeKeys: string[];
}

export function getFrontendEnv(): FrontendEnvReport {
  const exposedSecretLikeKeys = Object.keys(process.env).filter(
    (key) => key.startsWith("NEXT_PUBLIC_") && SECRET_NAME_PATTERN.test(key) && !PUBLIC_ENV_ALLOWLIST.has(key)
  );

  return {
    publicApiUrl: normalizeFrontendApiUrl(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v2"),
    appEnv: process.env.NEXT_PUBLIC_APP_ENV || process.env.NODE_ENV || "development",
    devSessionEnabled: process.env.NEXT_PUBLIC_ENABLE_DEV_SESSION === "true" || process.env.NODE_ENV !== "production",
    exposedSecretLikeKeys,
  };
}

export function assertNoPublicSecretEnv() {
  const report = getFrontendEnv();
  if (report.exposedSecretLikeKeys.length > 0) {
    throw new Error(`Secret-like browser environment variables are not allowed: ${report.exposedSecretLikeKeys.join(", ")}`);
  }
  return report;
}
