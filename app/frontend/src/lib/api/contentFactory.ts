import { fetchApi } from "./client";

export type ContentScope = {
  scope_id: string;
  grade: number;
  subject_code: string;
  subject: string;
  language: string;
  curriculum: string;
  status: string;
  caps_refs: string[];
};

export type ScopeCoverageReport = {
  scope_id: string;
  summary: Record<string, number>;
  layers: Record<string, { target_total: number; approved_total: number; coverage_ratio: number }>;
};

export type GenerationRun = {
  run_id: string;
  scope_id: string;
  status: string;
  requested_by?: string | null;
  run_metadata: Record<string, unknown>;
};


export type GenerationTask = {
  task_id: string;
  run_id: string;
  scope_id: string;
  caps_ref?: string | null;
  content_layer: string;
  status: string;
  attempt_number: number;
  max_attempts: number;
  output_artifact_ids: string[];
  validation_failures: string[];
};

export type GenerationPlanResponse = {
  run_id: string;
  created_task_ids: string[];
  skipped: Array<Record<string, unknown>>;
  missing: Array<Record<string, unknown>>;
};

export type GenerationExecutionResponse = {
  run_id?: string | null;
  task_id?: string | null;
  status: string;
  artifact_ids: string[];
  errors: string[];
  summary: Record<string, unknown>;
  provider?: string | null;
  mode?: string | null;
};

export type GenerationExecutionReport = {
  run_id: string;
  status: string;
  tasks: number;
  queued: number;
  succeeded: number;
  failed: number;
  skipped: number;
  artifacts: number;
};


export type ReviewQueueItem = {
  artifact_id: string;
  scope_id: string;
  content_layer: string;
  artifact_type: string;
  caps_ref?: string | null;
  status: string;
  risk_level: string;
  risk_reasons: string[];
  validation_status: string;
  provenance_status: string;
  reviewer_id?: string | null;
};

export type ReviewQueuePage = {
  items: ReviewQueueItem[];
  total: number;
  limit: number;
  offset: number;
};

export type ReviewBundle = {
  artifact: Record<string, unknown>;
  validation_report?: Record<string, unknown> | null;
  provenance: Record<string, unknown>;
  sources: Array<Record<string, unknown>>;
  review_risk: { level: string; score: number; reasons: string[] };
  generation_metadata: Record<string, unknown>;
  prior_review_events: Array<Record<string, unknown>>;
};

export type BulkReviewResponse = {
  status: string;
  artifact_ids: string[];
  errors: string[];
  summary: Record<string, number>;
};

export type ReviewerWorkload = {
  reviewer_id: string;
  assigned: number;
  in_review: number;
  overdue: number;
  total_open: number;
};

export type ContentArtifact = {
  artifact_id: string;
  scope_id: string;
  content_layer: string;
  artifact_type: string;
  caps_ref?: string | null;
  status: string;
};


export type ScopeBlocker = {
  code: string;
  severity: "info" | "warning" | "blocking";
  layer?: string | null;
  caps_ref?: string | null;
  required?: number | null;
  approved?: number | null;
  pending_review?: number | null;
};

export type LayerReadinessSummary = {
  layer: string;
  caps_ref: string;
  target: number;
  approved: number;
  pending_review: number;
  generated: number;
  validation_failed: number;
  rejected: number;
  quarantined: number;
  seeded_staging: number;
  promoted_production: number;
  stageable: number;
  status: string;
};

export type ScopeStagingVerificationReport = {
  scope_id: string;
  status: string;
  can_seed_staging: boolean;
  can_promote_production: boolean;
  blockers: ScopeBlocker[];
  layers: LayerReadinessSummary[];
  summary: Record<string, number | string | boolean>;
};

export type AllScopeStagingVerificationReport = {
  run_id?: string | null;
  status: string;
  can_seed_staging: boolean;
  can_promote_production: boolean;
  scopes: ScopeStagingVerificationReport[];
  summary: Record<string, number | string | boolean>;
  created_by?: string | null;
  created_at: string;
};

export type StagingSeedPlan = {
  scope_id: string;
  layers: string[];
  seedable_count: number;
  skipped_count: number;
  skipped: Array<{ artifact_id: string; reason: string }>;
};

export type StagingSeedRun = {
  seed_run_id: string;
  scope_id: string;
  status: string;
  seeded_count: number;
  skipped_count: number;
  errors: string[];
};

export type StagingSeedRunPage = {
  items: StagingSeedRun[];
  total: number;
  limit: number;
  offset: number;
};

export type StagingSeedItem = {
  id: string;
  seed_run_id: string;
  artifact_id: string;
  scope_id: string;
  caps_ref?: string | null;
  layer: string;
  artifact_type: string;
  target_table: string;
  target_record_id?: string | null;
  status: string;
  skip_reason?: string | null;
  seed_payload_hash?: string | null;
};

export type StagingReadVerification = {
  seed_run_id?: string | null;
  scope_id?: string | null;
  passed: boolean;
  verified_count?: number | null;
  staged_artifacts_count?: number | null;
  errors: string[];
};

export type StagingRollback = {
  seed_run_id: string;
  status: string;
  rolled_back_count: number;
};

export type ProductionGateBlocker = {
  type: string;
  message: string;
  artifact_id?: string | null;
  caps_ref?: string | null;
};

export type ProductionGateReport = {
  scope_id: string;
  status: string;
  blockers: ProductionGateBlocker[];
  coverage_summary: Record<string, unknown>;
  staging_summary: Record<string, unknown>;
};

export type ProductionPromotionPlan = {
  scope_id: string;
  layers: string[];
  promotable_count: number;
  skipped_count: number;
  skipped: Array<Record<string, unknown>>;
};

export type ProductionPromotionRequest = {
  layers?: string[] | null;
  confirmation: string;
};

export type ProductionPromotionResult = {
  promotion_event_id: string;
  scope_id: string;
  status: string;
  promoted_count: number;
  skipped_count: number;
  errors: string[];
};

export type ProductionPromotionPage = {
  items: ProductionPromotionResult[];
  total: number;
  limit: number;
  offset: number;
};

export type ProductionReadVerificationReport = {
  promotion_event_id: string;
  passed: boolean;
  verified_count: number;
  errors: string[];
};

export type ScopeProductionReadReport = {
  scope_id: string;
  passed: boolean;
  production_artifacts_count: number;
  errors: string[];
};

export type ProductionRollbackRequest = {
  reason: string;
};

export type ProductionRollbackResult = {
  promotion_event_id: string;
  status: string;
  rolled_back_count: number;
};

export type EtlStatus = {
  status: string;
  documents_indexed?: number;
  mcp_runtime_imported?: boolean;
};

export function fetchContentFactoryScopes() {
  return fetchApi<ContentScope[]>("/admin/content-factory/scopes");
}

export function fetchContentFactoryCoverage(scopeId: string) {
  return fetchApi<ScopeCoverageReport>(`/admin/content-factory/scopes/${scopeId}/coverage`);
}

export function fetchContentFactoryRuns() {
  return fetchApi<GenerationRun[]>("/admin/content-factory/runs");
}

export function fetchContentFactoryReviewQueue(params: Record<string, string> = {}) {
  const query = new URLSearchParams(params).toString();
  return fetchApi<ReviewQueuePage>(`/admin/content-factory/review-queue${query ? `?${query}` : ""}`);
}

export function fetchReviewBundle(artifactId: string) {
  return fetchApi<ReviewBundle>(`/admin/content-factory/artifacts/${artifactId}/review-bundle`);
}

export function bulkApproveReview(artifactIds: string[], notes: string) {
  return fetchApi<BulkReviewResponse>("/admin/content-factory/review/bulk-approve", {
    method: "POST",
    body: JSON.stringify({ artifact_ids: artifactIds, notes }),
  });
}

export function bulkRejectReview(artifactIds: string[], reason: string) {
  return fetchApi<BulkReviewResponse>("/admin/content-factory/review/bulk-reject", {
    method: "POST",
    body: JSON.stringify({ artifact_ids: artifactIds, reason }),
  });
}

export function bulkQuarantineReview(artifactIds: string[], reason: string) {
  return fetchApi<BulkReviewResponse>("/admin/content-factory/review/bulk-quarantine", {
    method: "POST",
    body: JSON.stringify({ artifact_ids: artifactIds, reason }),
  });
}

export function assignReviewBatch(artifactIds: string[], reviewerId: string) {
  return fetchApi<BulkReviewResponse>("/admin/content-factory/review-assignments/bulk", {
    method: "POST",
    body: JSON.stringify({ artifact_ids: artifactIds, reviewer_id: reviewerId }),
  });
}

export function fetchReviewerWorkload(reviewerId: string) {
  return fetchApi<ReviewerWorkload>(`/admin/content-factory/reviewers/${reviewerId}/workload`);
}

export function fetchAdminEtlStatus() {
  return fetchApi<EtlStatus>("/admin/etl/status");
}


export function runAllScopeStagingVerification() {
  return fetchApi<AllScopeStagingVerificationReport>("/admin/content-factory/staging-verification/all-scopes", {
    method: "POST",
  });
}

export function fetchScopeStagingReadiness(scopeId: string) {
  return fetchApi<ScopeStagingVerificationReport>(`/admin/content-factory/scopes/${scopeId}/staging-readiness`);
}

export function dryRunStagingSeed(scopeId: string) {
  return fetchApi<StagingSeedPlan>(`/admin/content-factory/scopes/${scopeId}/dry-run-seed`, { method: "POST" });
}

export function seedStaging(scopeId: string, allowPartial = true) {
  return fetchApi<StagingSeedRun>(`/admin/content-factory/scopes/${scopeId}/seed-staging?allow_partial=${String(allowPartial)}`, {
    method: "POST",
  });
}

export function fetchStagingSeedRuns(scopeId?: string) {
  const query = scopeId ? `?scope_id=${encodeURIComponent(scopeId)}` : "";
  return fetchApi<StagingSeedRunPage>(`/admin/content-factory/seed-runs${query}`);
}

export function fetchStagingSeedRunItems(seedRunId: string) {
  return fetchApi<StagingSeedItem[]>(`/admin/content-factory/seed-runs/${seedRunId}/items`);
}

export function verifyStagingSeedRun(seedRunId: string) {
  return fetchApi<StagingReadVerification>(`/admin/content-factory/seed-runs/${seedRunId}/verify`, { method: "POST" });
}

export function verifyScopeStagingRead(scopeId: string) {
  return fetchApi<StagingReadVerification>(`/admin/content-factory/scopes/${scopeId}/staging-read-verification`);
}

export function rollbackStagingSeedRun(seedRunId: string, reason: string) {
  return fetchApi<StagingRollback>(`/admin/content-factory/seed-runs/${seedRunId}/rollback?reason=${encodeURIComponent(reason)}`, {
    method: "POST",
  });
}

export function fetchProductionGate(scopeId: string, layers?: string[] | null) {
  const query = layers ? `?layers=${layers.join(",")}` : "";
  return fetchApi<ProductionGateReport>(`/admin/content-factory/scopes/${scopeId}/production-gate${query}`);
}

export function dryRunProductionPromotion(scopeId: string, layers?: string[] | null) {
  const query = layers ? `?layers=${layers.join(",")}` : "";
  return fetchApi<ProductionPromotionPlan>(`/admin/content-factory/scopes/${scopeId}/dry-run-promotion${query}`, { method: "POST" });
}

export function promoteProduction(scopeId: string, request: ProductionPromotionRequest) {
  return fetchApi<ProductionPromotionResult>(`/admin/content-factory/scopes/${scopeId}/promote-production`, {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export function fetchPromotionEvents(scopeId?: string | null, limit = 50, offset = 0) {
  const params = new URLSearchParams();
  if (scopeId) params.set("scope_id", scopeId);
  params.set("limit", String(limit));
  params.set("offset", String(offset));
  const query = params.toString();
  return fetchApi<ProductionPromotionPage>(`/admin/content-factory/promotion-events${query ? `?${query}` : ""}`);
}

export function fetchPromotionEvent(promotionEventId: string) {
  return fetchApi<ProductionPromotionResult>(`/admin/content-factory/promotion-events/${promotionEventId}`);
}

export function fetchPromotionEventItems(promotionEventId: string) {
  return fetchApi<{ items: Array<Record<string, unknown>>; total: number }>(`/admin/content-factory/promotion-events/${promotionEventId}/items`);
}

export function verifyPromotionEvent(promotionEventId: string) {
  return fetchApi<ProductionReadVerificationReport>(`/admin/content-factory/promotion-events/${promotionEventId}/verify`, { method: "POST" });
}

export function rollbackPromotionEvent(promotionEventId: string, reason: string) {
  return fetchApi<ProductionRollbackResult>(`/admin/content-factory/promotion-events/${promotionEventId}/rollback`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function verifyScopeProductionRead(scopeId: string, layers?: string[] | null) {
  const query = layers ? `?layers=${layers.join(",")}` : "";
  return fetchApi<ScopeProductionReadReport>(`/admin/content-factory/scopes/${scopeId}/production-read-verification${query}`);
}

export type StagingArtifactPreview = {
  artifact_id: string;
  scope_id: string;
  caps_ref: string | null;
  layer: string;
  artifact_type: string;
  staging_status: string;
  learner_visible: boolean;
  seed_run_id: string | null;
  seed_run_status: string | null;
  verification_passed: boolean | null;
  payload: Record<string, unknown>;
  source_artifact_hash: string;
  created_at: string;
};

export type StagingPreviewReport = {
  scope_id: string;
  layers: string[];
  total_artifacts_count: number;
  active_artifacts_count: number;
  pending_artifacts_count: number;
  learner_visible_count: number;
  artifacts: StagingArtifactPreview[];
};

export type StagingCapsRefPreview = {
  scope_id: string;
  caps_ref: string;
  layers: string[];
  total_artifacts_count: number;
  active_artifacts_count: number;
  learner_visible_count: number;
  artifacts: StagingArtifactPreview[];
};

export type LearnerDiagnosticItem = {
  artifact_id: string;
  scope_id: string;
  caps_ref: string | null;
  grade: number | null;
  subject_code: string | null;
  language: string;
  title: string | null;
  payload: Record<string, unknown>;
  source_artifact_hash: string;
  promotion_event_id: string | null;
  created_at: string;
};

export type LearnerLesson = {
  artifact_id: string;
  scope_id: string;
  caps_ref: string | null;
  grade: number | null;
  subject_code: string | null;
  language: string;
  title: string | null;
  payload: Record<string, unknown>;
  source_artifact_hash: string;
  promotion_event_id: string | null;
  created_at: string;
};

export type LearnerScopeContentSummary = {
  scope_id: string;
  diagnostic_items_count: number;
  lessons_count: number;
  total_artifacts_count: number;
  last_promotion_at: string | null;
};

export function fetchStagingPreview(scopeId: string, layers?: string[] | null) {
  const query = layers ? `?layers=${layers.join(",")}` : "";
  return fetchApi<StagingPreviewReport>(`/admin/content-factory/staging-preview/scopes/${scopeId}${query}`);
}

export function fetchStagingPreviewByCapsRef(scopeId: string, capsRef: string, layers?: string[] | null) {
  const query = layers ? `?layers=${layers.join(",")}` : "";
  return fetchApi<StagingCapsRefPreview>(`/admin/content-factory/staging-preview/scopes/${scopeId}/caps/${capsRef}${query}`);
}

export function fetchProductionPreview(scopeId: string) {
  return fetchApi<LearnerScopeContentSummary>(`/admin/content-factory/production-preview/scopes/${scopeId}`);
}

export function fetchProductionPreviewByCapsRef(scopeId: string, capsRef: string) {
  return fetchApi<{ diagnostic_items: LearnerDiagnosticItem[]; lessons: LearnerLesson[] }>(`/admin/content-factory/production-preview/scopes/${scopeId}/caps/${capsRef}`);
}


// ── Full Generation Run API ─────────────────────────────────────────────────────

export type FullGenerationPlanResponse = {
  run_id: string;
  created_task_ids: string[];
  skipped: Array<Record<string, unknown>>;
  missing: Array<Record<string, unknown>>;
};

export type FullGenerationRunsResponse = {
  items: GenerationRun[];
  total: number;
};

export type FullGenerationRunReport = {
  run_id: string;
  status: string;
  metadata: Record<string, unknown>;
};

export function planFullGeneration() {
  return fetchApi<FullGenerationPlanResponse>("/admin/content-factory/full-generation/plan", { method: "POST" });
}

export function startFullGeneration(runId: string, confirmation: string) {
  return fetchApi<{ run_id: string; status: string }>("/admin/content-factory/full-generation/start", {
    method: "POST",
    body: JSON.stringify({ run_id: runId, confirmation }),
  });
}

export function listFullGenerationRuns() {
  return fetchApi<FullGenerationRunsResponse>("/admin/content-factory/full-generation/runs");
}

export function getFullGenerationRun(runId: string) {
  return fetchApi<GenerationRun>(`/admin/content-factory/full-generation/runs/${runId}`);
}

export function getFullGenerationRunReport(runId: string) {
  return fetchApi<FullGenerationRunReport>(`/admin/content-factory/full-generation/runs/${runId}/report`);
}

export function cancelFullGenerationRun(runId: string) {
  return fetchApi<{ run_id: string; status: string }>(`/admin/content-factory/full-generation/runs/${runId}/cancel`, { method: "POST" });
}

export function resumeFullGenerationRun(runId: string) {
  return fetchApi<{ run_id: string; status: string }>(`/admin/content-factory/full-generation/runs/${runId}/resume`, { method: "POST" });
}


export function fetchGenerationRunTasks(runId: string) {
  return fetchApi<GenerationTask[]>(`/admin/content-factory/runs/${runId}/tasks`);
}

export function planMissingGenerationTasks(runId: string) {
  return fetchApi<GenerationPlanResponse>(`/admin/content-factory/runs/${runId}/plan-missing`, { method: "POST" });
}

export function executeGenerationRun(runId: string) {
  return fetchApi<GenerationExecutionResponse>(`/admin/content-factory/runs/${runId}/execute`, { method: "POST" });
}

export function executeGenerationTask(taskId: string) {
  return fetchApi<GenerationExecutionResponse>(`/admin/content-factory/tasks/${taskId}/execute`, { method: "POST" });
}

export function fetchGenerationExecutionReport(runId: string) {
  return fetchApi<GenerationExecutionReport>(`/admin/content-factory/runs/${runId}/execution-report`);
}
