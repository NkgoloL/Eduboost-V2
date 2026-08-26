# RouteGuard Authentication Flow & Testing

Frontend route protection system using dual-layer authentication: middleware cookie validation for initial request interception, and client-side RouteGuard component for role-based access control distinguishing learner routes (LearnerContext state) from guardian routes (session endpoint validation). Key entry points: [1a] parent route guard, [2a] learner route guard, [6a] test suite setup.

## Trace ID: 1
**Title:** Parent/Guardian Route Authentication Flow

**Description:** Client-side authentication check for guardian routes via session endpoint validation

**Motivation:**
EduBoost Frontend implements a guardian-centric authentication flow where parent/guardian routes require active session validation. The RouteGuard component handles this by calling fetchSessionState() which queries the /api/auth/session endpoint to verify authentication status. This endpoint reads the httpOnly eduboost_session cookie server-side and returns authentication state with claims. The dual-layer approach (middleware + client-side guard) ensures both request-level protection and runtime authorization checks. For guardian routes, the system relies on session cookie presence rather than LearnerContext state, as guardians may not have an active learner selected. This separation allows guardians to access parent-specific routes (dashboard, settings) without requiring a learner context.

**Details:**
- **Session Validation Flow:** RouteGuard mount → useEffect triggers for non-learner routes → fetchSessionState() call → GET /api/auth/session with no-cache policy → Next.js API route handler → getSessionToken() extracts cookie → NextResponse.json() returns {authenticated, claims} → setGuardianAuthenticated() updates state → Component re-renders → useEffect watches !allowed → router.push("/login") for unauthenticated
- **Cookie-Based Authentication:** Session stored in httpOnly eduboost_session cookie, extracted server-side via Next.js cookie store, token presence determines authentication status, claims extracted from JWT payload for role information
- **Concurrent Request Handling:** fetchSessionState() uses active flag to prevent state updates on unmounted components, multiple concurrent requests handled independently, no distributed locks needed as operations are per-component
- **Covered Objects:** RouteGuard component, fetchSessionState() function, /api/auth/session API route, getSessionToken() server helper, httpOnly cookie store, NextResponse, React state (guardianAuthenticated, sessionLoaded), Next.js router
- **Timeouts:** Session fetch: ~100-300ms. Cookie extraction: <5ms. State update: ~1-5ms. Redirect: ~10-50ms. Total guardian auth check: ~111-355ms
- **Error Handling:** Fetch failures return {authenticated: false}. Missing cookie returns false. Network errors logged. All errors fail closed (assume unauthenticated) for security
- **Security Considerations:** httpOnly cookie prevents XSS access. no-cache policy prevents stale responses. Server-side cookie extraction prevents client tampering. Fail-closed error handling. Session validation on every protected route access

**Trace text diagram:**
```
Parent/Guardian Route Authentication Flow
├── RouteGuard component mount <-- RouteGuard.tsx:27
│   └── useEffect for non-learner routes <-- RouteGuard.tsx:35
│       └── fetchSessionState() call <-- 1a
│           └── fetch("/api/auth/session") <-- 1b
│               └── Next.js API route handler <-- route.ts:5
│                   └── GET /api/auth/session
│                       ├── getSessionToken() <-- 1c
│                       │   └── cookies.get() <-- 1d
│                       └── NextResponse.json() <-- 1e
│                           └── { authenticated, claims }
├── Promise resolves with result
│   └── setGuardianAuthenticated() <-- 1f
│       └── Component re-renders
│           └── useEffect watches !allowed <-- RouteGuard.tsx:52
│               └── router.push("/login") <-- 1g
```

**Location ID: 1a**
- **Title:** Trigger session validation
- **Description:** RouteGuard initiates async session check for non-learner routes
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:41

**Location ID: 1b**
- **Title:** Fetch session status
- **Description:** HTTP request to session endpoint with no-cache policy
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:16

**Location ID: 1c**
- **Title:** Read session cookie
- **Description:** Server-side extraction of JWT from httpOnly cookie
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/auth/session/route.ts:6

**Location ID: 1d**
- **Title:** Extract cookie value
- **Description:** Retrieves eduboost_session cookie from Next.js cookie store
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/auth/session.server.ts:21

**Location ID: 1e**
- **Title:** Return auth status
- **Description:** Responds with authentication state based on token presence
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/auth/session/route.ts:8

**Location ID: 1f**
- **Title:** Update auth state
- **Description:** Sets component state triggering re-render with auth result
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:43

**Location ID: 1g**
- **Title:** Redirect unauthenticated
- **Description:** Navigates to login for parent routes or home for other roles
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:54

### AI Guide: Parent/Guardian Route Authentication Flow

**Motivation:**
Guardian route authentication uses session endpoint validation to verify authentication status without requiring learner context. This enables parents/guardians to access protected routes (dashboard, settings) independently of learner selection, using httpOnly cookies for secure session management.

**Details:**

**Session Validation Architecture**
The RouteGuard component triggers session validation on mount for non-learner routes via useEffect [1a]. The fetchSessionState() function makes an HTTP request to /api/auth/session with no-cache policy to prevent stale responses [1b]. The Next.js API route handler processes the GET request server-side [1c].

**Server-Side Cookie Extraction**
The getSessionToken() helper extracts the eduboost_session cookie from the Next.js cookie store [1d]. This server-side extraction prevents client-side tampering and ensures the cookie is httpOnly, protecting against XSS attacks. The route returns authentication status and claims via NextResponse.json() [1e].

**State Management and Redirect**
When the promise resolves, setGuardianAuthenticated() updates component state [1f]. This triggers a re-render, and the redirect useEffect watches the allowed flag [1g]. If authentication fails, the router navigates to /login for parent routes or / for other roles.

**Security Properties**
The system uses httpOnly cookies to prevent XSS access, no-cache policy to prevent stale responses, server-side cookie extraction to prevent tampering, and fail-closed error handling for security. Session validation occurs on every protected route access to ensure current authentication status.

## Trace ID: 2
**Title:** Learner Route Authentication Flow

**Description:** Client-side authentication check for learner routes via LearnerContext state validation

**Motivation:**
EduBoost Frontend implements learner-specific authentication that relies on LearnerContext state rather than session cookies. Learner routes (lesson pages, diagnostic assessments, study plans) require an active learner profile to be selected in the context. This design choice separates learner access from guardian authentication, allowing guardians to manage multiple learners without constantly switching sessions. The RouteGuard component checks the learner object presence from LearnerContext to determine access. If no learner is selected, the user is redirected to the home page where they can select a learner. This approach provides a more granular access control model where learner-specific routes are protected by learner context state, while guardian routes are protected by session authentication.

**Details:**
- **Learner Context Validation:** RouteGuard mount → useLearner() hook call → useContext(LearnerContext) → returns { learner, loading } → compute allowed flag as Boolean(learner) for learner routes → useEffect for session check immediately sets sessionLoaded(true) for learner routes → useEffect for redirect logic checks if (!loading && !allowed) → router.push("/") for unauthorized
- **Context-Based Authorization:** LearnerContext provides global learner state, learner presence determines route access, loading state prevents premature redirects, sessionLoaded flag bypasses guardian session validation for learner routes
- **Concurrent State Updates:** Context updates are batched by React, multiple route guards read same context independently, no distributed locks needed as React handles state synchronization
- **Covered Objects:** RouteGuard component, useLearner() hook, LearnerContext, useContext hook, React state (learner, loading, sessionLoaded, allowed), Next.js router
- **Timeouts:** Context read: <1ms. Allowed computation: <1ms. State update: ~1-5ms. Redirect: ~10-50ms. Total learner auth check: ~12-57ms
- **Error Handling:** Missing learner triggers redirect. Context errors handled by error boundary. Loading state prevents race conditions. All errors fail closed (assume unauthorized)
- **Security Considerations:** Learner context stored in memory (not localStorage), context cleared on logout, learner_id validated by backend APIs, no direct access to learner data without context, fail-closed authorization

**Trace text diagram:**
```
RouteGuard Learner Route Authentication
├── RouteGuard component mount <-- RouteGuard.tsx:27
│   ├── useLearner() hook call <-- 2a
│   │   └── useContext(LearnerContext) <-- 2b
│   │       └── returns { learner, loading } <-- LearnerContext.tsx:97
│   ├── compute allowed flag <-- 2c
│   │   └── Boolean(learner) for learner routes
│   └── useEffect for session check <-- RouteGuard.tsx:35
│       ├── if (isLearnerRoute) check <-- 2d
│       └── setSessionLoaded(true) immediately <-- 2e
├── useEffect for redirect logic <-- RouteGuard.tsx:52
│   └── if (!loading && !allowed) <-- 2f
│       └── router.push("/") <-- 2g
└── render decision
    ├── loading state → LoadingSpinner <-- RouteGuard.tsx:58
    ├── !allowed → ErrorMessage + redirect <-- RouteGuard.tsx:67
    └── allowed → render children <-- RouteGuard.tsx:77
```

**Location ID: 2a**
- **Title:** Access learner context
- **Description:** Retrieves current learner state from React context
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:29

**Location ID: 2b**
- **Title:** Read context value
- **Description:** Hook accesses LearnerContext provider value
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:93

**Location ID: 2c**
- **Title:** Compute access permission
- **Description:** Determines route access based on learner presence for learner routes
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:33

**Location ID: 2d**
- **Title:** Skip session fetch
- **Description:** Learner routes bypass guardian session validation
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:36

**Location ID: 2e**
- **Title:** Mark session ready
- **Description:** Immediately marks session as loaded for learner routes
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:37

**Location ID: 2f**
- **Title:** Check authorization
- **Description:** Validates access after context loading completes
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:53

**Location ID: 2g**
- **Title:** Redirect unauthorized
- **Description:** Navigates to home when learner context is empty
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:54

### AI Guide: Learner Route Authentication Flow

**Motivation:**
Learner route authentication uses LearnerContext state validation to ensure an active learner is selected before accessing learner-specific content. This context-based approach separates learner access from guardian session authentication, enabling multi-learner management without session switching.

**Details:**

**Context Access and Computation**
The RouteGuard component accesses learner context via the useLearner() hook [2a]. The hook uses useContext(LearnerContext) to read the provider value, returning { learner, loading } state [2b]. The allowed flag is computed as Boolean(learner) for learner routes [2c].

**Session Check Bypass**
For learner routes, the session check useEffect immediately sets sessionLoaded(true) [2d]. This bypasses the guardian session validation since learner routes don't require session cookies [2e]. The redirect useEffect then checks if (!loading && !allowed) to determine authorization [2f].

**Redirect Logic**
If authorization fails, the router navigates to "/" for learner routes [2g]. This redirects users to the home page where they can select a learner. The render decision shows loading state during context loading, error message for unauthorized access, or protected children when authorized.

**Security Properties**
Learner context is stored in memory (not localStorage) to prevent persistence across sessions. Context is cleared on logout to prevent unauthorized access. Learner_id is validated by backend APIs for all learner-specific requests. The system uses fail-closed authorization to prevent unauthorized access.

## Trace ID: 3
**Title:** LearnerContext Initialization & State Management

**Description:** React context provider managing learner profile, mastery data, and gamification state

**Motivation:**
EduBoost Frontend implements a global LearnerContext to manage learner state across the application. The context provider wraps the entire application in the root layout, providing centralized state management for learner profile, mastery data, and gamification profile. This approach eliminates prop drilling and ensures consistent state access across all components. The provider initializes on mount by restoring learner state from localStorage (if available) and marks loading as complete. When the learner changes, a refresh effect triggers parallel API calls to fetch mastery scores and gamification profile, updating the context with the latest data. This centralized state management enables components like RouteGuard to quickly check learner presence for authorization, and allows the application to display up-to-date learner information without repeated API calls.

**Details:**
- **Context Initialization Flow:** Root Application Layout → <LearnerProvider> wrapper → Provider mount effect → restoreLearner() async → setLoading(false) → Learner change effect → refreshState() callback → Promise.all() fetch → getMastery() + getGamificationProfile() → setMasteryData() + setGamification() → Context.Provider value updates
- **State Management Architecture:** LearnerContext provides global state, useState hooks manage learner, masteryData, gamification, loading states, useEffect hooks handle initialization and learner changes, context value exposes state and setters to consumers
- **Concurrent Data Fetching:** Promise.all() fetches mastery and gamification in parallel, API calls are independent, no distributed locks needed as React handles state updates, multiple components read context simultaneously
- **Covered Objects:** LearnerProvider component, LearnerContext, React hooks (useState, useEffect, useContext), API services (LearnerService.getMastery, LearnerService.getGamificationProfile), localStorage, context state (learner, masteryData, gamification, loading)
- **Timeouts:** Context mount: ~1-5ms. restoreLearner: ~10-50ms. API fetch (parallel): ~200-500ms. State update: ~1-5ms. Total initialization: ~212-560ms
- **Error Handling:** API failures logged but don't block context, missing learner_id prevents fetch, loading state prevents premature access, error boundaries catch context errors
- **Security Considerations:** Learner data validated by backend APIs, context cleared on logout, no sensitive data in localStorage, learner_id used for all API requests, fail-closed on missing learner

**Trace text diagram:**
```
LearnerContext Initialization & State Management
├── Root Application Layout <-- 3a
│   └── <LearnerProvider> wrapper <-- LearnerContext.tsx:22
│       ├── Provider mount effect <-- 3b
│       │   └── restoreLearner() async <-- LearnerContext.tsx:31
│       │       └── setLoading(false) <-- 3c
│       ├── Learner change effect <-- 3f
│       │   └── refreshState() callback <-- LearnerContext.tsx:41
│       │       ├── Promise.all() fetch <-- 3d
│       │       │   ├── getMastery() <-- LearnerContext.tsx:45
│       │       │   └── getGamificationProfile() <-- LearnerContext.tsx:46
│       │       ├── setMasteryData() <-- 3e
│       │       └── setGamification() <-- LearnerContext.tsx:57
│       └── Context.Provider value <-- LearnerContext.tsx:73
│           ├── learner state <-- LearnerContext.tsx:23
│           ├── loading state <-- LearnerContext.tsx:27
│           ├── masteryData state <-- LearnerContext.tsx:24
│           └── gamification state <-- LearnerContext.tsx:25
```

**Location ID: 3a**
- **Title:** Mount context provider
- **Description:** Root layout wraps entire app with LearnerProvider
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/layout.tsx:76

**Location ID: 3b**
- **Title:** Initialize on mount
- **Description:** Effect runs once to restore learner state
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:29

**Location ID: 3c**
- **Title:** Complete initialization
- **Description:** Marks context as ready, enabling RouteGuard checks
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:33

**Location ID: 3d**
- **Title:** Fetch learner data
- **Description:** Parallel API calls for mastery scores and gamification profile
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:44

**Location ID: 3e**
- **Title:** Update mastery state
- **Description:** Stores subject mastery percentages in context
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:55

**Location ID: 3f**
- **Title:** Trigger data refresh
- **Description:** Effect watches learner changes to refresh associated data
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:64

### AI Guide: LearnerContext Initialization & State Management

**Motivation:**
LearnerContext provides centralized state management for learner profile, mastery data, and gamification profile across the application. This global context eliminates prop drilling and ensures consistent state access for components like RouteGuard that need to check learner presence for authorization.

**Details:**

**Provider Mount and Initialization**
The root application layout wraps the entire app with <LearnerProvider> [3a]. The provider mount effect runs once to restore learner state via restoreLearner() async function [3b]. When initialization completes, setLoading(false) marks the context as ready [3c].

**Learner Change and Data Refresh**
When the learner changes, the refreshState() callback is triggered [3f]. This function uses Promise.all() to fetch mastery scores and gamification profile in parallel [3d]. The results are stored via setMasteryData() and setGamification() [3e, 3f].

**Context Value Exposure**
The Context.Provider value exposes learner state, loading state, masteryData state, and gamification state to all consumers. This allows components like RouteGuard to quickly check learner presence for authorization without repeated API calls.

**Performance and Security**
Parallel API fetching reduces total latency. Learner data is validated by backend APIs for security. Context is cleared on logout to prevent unauthorized access. The system uses fail-closed authorization when learner is missing.

## Trace ID: 4
**Title:** Middleware Cookie-Based Route Protection

**Description:** Next.js middleware layer providing initial request-level authentication before page render

**Motivation:**
EduBoost Frontend implements Next.js middleware as the first line of defense for route protection. Middleware runs before page handlers execute, providing request-level authentication that prevents unauthorized users from even loading protected pages. The middleware checks for the presence of the eduboost_session httpOnly cookie. If the cookie exists, the request is allowed to proceed to the page handler. If the cookie is missing, the middleware constructs a redirect URL to the login page with a return path parameter, then returns a 307 redirect response. This early interception improves security by preventing page rendering for unauthorized users and provides a better user experience by redirecting before loading the page. The middleware is configured via a matcher array that specifies which routes trigger middleware execution. This dual-layer approach (middleware + RouteGuard) provides defense in depth: middleware handles initial request interception, while RouteGuard handles runtime authorization checks.

**Details:**
- **Middleware Request Flow:** middleware(request) entry → Check session cookie presence via request.cookies.get() → Session exists branch: if (hasSession) → NextResponse.next() → Continue to page handler → No session branch: buildRedirectUrl() → Extract pathname + search → Construct /login?redirect=... → NextResponse.redirect() → Return 307 redirect response
- **Protected Routes Configuration:** config.matcher → PROTECTED_MATCHERS array → Triggers middleware execution for specified route patterns
- **Cookie Validation:** Middleware checks eduboost_session cookie presence, cookie value not validated (only presence checked), httpOnly cookie prevents client-side access, redirect preserves original destination via query parameter
- **Concurrency Safety:** Middleware runs per-request, no shared state, cookie read is atomic, redirect construction is deterministic, no distributed locks needed
- **Covered Objects:** Next.js middleware, NextRequest, NextResponse, cookie store, PROTECTED_MATCHERS configuration, buildRedirectUrl helper, redirect URL construction
- **Timeouts:** Cookie check: <1ms. Redirect construction: ~1-5ms. Response generation: <1ms. Total middleware: ~2-7ms
- **Error Handling:** Missing cookie triggers redirect. Cookie read failures logged. Redirect construction failures logged. All errors fail closed (redirect to login)
- **Security Considerations:** httpOnly cookie prevents XSS, early interception prevents page load, redirect preserves destination, fail-closed on missing cookie, matcher configuration limits scope

**Trace text diagram:**
```
Next.js Middleware Request Interception
└── middleware(request) <-- 4a
    ├── Check session cookie presence
    │   └── request.cookies.get() <-- 4b
    ├── Session exists branch
    │   └── if (hasSession) <-- 4c
    │       └── NextResponse.next() <-- middleware.ts:32
    │           └── Continue to page handler
    └── No session branch
        ├── buildRedirectUrl() <-- 4d
        │   ├── Extract pathname + search <-- middleware.ts:23
        │   └── Construct /login?redirect=... <-- middleware.ts:25
        └── NextResponse.redirect() <-- 4e
            └── Return 307 redirect response

Protected Routes Configuration
└── config.matcher <-- middleware.ts:38
    └── PROTECTED_MATCHERS array <-- middleware.ts:7
        └── Triggers middleware execution
```

**Location ID: 4a**
- **Title:** Intercept request
- **Description:** Middleware runs before protected route handlers execute
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:29

**Location ID: 4b**
- **Title:** Check session cookie
- **Description:** Validates presence of eduboost_session cookie
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:30

**Location ID: 4c**
- **Title:** Allow authenticated
- **Description:** Permits request to continue when session cookie exists
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:31

**Location ID: 4d**
- **Title:** Build redirect URL
- **Description:** Constructs login URL with return path parameter
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:34

**Location ID: 4e**
- **Title:** Redirect to login
- **Description:** Returns 307 redirect response for unauthenticated requests
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:35

### AI Guide: Middleware Cookie-Based Route Protection

**Motivation:**
Next.js middleware provides the first line of defense for route protection by intercepting requests before page handlers execute. This early interception prevents unauthorized users from loading protected pages and provides a better user experience by redirecting before page render.

**Details:**

**Request Interception and Cookie Check**
The middleware function intercepts requests to protected routes [4a]. It checks for the presence of the eduboost_session cookie via request.cookies.get() [4b]. This cookie presence check is fast and doesn't require validation of the cookie value.

**Session Validation and Allow**
If the session cookie exists (hasSession is true), the middleware calls NextResponse.next() to allow the request to proceed to the page handler [4c]. This permits authenticated users to access the protected page.

**Redirect Construction**
When no session cookie is present, buildRedirectUrl() constructs a login URL with the original destination preserved as a query parameter [4d]. This allows the login page to redirect users back to their intended destination after authentication.

**Redirect Response**
The middleware returns NextResponse.redirect() with a 307 status code to redirect the user to the login page [4e]. The matcher configuration in config.middleware specifies which routes trigger middleware execution via the PROTECTED_MATCHERS array.

**Security Properties**
The middleware uses httpOnly cookies to prevent XSS access. Early interception prevents page load for unauthorized users. The redirect preserves the original destination for post-login navigation. The system uses fail-closed authorization when the cookie is missing.

## Trace ID: 5
**Title:** Login Flow Setting Learner Context

**Description:** User authentication flow that establishes session and populates learner context

**Motivation:**
EduBoost Frontend implements a login flow that establishes both session authentication and learner context. The login form submission calls AuthService.loginGuardian() which POSTs to /api/auth/login endpoint. This Next.js API route proxies the request to the FastAPI backend for credential validation. On successful authentication, the backend returns an access token which is set as an httpOnly cookie via setSessionCookie(). The login page then fetches the guardian dashboard via ParentService.getDashboard() to retrieve the list of associated learners. The first learner from the dashboard is selected and used to populate the LearnerContext via setLearner(). This context update triggers RouteGuard re-renders, allowing access to protected routes. This flow ensures that after login, users have both a valid session cookie for guardian authentication and an active learner context for learner-specific routes.

**Details:**
- **Login Authentication Flow:** Login form submission → AuthService.loginGuardian() → fetchApi("/api/auth/login") → Next.js API Route Handler → backendFetch("/auth/login") → FastAPI backend validates credentials → On success: setSessionCookie() → Set httpOnly cookie → Return access_token → Fetch guardian dashboard → ParentService.getDashboard() → Returns learner profiles array → Update LearnerContext → setLearner(activeLearner) → Context state update → Triggers RouteGuard re-render
- **Cookie and Context Management:** Session stored in httpOnly cookie for guardian auth, LearnerContext stores active learner profile, context update triggers consumer re-renders, dashboard fetch provides learner selection options
- **Concurrent Operations:** Login request is sequential, dashboard fetch waits for login success, context update is synchronous, no distributed locks needed as operations are per-session
- **Covered Objects:** Login form, AuthService, fetchApi, Next.js API route, backendFetch, FastAPI backend, setSessionCookie, ParentService, LearnerContext, setLearner, RouteGuard
- **Timeouts:** Login request: ~200-500ms. Cookie setting: <5ms. Dashboard fetch: ~200-500ms. Context update: ~1-5ms. Total login flow: ~401-1010ms
- **Error Handling:** Login failures return 401. Dashboard errors logged. Missing learners handled gracefully. Context errors caught by error boundary. All errors fail closed
- **Security Considerations:** httpOnly cookie prevents XSS, credentials validated by backend, learner_id validated by APIs, context cleared on logout, fail-closed on authentication failure

**Trace text diagram:**
```
Login Authentication Flow
├── Login form submission <-- 5a
│   └── AuthService.loginGuardian() <-- services.ts:72
│       └── fetchApi("/api/auth/login") <-- services.ts:72
│           └── Next.js API Route Handler <-- 5b
│               ├── backendFetch("/auth/login")
│               │   └── FastAPI backend validates credentials
│               └── On success:
│                   ├── setSessionCookie() <-- 5c
│                   │   └── Set httpOnly cookie <-- 5d
│                   └── Return access_token <-- route.ts:30
├── Fetch guardian dashboard <-- 5e
│   └── ParentService.getDashboard() <-- services.ts:177
│       └── Returns learner profiles array
└── Update LearnerContext <-- 5f
    └── setLearner(activeLearner)
        └── Context state update <-- 5g
            └── Triggers RouteGuard re-render
```

**Location ID: 5a**
- **Title:** Submit credentials
- **Description:** Calls backend login endpoint with email and password
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:88

**Location ID: 5b**
- **Title:** Proxy to backend
- **Description:** Next.js API route forwards request to FastAPI backend
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/auth/login/route.ts:8

**Location ID: 5c**
- **Title:** Set session cookie
- **Description:** Stores JWT in httpOnly cookie on successful authentication
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/auth/login/route.ts:25

**Location ID: 5d**
- **Title:** Write cookie header
- **Description:** Sets eduboost_session cookie with httpOnly and sameSite flags
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/auth/cookies.ts:16

**Location ID: 5e**
- **Title:** Fetch learner profiles
- **Description:** Retrieves guardian's associated learner accounts
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:92

**Location ID: 5f**
- **Title:** Populate learner context
- **Description:** Updates LearnerContext with active learner profile
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:100

**Location ID: 5g**
- **Title:** Update context state
- **Description:** React state setter triggers context consumers to re-render
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:23

### AI Guide: Login Flow Setting Learner Context

**Motivation:**
The login flow establishes both session authentication (via httpOnly cookie) and learner context (via LearnerContext). This dual setup enables guardian route protection through session validation and learner route protection through context state.

**Details:**

**Credential Submission and Backend Validation**
The login form submits credentials via AuthService.loginGuardian() [5a]. The request is proxied through a Next.js API route to the FastAPI backend for credential validation [5b]. On successful authentication, the backend returns an access token.

**Session Cookie Storage**
The setSessionCookie() function stores the access token in an httpOnly cookie [5c]. The cookie is set with httpOnly and sameSite flags via the cookie helper [5d]. This provides secure session storage that prevents XSS access.

**Dashboard Fetch and Learner Selection**
After successful login, ParentService.getDashboard() fetches the guardian's learner profiles [5e]. The first learner from the dashboard is selected as the active learner. setLearner() populates the LearnerContext with the active learner profile [5f].

**Context Update and RouteGuard Trigger**
The context state update triggers all context consumers to re-render [5g]. This includes RouteGuard components that can now check learner presence for authorization. The dual-layer authentication (session cookie + learner context) is now established.

**Security Properties**
The system uses httpOnly cookies to prevent XSS access. Credentials are validated by the FastAPI backend. Learner_id is validated by backend APIs for all learner-specific requests. Context is cleared on logout to prevent unauthorized access. The system uses fail-closed authorization on authentication failure.

## Trace ID: 6
**Title:** RouteGuard Test Suite - Loading State Validation

**Description:** Unit test verifying loading spinner display during async session validation

**Motivation:**
EduBoost Frontend implements automated tests for RouteGuard to ensure proper loading state behavior during async session validation. The test mocks the global fetch function to return a pending promise that never resolves, simulating an in-flight session validation request. The RouteGuard component is rendered with a LearnerProvider wrapper and configured for parent route protection. The test asserts that the loading message "Checking your session" is displayed to the user during the async operation. This test ensures that users see appropriate feedback while authentication is being validated, preventing confusion about whether the application is working. The loading state is determined by checking both the context loading state and the sessionLoaded flag, ensuring the loading spinner displays until both are ready.

**Details:**
- **Test Execution Flow:** Test suite setup → test('shows loading state...') definition → Mock fetch as pending promise → Component Rendering → render() test helper → <LearnerProvider> wrapper → <RouteGuard required="parent"> → <div>ok</div> children → Validation & Assertion → RouteGuard component logic → if (loading || !sessionLoaded) check → return LoadingSpinner + message → Test assertion → expect(getByText(/Checking.../))
- **Mock Strategy:** Global fetch stubbed to return pending promise, simulates in-flight request, prevents session resolution, forces loading state to persist
- **Component Behavior:** RouteGuard checks loading and sessionLoaded flags, loading state from LearnerContext, sessionLoaded flag from useEffect, both must be true to exit loading state
- **Covered Objects:** Test suite, global fetch mock, render helper, LearnerProvider, RouteGuard component, LoadingSpinner, loading message, React Testing Library queries
- **Timeouts:** Test execution: ~10-50ms. Component render: ~5-20ms. Assertion: <1ms. Total test: ~15-71ms
- **Error Handling:** Mock failures cause test failure. Component errors caught by test runner. Assertion failures reported with clear messages
- **Test Coverage:** Validates loading UI during async session fetch, ensures user feedback during authentication, covers loading state logic, tests parent route configuration

**Trace text diagram:**
```
RouteGuard Loading State Test Flow
├── Test Suite Setup
│   ├── test('shows loading state...') <-- 6a
│   └── Mock fetch as pending promise <-- 6b
├── Component Rendering
│   ├── render() test helper <-- 6c
│   └── <LearnerProvider> <-- RouteGuard.test.tsx:28
│       └── <RouteGuard required="parent"> <-- 6d
│           └── <div>ok</div> <-- RouteGuard.test.tsx:29
└── Validation & Assertion
    ├── RouteGuard component logic
    │   ├── if (loading || !sessionLoaded) <-- 6f
    │   └── return LoadingSpinner + message <-- 6g
    └── Test assertion
        └── expect(getByText(/Checking.../)) <-- 6e
```

**Location ID: 6a**
- **Title:** Define test case
- **Description:** Test validates loading UI during async session fetch
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:24

**Location ID: 6b**
- **Title:** Mock pending fetch
- **Description:** Stubs fetch to never resolve, simulating in-flight request
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:25

**Location ID: 6c**
- **Title:** Render component
- **Description:** Mounts RouteGuard with LearnerProvider wrapper
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:27

**Location ID: 6d**
- **Title:** Test parent route
- **Description:** Renders RouteGuard configured for guardian authentication
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:29

**Location ID: 6e**
- **Title:** Assert loading message
- **Description:** Verifies loading state UI is displayed to user
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:33

**Location ID: 6f**
- **Title:** Loading condition
- **Description:** Component checks both context and session loading states
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:58

**Location ID: 6g**
- **Title:** Render loading UI
- **Description:** Displays loading message that test assertion validates
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:62

### AI Guide: RouteGuard Test Suite - Loading State Validation

**Motivation:**
The loading state test ensures users see appropriate feedback during async session validation. By mocking fetch to return a pending promise, the test simulates an in-flight authentication request and validates that the loading spinner displays correctly.

**Details:**

**Test Setup and Mock Configuration**
The test case is defined with a descriptive name indicating it validates loading state during guardian session requests [6a]. The global fetch function is mocked to return a pending promise that never resolves, simulating an in-flight request [6b].

**Component Rendering**
The render() test helper mounts the RouteGuard component with a LearnerProvider wrapper [6c]. The RouteGuard is configured with required="parent" to test guardian route protection [6d]. The component is rendered with a simple <div>ok</div> child [6d].

**Loading State Logic**
The RouteGuard component checks both the loading state from LearnerContext and the sessionLoaded flag [6f]. When either is true, the component returns a LoadingSpinner with a loading message [6g]. This ensures users see feedback during authentication.

**Test Assertion**
The test uses React Testing Library's getByText query to find the loading message [6e]. The assertion verifies that the "Checking your session" message is displayed, confirming proper loading state behavior.

**Test Coverage**
This test validates loading UI during async session fetch, ensures user feedback during authentication, covers loading state logic, and tests parent route configuration.

## Trace ID: 7
**Title:** RouteGuard Test Suite - Authentication Success Flow

**Description:** Integration test verifying successful guardian authentication and content rendering

**Motivation:**
EduBoost Frontend implements automated tests for RouteGuard to ensure successful authentication allows access to protected content. The test mocks the global fetch function to return an authenticated session response (authenticated: true). The RouteGuard component is rendered with a LearnerProvider wrapper and configured for parent route protection. The test asserts that the protected children ("ok" text) are displayed after successful authentication, and verifies that the session endpoint was called. This test ensures that when session validation succeeds, users can access protected content without being redirected. The test validates the complete authentication flow from session fetch through authorization check to content rendering.

**Details:**
- **Test Execution Flow:** Test setup & mocking → Define test case → Mock fetch to return auth=true → Component render & execution → Render RouteGuard with LearnerProvider → useEffect triggers fetchSessionState() → fetch("/api/auth/session") called → Mock returns {authenticated: true} → setGuardianAuthenticated(true) → RouteGuard authorization logic → Check !allowed condition → Render protected children → Test assertions → Assert "ok" text visible → Verify session endpoint called
- **Mock Strategy:** Global fetch stubbed to return authenticated response, simulates successful session validation, allows test to control authentication outcome
- **Component Behavior:** RouteGuard calls fetchSessionState() on mount, session endpoint returns authenticated status, state update triggers re-render, allowed flag determines content rendering
- **Covered Objects:** Test suite, global fetch mock, render helper, LearnerProvider, RouteGuard component, fetchSessionState function, session endpoint, React state, React Testing Library queries
- **Timeouts:** Test execution: ~10-50ms. Component render: ~5-20ms. Session fetch: ~1-5ms. State update: ~1-5ms. Assertion: <1ms. Total test: ~17-81ms
- **Error Handling:** Mock failures cause test failure. Component errors caught by test runner. Assertion failures reported with clear messages
- **Test Coverage:** Validates authenticated user can access protected content, verifies session endpoint invocation, tests authorization logic, covers content rendering on success

**Trace text diagram:**
```
Trace 7: Authentication Success Flow
└── RouteGuard Test Suite
    ├── Test setup & mocking
    │   ├── Define test case <-- 7a
    │   └── Mock fetch to return auth=true <-- 7b
    ├── Component render & execution
    │   ├── Render RouteGuard with LearnerProvider <-- RouteGuard.test.tsx:49
    │   ├── useEffect triggers fetchSessionState() <-- RouteGuard.tsx:35
    │   ├── fetch("/api/auth/session") called <-- RouteGuard.tsx:16
    │   ├── Mock returns {authenticated: true}
    │   └── setGuardianAuthenticated(true) <-- RouteGuard.tsx:43
    ├── RouteGuard authorization logic
    │   ├── Check !allowed condition <-- 7e
    │   └── Render protected children <-- 7f
    └── Test assertions
        ├── Assert "ok" text visible <-- 7c
        └── Verify session endpoint called <-- 7d
```

**Location ID: 7a**
- **Title:** Define success test
- **Description:** Test validates authenticated user can access protected content
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:46

**Location ID: 7b**
- **Title:** Mock authenticated session
- **Description:** Stubs session endpoint to return authenticated=true
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:47

**Location ID: 7c**
- **Title:** Assert content rendered
- **Description:** Verifies protected children are displayed after auth succeeds
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:55

**Location ID: 7d**
- **Title:** Verify session call
- **Description:** Confirms RouteGuard invoked session validation endpoint
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:56

**Location ID: 7e**
- **Title:** Check authorization
- **Description:** Component evaluates allowed flag after session loads
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:67

**Location ID: 7f**
- **Title:** Render children
- **Description:** Returns protected content when authentication succeeds
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:77

### AI Guide: RouteGuard Test Suite - Authentication Success Flow

**Motivation:**
The authentication success test ensures that when session validation succeeds, users can access protected content. By mocking the session endpoint to return authenticated=true, the test validates the complete authentication flow from session fetch through authorization to content rendering.

**Details:**

**Test Setup and Mock Configuration**
The test case is defined to validate that authenticated users can access protected content [7a]. The global fetch function is mocked to return an authenticated session response [7b]. This simulates successful session validation.

**Component Execution**
The RouteGuard component is rendered with a LearnerProvider wrapper [7a]. The useEffect hook triggers fetchSessionState() which calls the session endpoint [7b]. The mock returns {authenticated: true}, and setGuardianAuthenticated(true) updates the component state [7b].

**Authorization Logic**
The RouteGuard checks the !allowed condition after the session loads [7e]. When authentication succeeds, the allowed flag is true, and the component renders the protected children [7f]. This allows the user to access the protected content.

**Test Assertions**
The test uses React Testing Library's findByText to assert that the "ok" text is visible [7c]. It also verifies that the session endpoint was called with the correct parameters [7d]. These assertions confirm successful authentication and content rendering.

**Test Coverage**
This test validates that authenticated users can access protected content, verifies session endpoint invocation, tests authorization logic, and covers content rendering on success.

## Trace ID: 8
**Title:** RouteGuard Test Suite - Unauthenticated Redirect Flow

**Description:** Test validating error UI and retry navigation for failed authentication

**Motivation:**
EduBoost Frontend implements automated tests for RouteGuard to ensure proper error handling and retry navigation when authentication fails. The test mocks the global fetch function to return an unauthenticated session response (authenticated: false). The RouteGuard component is rendered with a LearnerProvider wrapper and configured for parent route protection. The test asserts that a guardian-specific error message is displayed, and verifies that clicking the "Try Again" button navigates to the login page. This test ensures that when session validation fails, users see appropriate error messaging and can retry authentication. The test validates the complete error flow from session fetch failure through error display to retry navigation.

**Details:**
- **Test Execution Flow:** Test Setup & Execution → Define failure test case → Mock session endpoint (auth=false) → Render RouteGuard with parent role → (triggers useEffect in RouteGuard) → RouteGuard Component Lifecycle → fetchSessionState() called → fetch("/api/auth/session") → returns { authenticated: false } → setGuardianAuthenticated(false) → setSessionLoaded(true) → Re-render with allowed=false → Renders ErrorMessage component → Shows "Please log in..." → onRetry handler defined → User Interaction & Assertion → User clicks "Try Again" button → Triggers onRetry callback → router.push("/login") → Test verifies login redirect
- **Mock Strategy:** Global fetch stubbed to return unauthenticated response, simulates failed session validation, allows test to control authentication outcome
- **Component Behavior:** RouteGuard calls fetchSessionState() on mount, session endpoint returns unauthenticated status, state update triggers re-render, ErrorMessage component displays error, onRetry handler navigates to login
- **Covered Objects:** Test suite, global fetch mock, render helper, LearnerProvider, RouteGuard component, ErrorMessage component, fetchSessionState function, session endpoint, React state, Next.js router, React Testing Library queries
- **Timeouts:** Test execution: ~10-50ms. Component render: ~5-20ms. Session fetch: ~1-5ms. State update: ~1-5ms. Button click: ~1-5ms. Navigation: ~1-5ms. Assertion: <1ms. Total test: ~19-91ms
- **Error Handling:** Mock failures cause test failure. Component errors caught by test runner. Assertion failures reported with clear messages
- **Test Coverage:** Validates unauthenticated user sees error and can retry, tests error message display, verifies retry navigation, covers error handling logic

**Trace text diagram:**
```
RouteGuard Unauthenticated Redirect Flow
├── Test Setup & Execution
│   ├── Define failure test case <-- 8a
│   ├── Mock session endpoint (auth=false) <-- 8b
│   └── Render RouteGuard with parent role <-- RouteGuard.test.tsx:62
│       └── (triggers useEffect in RouteGuard) <-- RouteGuard.tsx:35
├── RouteGuard Component Lifecycle
│   ├── fetchSessionState() called <-- RouteGuard.tsx:41
│   │   └── fetch("/api/auth/session") <-- RouteGuard.tsx:16
│   │       └── returns { authenticated: false } <-- RouteGuard.tsx:21
│   ├── setGuardianAuthenticated(false) <-- RouteGuard.tsx:43
│   ├── setSessionLoaded(true) <-- RouteGuard.tsx:44
│   └── Re-render with allowed=false <-- RouteGuard.tsx:33
│       └── Renders ErrorMessage component <-- RouteGuard.tsx:69
│           ├── Shows "Please log in..." <-- 8c
│           └── onRetry handler defined <-- 8f
└── User Interaction & Assertion
    ├── User clicks "Try Again" button <-- 8d
    │   └── Triggers onRetry callback <-- RouteGuard.tsx:72
    │       └── router.push("/login") <-- RouteGuard.tsx:54
    └── Test verifies login redirect <-- 8e
```

**Location ID: 8a**
- **Title:** Define failure test
- **Description:** Test validates unauthenticated user sees error and can retry
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:59

**Location ID: 8b**
- **Title:** Mock failed session
- **Description:** Stubs session endpoint to return authenticated=false
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:60

**Location ID: 8c**
- **Title:** Assert error message
- **Description:** Verifies guardian-specific error message is displayed
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:68

**Location ID: 8d**
- **Title:** Click retry button
- **Description:** Simulates user clicking retry action in error UI
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:70

**Location ID: 8e**
- **Title:** Assert login redirect
- **Description:** Confirms retry button navigates to login page
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/__tests__/RouteGuard.test.tsx:71

**Location ID: 8f**
- **Title:** Retry handler
- **Description:** ErrorMessage onRetry prop navigates based on required role
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:72

### AI Guide: RouteGuard Test Suite - Unauthenticated Redirect Flow

**Motivation:**
The unauthenticated redirect test ensures that when session validation fails, users see appropriate error messaging and can retry authentication. By mocking the session endpoint to return authenticated=false, the test validates the complete error flow from session fetch failure through error display to retry navigation.

**Details:**

**Test Setup and Mock Configuration**
The test case is defined to validate that unauthenticated users see an error message and can retry [8a]. The global fetch function is mocked to return an unauthenticated session response [8b]. This simulates failed session validation.

**Component Lifecycle**
The RouteGuard component is rendered with parent role configuration [8b]. The useEffect hook triggers fetchSessionState() which calls the session endpoint [8b]. The mock returns {authenticated: false}, and setGuardianAuthenticated(false) updates the component state [8b]. The component re-renders with allowed=false [8b].

**Error Display**
The RouteGuard renders the ErrorMessage component when authentication fails [8f]. The error message shows "Please log in as a guardian" for parent routes [8c]. The ErrorMessage component includes an onRetry handler defined by RouteGuard [8f].

**User Interaction and Navigation**
The test simulates a user clicking the "Try Again" button [8d]. This triggers the onRetry callback which calls router.push("/login") [8f]. The test verifies that the navigation to the login page occurred [8e].

**Test Coverage**
This test validates that unauthenticated users see error and can retry, tests error message display, verifies retry navigation, and covers error handling logic.
