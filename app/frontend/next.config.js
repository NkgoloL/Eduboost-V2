/** @type {import('next').NextConfig} */
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

const withSerwist = require("@serwist/next").default({
  swSrc: "src/app/sw.ts",
  swDest: "public/sw.js",
  disable: process.env.NODE_ENV === "development",
});

function normalizeApiBaseUrl(value) {
  const trimmed = String(value || "").trim().replace(/\/+$/, "");
  if (!trimmed) {
    if (process.env.NODE_ENV === "development" || process.env.NODE_ENV === "test") {
      return "http://localhost:8000/api/v2";
    }
    throw new Error("NEXT_PUBLIC_API_URL is required outside development/test");
  }
  return trimmed.endsWith("/api/v2") ? trimmed : `${trimmed}/api/v2`;
}

const apiBaseUrl = normalizeApiBaseUrl(process.env.NEXT_PUBLIC_API_URL);

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  outputFileTracingRoot: __dirname,
  // PPR remains disabled — re-evaluate after stable Next.js support (FE-SPIKE-003)
  // experimental: { ppr: true }, // DO NOT ENABLE
  // Allow HMR WebSocket connections from 127.0.0.1 (used by Playwright E2E tests)
  allowedDevOrigins: ["127.0.0.1"],
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/v2/:path*",
        destination: `${apiBaseUrl}/:path*`,
      },
    ];
  },
};

module.exports = withSerwist(withBundleAnalyzer(nextConfig));
