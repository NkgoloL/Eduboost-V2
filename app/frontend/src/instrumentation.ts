import { getValidatedEnv } from "@/lib/env";

export async function register() {
  const env = getValidatedEnv();

  const { captureEvent, captureTestEvent } = await import("@/lib/monitoring");

  if (env.NEXT_PUBLIC_APP_ENV === "production") {
    captureEvent({
      level: "info",
      message: "frontend instrumentation initialised",
      tags: { env: env.NEXT_PUBLIC_APP_ENV },
    });
  }

  if (process.env.NEXT_RUNTIME === "nodejs") {
    captureTestEvent();
  }
}
