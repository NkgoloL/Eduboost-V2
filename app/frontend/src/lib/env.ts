const PUBLIC_ENV_ALLOWLIST = new Set(["NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_APP_ENV", "NEXT_PUBLIC_ENABLE_DEV_SESSION"]);
const SECRET_NAME_PATTERN = /(SECRET|TOKEN|KEY|PASSWORD|PRIVATE|DATABASE_URL|REDIS_URL)/i;

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
    publicApiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v2",
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
