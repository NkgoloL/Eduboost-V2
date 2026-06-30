/**
 * app/frontend/src/app/(dashboard)/admin/roadmap/page.tsx
 *
 * Admin-only route: /admin/roadmap
 *
 * This is a Server Component shell — LessonRoadmap is "use client" and
 * handles its own interactivity. No props need to flow down from the server.
 *
 * Access control
 * ──────────────
 * Protect this route at two levels:
 *   1. middleware.ts — redirect unauthenticated users to /login
 *   2. here — check the session role; redirect non-admins to /dashboard
 *
 * When your auth layer is ready, uncomment the role-check block below.
 */

import type { Metadata } from "next";
import { redirect } from "next/navigation";
import LessonRoadmap from "@/components/eduboost/LessonRoadmap";

// Uncomment when your session helper is in place:
// import { getServerSession } from "@/lib/auth/session";

export const metadata: Metadata = {
  title: "Lesson generation roadmap — EduBoost admin",
  description:
    "Tracks the path from 14 approved items to a production-grade CAPS item bank.",
};

export default async function RoadmapPage() {
  // ── Role guard (uncomment when auth is wired up) ──────────────────────────
  // const session = await getServerSession();
  // if (!session) redirect("/login?redirect=/admin/roadmap");
  // if (session.user.role !== "admin") redirect("/dashboard");
  // ─────────────────────────────────────────────────────────────────────────

  return <LessonRoadmap />;
}
