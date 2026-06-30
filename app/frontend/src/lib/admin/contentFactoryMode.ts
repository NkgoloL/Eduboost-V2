export function shouldUseMockContentFactoryDashboard(env: NodeJS.ProcessEnv = process.env): boolean {
  return env.NEXT_PUBLIC_CONTENT_FACTORY_MOCK === "true" && env.NODE_ENV !== "production";
}
