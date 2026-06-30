"use server";

import "server-only";

import { randomUUID } from "node:crypto";

import type { ShellDataSource } from "@/lib/learner/server-loaders";

export interface LessonCompletionRequest {
  lessonId: string;
  learnerId: string;
  xpAward: number;
}

export interface LessonCompletionResponse {
  lessonId: string;
  learnerId: string;
  xpAward: number;
  auditEventId: string;
  completedAt: string;
  completionStatus: "completed";
  xpStatus: "awarded";
  source: ShellDataSource;
}

export async function completeLessonTransaction(payload: LessonCompletionRequest): Promise<LessonCompletionResponse> {
  // Fixture-backed handler standing in for transactional completion + XP boundary.
  await new Promise((resolve) => setTimeout(resolve, 250));

  return {
    lessonId: payload.lessonId,
    learnerId: payload.learnerId,
    xpAward: payload.xpAward,
    auditEventId: randomUUID(),
    completedAt: new Date().toISOString(),
    completionStatus: "completed",
    xpStatus: "awarded",
    source: "fixture",
  };
}
