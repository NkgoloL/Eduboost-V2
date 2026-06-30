# FE-SPIKE-006 — Service Worker + App Router Cache Interaction Spike

## Objective
Determine the service worker toolchain, cache boundaries, and POPIA offline-audit guardrails for EduBoost's RC4 offline/PWA implementation.

## Toolchain Evaluation

### Options Considered
1. **next-pwa** - Last published 4 years ago (2022), not actively maintained, incompatible with Next.js 15/Turbopack
2. **Raw Workbox** - Manual build process with esbuild/tsx, maximum control but high complexity
3. **Serwist** - Successor to next-pwa, actively maintained, has @serwist/next for Next.js integration

### Recommendation: Serwist

**Rationale:**
- Active maintenance and modern codebase (2024-2026 updates)
- `@serwist/next` provides Next.js-specific integration
- Handles build-time plumbing: precache manifest injection, public/sw.js generation
- Workbox-compatible (fork of Workbox, familiar patterns)
- Community examples for Next.js 14+ App Router
- Supports Turbopack (unlike next-pwa)

**Installation:**
```bash
pnpm add serwist @serwist/next
```

**Configuration (next.config.ts):**
```typescript
import withSerwist from "@serwist/next";

const nextConfig = {
  // existing config
};

export default withSerwist(nextConfig, {
  swSrc: "src/app/sw.ts",
  swDest: "public/sw.js",
  disable: process.env.NODE_ENV === "development",
});
```

## Cache Boundaries

### Safe to Cache (Static Assets)
- JavaScript bundles (chunks)
- CSS files
- Images from public/ folder
- Font files
- Manifest.json
- Static HTML pages (login, register, onboarding)

### Safe to Cache (Public Routes)
- `/` - Landing page
- `/login` - Login page
- `/register` - Registration page
- `/onboarding` - Onboarding flow
- `/auth/verify-email` - Email verification
- `/auth/reset-password` - Password reset

### NOT Safe to Cache (Authenticated Routes)
- `/dashboard` - Learner dashboard (personalized data)
- `/lesson` - Lesson pages (learner-specific progress)
- `/diagnostic` - Diagnostic assessment (learner-specific)
- `/plan` - Learning plan (personalized)
- `/badges` - User achievements (personalized)
- `/settings/privacy` - Privacy settings (sensitive)
- `/parent-dashboard` - Guardian portal (sensitive learner data)
- `/parent` - Learner invite flow (contains learner ID)

### Cache Strategy

**Static Assets:** CacheFirst with expiration
```typescript
{
  urlPattern: /^https?.*/,
  handler: new CacheFirst({
    cacheName: "static-assets",
    plugins: [
      new ExpirationPlugin({
        maxEntries: 1000,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
      }),
    ],
  }),
}
```

**Public Routes:** NetworkFirst with fallback
```typescript
{
  urlPattern: ({ request, url }) => {
    return request.mode === "navigate" && 
           ["/", "/login", "/register", "/onboarding"].includes(url.pathname);
  },
  handler: new NetworkFirst({
    cacheName: "public-pages",
    networkTimeoutSeconds: 3,
  }),
}
```

**Authenticated Routes:** NetworkOnly (no caching)
```typescript
{
  urlPattern: ({ request, url }) => {
    return request.mode === "navigate" && 
           ["/dashboard", "/lesson", "/diagnostic", "/plan", "/badges", "/settings", "/parent-dashboard", "/parent"].some(path => url.pathname.startsWith(path));
  },
  handler: new NetworkOnly(),
}
```

**API Routes:** NetworkOnly (no caching)
```typescript
{
  urlPattern: ({ url }) => url.pathname.startsWith("/api/"),
  handler: new NetworkOnly(),
}
```

## Authenticated Route Protection

### Risk Assessment
Caching authenticated content can expose user data to other users on shared devices. Service workers must never cache:
- User-specific HTML responses
- API responses containing personal data
- Session tokens or authentication state

### Protection Strategy
1. **Service worker check:** Verify session cookie presence before serving cached content
2. **Route-based exclusion:** Explicitly exclude authenticated routes from cache
3. **Cache-busting headers:** Use `Cache-Control: no-store` for authenticated responses
4. **Middleware validation:** Ensure middleware validates auth before service worker intercepts

### Implementation
```typescript
// In service worker
const isAuthRoute = (url: URL) => {
  const authPaths = ["/dashboard", "/lesson", "/diagnostic", "/plan", "/badges", "/settings", "/parent-dashboard", "/parent"];
  return authPaths.some(path => url.pathname.startsWith(path));
};

if (isAuthRoute(url)) {
  return new NetworkOnly();
}
```

## Offline Lesson Shell Caching

### Decision: Safe with Guardrails

**What can be cached offline:**
- Lesson content structure (static lesson metadata)
- Question text (non-personalized)
- Assessment framework
- Learning objectives

**What cannot be cached offline:**
- Learner progress data
- Assessment responses
- Personalized recommendations
- AI-generated feedback

**Guardrails:**
1. Lesson shell cached as static HTML with placeholders for dynamic content
2. Offline mode shows "Offline - progress will sync when connected" banner
3. No assessment submission allowed offline (must be online)
4. Read-only lesson viewing only offline

## Progress Queue Boundary

### Decision: Technically Viable with POPIA Constraints

**Technical Approach:**
- IndexedDB for local progress queue
- Background sync API for automatic replay when online
- Conflict resolution: server timestamp wins

**POPIA Constraints:**
- Every offline progress event must generate an audit event ID
- Audit trail must be replayable with timestamps
- No personal data processed without consent
- Information Officer must have visibility into offline processing

**Queue Structure:**
```typescript
interface QueuedProgressEvent {
  eventId: string; // UUID for audit trail
  timestamp: string; // ISO 8601
  learnerId: string;
  eventType: "lesson_complete" | "question_answered" | "streak_update";
  payload: unknown; // Event-specific data
  consentVersion: string; // Link to consent at time of event
}
```

## POPIA Offline Audit Replay Guardrails

### Decision: Audit Replay DISABLED until Explicit Approval

**Rationale:**
- POPIA requires continuous audit trail visibility
- Offline processing breaks real-time audit visibility
- Information Officer cannot monitor offline events
- Risk of audit trail gaps during extended offline periods
- No legal precedent for offline audit replay in SA

**Guardrails if Approved Later:**
1. **Audit event generation:** Every offline action generates UUID before queueing
2. **Timestamp preservation:** Client timestamp recorded, server timestamp on sync
3. **Consent linkage:** Each event linked to consent version at time of action
4. **Replay transparency:** Sync process logs all replayed audit events
5. **Information Officer access:** Offline audit log viewable via admin dashboard
6. **Data minimization:** Only essential progress data queued, no sensitive content
7. **Expiration:** Queued events expire after 7 days if not synced

**Current Decision:**
- Offline progress queue DISABLED
- Offline lesson viewing only (read-only)
- No assessment submission offline
- All progress requires online connection
- Audit trail remains real-time and continuous

## Implementation Recommendations

### Phase 1: PWA Shell (FE-PR-010)
1. Install Serwist and configure @serwist/next
2. Generate manifest.json with app metadata
3. Add PWA install prompt UI
4. Implement static asset caching
5. Implement public route caching
6. Add offline fallback page for public routes

### Phase 2: Offline Lesson Shell (FE-PR-011 - Partial)
1. Cache lesson content structure (static metadata)
2. Add offline banner indicator
3. Disable assessment submission offline
4. Read-only lesson viewing offline
5. **DO NOT implement progress queue**

### Phase 3: Loadshedding UI
1. Detect network connectivity status
2. Show "Loadshedding mode" banner when offline
3. Display cached content when available
4. Show "Reconnect to continue" for authenticated routes

### Phase 4: Progress Queue (BLOCKED - Requires POPIA Approval)
1. Implement IndexedDB queue
2. Add background sync
3. Implement conflict resolution
4. Add audit event generation
5. **ONLY after explicit POPIA/legal approval**

## Security Checklist

- [ ] Service worker never caches authenticated HTML responses
- [ ] Service worker never caches API responses
- [ ] Session cookies not stored in service worker cache
- [ ] Cache-Control headers set correctly for authenticated routes
- [ ] Service worker registration checks for auth state
- [ ] Offline mode clearly indicated to user
- [ ] No sensitive data in IndexedDB without encryption
- [ ] Audit trail remains continuous (no offline replay)

## POPIA Compliance Checklist

- [ ] Information Officer notified of offline capabilities
- [ ] Consent updated to include offline processing (if enabled)
- [ ] Privacy policy updated to explain offline behavior
- [ ] Audit trail gaps documented (if offline replay enabled)
- [ ] Data minimization applied to offline queue
- [ ] Security safeguards maintained offline
- [ ] Data subject rights available offline (export/erasure)

## Next Steps

1. **Review this spike document** with legal/compliance team
2. **Get explicit POPIA approval** for offline audit replay before enabling progress queue
3. **Begin FE-PR-010** (PWA shell) using Serwist
4. **Begin FE-PR-011** (offline lesson shell) without progress queue
5. **Reassess progress queue** after POPIA approval

## Explicit Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Toolchain | Serwist | Active maintenance, Next.js integration, Turbopack compatible |
| Authenticated route caching | NetworkOnly (no cache) | Security: prevent data leakage on shared devices |
| Offline lesson shell | Safe with guardrails | Read-only viewing, no assessment submission |
| Progress queue | DISABLED | POPIA: audit trail continuity, Information Officer visibility |
| Offline audit replay | DISABLED | POPIA: no legal precedent, requires explicit approval |
| PWA install prompt | ENABLED | User experience improvement, low risk |
| Loadshedding UI | ENABLED | South African context, user experience |

## References

- Serwist documentation: https://serwist.pages.dev
- Next.js App Router caching: https://nextjs.org/docs/app/building-your-application/caching
- POPIA Act: https://popia.co.za
- POPIA compliance guides: Qualysec, Securiti, OneTrust
