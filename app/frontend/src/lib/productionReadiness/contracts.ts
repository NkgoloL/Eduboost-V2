export type FrontendEnvironmentName = "development" | "test" | "staging" | "production";
export type RouteRole = "anonymous" | "learner" | "guardian" | "teacher" | "admin";
export type RouteGuardState = "public" | "authenticated" | "role-restricted" | "forbidden" | "unauthorized";
export type UxPriority = "P0" | "P1" | "P2";

export interface FrontendPublicEnvContract {
  key: "NEXT_PUBLIC_API_URL" | "NEXT_PUBLIC_APP_ENV" | "NEXT_PUBLIC_ENABLE_DEV_SESSION";
  browserSafe: boolean;
  requiredIn: FrontendEnvironmentName[];
  description: string;
}

export interface CanonicalEnvelopeClientContract {
  consumesCanonicalEnvelope: true;
  normalizesErrorEnvelope: true;
  propagatesRequestId: true;
  storesAuthTokenClientSide: true;
  refreshesExpiredSession: true;
  parsesTypedResponses: true;
  retriesIdempotentReads: true;
  detectsOfflineNetworkState: true;
  handlesStaleData: true;
}

export interface FrontendRouteGuardContract {
  route: string;
  guard: RouteGuardState;
  allowedRoles: RouteRole[];
  unauthorizedState: string;
  forbiddenState: string;
  redirectRule: string;
}

export interface FrontendUxCapability {
  key: string;
  priority: UxPriority;
  area: "auth-onboarding" | "learner" | "parent-guardian" | "teacher-admin" | "accessibility-mobile" | "pwa-low-data";
  repositoryEvidence: string;
  acceptanceSignal: string;
}

export const PUBLIC_FRONTEND_ENV_CONTRACT: FrontendPublicEnvContract[] = [
  {
    key: "NEXT_PUBLIC_API_URL",
    browserSafe: true,
    requiredIn: ["development", "test", "staging", "production"],
    description: "Safe public API base URL for the canonical /api/v2 backend.",
  },
  {
    key: "NEXT_PUBLIC_APP_ENV",
    browserSafe: true,
    requiredIn: ["staging", "production"],
    description: "Browser-safe deployment environment name used for telemetry and environment banners.",
  },
  {
    key: "NEXT_PUBLIC_ENABLE_DEV_SESSION",
    browserSafe: true,
    requiredIn: ["development", "test"],
    description: "Development-only session bootstrap flag. It must not be enabled in production.",
  },
];

export const SERVER_SECRET_ENV_DENYLIST_PATTERNS = [
  "SECRET",
  "TOKEN",
  "PRIVATE",
  "PASSWORD",
  "DATABASE_URL",
  "REDIS_URL",
  "STRIPE_SECRET",
  "SUPABASE_SERVICE_ROLE",
];

export const API_CLIENT_PRODUCTION_CONTRACT: CanonicalEnvelopeClientContract = {
  consumesCanonicalEnvelope: true,
  normalizesErrorEnvelope: true,
  propagatesRequestId: true,
  storesAuthTokenClientSide: true,
  refreshesExpiredSession: true,
  parsesTypedResponses: true,
  retriesIdempotentReads: true,
  detectsOfflineNetworkState: true,
  handlesStaleData: true,
};

export const ROUTE_GUARD_MATRIX: FrontendRouteGuardContract[] = [
  {
    route: "/dashboard",
    guard: "authenticated",
    allowedRoles: ["learner"],
    unauthorizedState: "redirect to /login with session-expired message",
    forbiddenState: "show learner forbidden state",
    redirectRule: "guardian, teacher, and admin users must be routed to their own dashboards",
  },
  {
    route: "/parent-dashboard",
    guard: "authenticated",
    allowedRoles: ["guardian"],
    unauthorizedState: "redirect to /login with guardian context",
    forbiddenState: "show guardian forbidden state",
    redirectRule: "learner users must be routed to /dashboard",
  },
  {
    route: "/teacher-dashboard",
    guard: "role-restricted",
    allowedRoles: ["teacher"],
    unauthorizedState: "redirect to /login",
    forbiddenState: "show teacher feature not in beta scope unless enabled",
    redirectRule: "non-teacher users must be denied",
  },
  {
    route: "/admin-dashboard",
    guard: "role-restricted",
    allowedRoles: ["admin"],
    unauthorizedState: "redirect to /login",
    forbiddenState: "show admin feature not in beta scope unless enabled",
    redirectRule: "non-admin users must be denied",
  },
];

export const FRONTEND_UX_CAPABILITIES: FrontendUxCapability[] = [
  { key: "guardian signup screen", priority: "P0", area: "auth-onboarding", repositoryEvidence: "app/frontend/src/app/(auth)/register/page.tsx", acceptanceSignal: "signup form has accessible labels, validation, and canonical error display" },
  { key: "guardian login screen", priority: "P0", area: "auth-onboarding", repositoryEvidence: "app/frontend/src/app/(auth)/login/page.tsx", acceptanceSignal: "login form handles auth success, failure, and session-expiry messaging" },
  { key: "logout UX", priority: "P0", area: "auth-onboarding", repositoryEvidence: "app/frontend/src/lib/api/client.ts", acceptanceSignal: "stored tokens are cleared and user is routed to login" },
  { key: "session-expiry UX", priority: "P0", area: "auth-onboarding", repositoryEvidence: "app/frontend/src/lib/api/client.ts", acceptanceSignal: "401 responses trigger refresh or user-visible expiry state" },
  { key: "password reset request screen", priority: "P0", area: "auth-onboarding", repositoryEvidence: "docs/frontend/production_auth_onboarding_ux_contract.md", acceptanceSignal: "reset request contract is documented for implementation and testing" },
  { key: "password reset completion screen", priority: "P0", area: "auth-onboarding", repositoryEvidence: "docs/frontend/production_auth_onboarding_ux_contract.md", acceptanceSignal: "reset completion contract is documented for implementation and testing" },
  { key: "email verification UX", priority: "P0", area: "auth-onboarding", repositoryEvidence: "docs/frontend/production_auth_onboarding_ux_contract.md", acceptanceSignal: "verification state contract is documented for implementation and testing" },
  { key: "learner profile creation", priority: "P0", area: "auth-onboarding", repositoryEvidence: "app/frontend/src/context/LearnerContext.tsx", acceptanceSignal: "learner context supports active learner and profile data" },
  { key: "grade selection", priority: "P0", area: "auth-onboarding", repositoryEvidence: "app/frontend/src/components/eduboost/EntryScreens.tsx", acceptanceSignal: "grade is captured before learner journey starts" },
  { key: "subject selection", priority: "P0", area: "auth-onboarding", repositoryEvidence: "app/frontend/src/components/eduboost/EntryScreens.tsx", acceptanceSignal: "subject selection is represented in learner entry flow" },
  { key: "parental consent capture", priority: "P0", area: "auth-onboarding", repositoryEvidence: "app/frontend/src/app/(learner)/parent/page.tsx", acceptanceSignal: "consent route and parent flow are represented" },
  { key: "onboarding completion route", priority: "P0", area: "auth-onboarding", repositoryEvidence: "docs/frontend/production_auth_onboarding_ux_contract.md", acceptanceSignal: "completion route contract is documented for implementation and testing" },
  { key: "learner dashboard", priority: "P0", area: "learner", repositoryEvidence: "app/frontend/src/app/(learner)/dashboard/page.tsx", acceptanceSignal: "dashboard route renders learner summary" },
  { key: "study plan", priority: "P0", area: "learner", repositoryEvidence: "app/frontend/src/app/(learner)/plan/page.tsx", acceptanceSignal: "study plan route exists and is covered by journey evidence" },
  { key: "diagnostic question display", priority: "P0", area: "learner", repositoryEvidence: "app/frontend/src/app/(learner)/diagnostic/page.tsx", acceptanceSignal: "diagnostic route and interactive diagnostic component exist" },
  { key: "lesson explanation view", priority: "P0", area: "learner", repositoryEvidence: "app/frontend/src/app/(learner)/lesson/page.tsx", acceptanceSignal: "lesson route and interactive lesson component exist" },
  { key: "parent dashboard", priority: "P0", area: "parent-guardian", repositoryEvidence: "app/frontend/src/app/(parent)/parent-dashboard/page.tsx", acceptanceSignal: "parent dashboard route exists" },
  { key: "privacy controls", priority: "P0", area: "parent-guardian", repositoryEvidence: "docs/frontend/production_parent_privacy_controls_contract.md", acceptanceSignal: "export, erasure, correction, and restriction flows are documented" },
  { key: "teacher dashboard beta scope", priority: "P1", area: "teacher-admin", repositoryEvidence: "docs/frontend/production_teacher_admin_scope_contract.md", acceptanceSignal: "teacher beta scope is explicitly gated" },
  { key: "admin console beta scope", priority: "P1", area: "teacher-admin", repositoryEvidence: "docs/frontend/production_teacher_admin_scope_contract.md", acceptanceSignal: "admin beta scope is explicitly gated" },
  { key: "WCAG 2.1 AA accessibility", priority: "P0", area: "accessibility-mobile", repositoryEvidence: "docs/frontend/frontend_accessibility_contract.md", acceptanceSignal: "keyboard, contrast, labels, headings, landmarks, and screen-reader states are documented" },
  { key: "mobile learner and parent flows", priority: "P0", area: "accessibility-mobile", repositoryEvidence: "docs/frontend/production_frontend_ux_accessibility_mobile_contract.md", acceptanceSignal: "responsive and mobile constraints are documented" },
  { key: "PWA service worker and manifest", priority: "P1", area: "pwa-low-data", repositoryEvidence: "app/frontend/src/components/ServiceWorkerRegistration.tsx", acceptanceSignal: "service worker registration exists and PWA contract is documented" },
  { key: "low-data and offline messaging", priority: "P1", area: "pwa-low-data", repositoryEvidence: "app/frontend/src/lib/api/offlineSync.ts", acceptanceSignal: "offline sync and low-data expectations are documented" },
];

export function findUxCapability(key: string): FrontendUxCapability | undefined {
  return FRONTEND_UX_CAPABILITIES.find((capability) => capability.key === key);
}

export function publicEnvKeys(): string[] {
  return PUBLIC_FRONTEND_ENV_CONTRACT.map((entry) => entry.key);
}

export function routeRequiresRole(route: string, role: RouteRole): boolean {
  const entry = ROUTE_GUARD_MATRIX.find((candidate) => candidate.route === route);
  return Boolean(entry && entry.allowedRoles.includes(role));
}
