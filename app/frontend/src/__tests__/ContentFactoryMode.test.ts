import { describe, expect, it } from "vitest";
import { shouldUseMockContentFactoryDashboard } from "../lib/admin/contentFactoryMode";

describe("content factory admin mode", () => {
  it("allows mock dashboard only outside production", () => {
    expect(shouldUseMockContentFactoryDashboard({ NEXT_PUBLIC_CONTENT_FACTORY_MOCK: "true", NODE_ENV: "development" })).toBe(true);
    expect(shouldUseMockContentFactoryDashboard({ NEXT_PUBLIC_CONTENT_FACTORY_MOCK: "true", NODE_ENV: "production" })).toBe(false);
  });

  it("uses live dashboard by default", () => {
    expect(shouldUseMockContentFactoryDashboard({ NODE_ENV: "development" })).toBe(false);
  });
});
