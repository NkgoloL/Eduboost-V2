# EduBoost Frontend: Next.js Learning Platform with Auth, AI Lessons, Diagnostics & PWA

A Next.js 15 TypeScript frontend providing guardian authentication, AI-powered adaptive lessons, IRT diagnostics, gamification, POPIA-compliant parent dashboards, and offline PWA capabilities. Key flows: guardian login [1c], API proxy layer [2b], learner dashboard hydration [3d], async lesson generation [4c], diagnostic submission [5d], and offline service worker caching [6b].

## Trace ID: 1
**Title:** Guardian Login → JWT Token → Parent Dashboard → Learner Context → Navigation

**Description:** Authentication flow from form submission through token storage, parent dashboard fetch, learner context initialization, and redirect to dashboard

**Motivation:**
EduBoost Frontend implements a comprehensive guardian authentication flow that establishes session-based authentication and initializes learner context. The login form submits credentials via AuthService.loginGuardian() which calls the /api/auth/login endpoint. This Next.js API route proxies the request to the FastAPI backend for credential validation. On successful authentication, the backend returns a JWT access token which is stored in an httpOnly session cookie via setSessionCookie(). The login page then fetches the parent dashboard via ParentService.getDashboard() to retrieve the guardian's learner list. The first learner from the dashboard is selected and used to initialize the LearnerContext via setLearner(). Finally, the user is redirected to the dashboard or their original destination. This flow ensures that after login, users have both a valid session cookie for authentication and an active learner context for learner-specific features.

**Details:**
- **Authentication Flow:** LoginPage form submission → AuthService.loginGuardian() → fetchApi() wrapper → POST /api/auth/login → Next.js API route handler → Extract request body → backendFetch() to FastAPI → JWT response received → setSessionCookie() → Fetch parent dashboard → ParentService.getDashboard() → GET /parents/dashboard → Learner list retrieved → Initialize learner context → setLearner() updates context → router.push() navigation
- **Session and Context Management:** JWT stored in httpOnly cookie for session authentication, LearnerContext stores active learner profile, context update triggers consumer re-renders, dashboard fetch provides learner selection options, redirect preserves original destination
- **Concurrent Operations:** Login request is sequential, dashboard fetch waits for login success, context update is synchronous, no distributed locks needed as operations are per-session
- **Covered Objects:** LoginPage, AuthService, fetchApi, Next.js API route, backendFetch, FastAPI backend, setSessionCookie, ParentService, LearnerContext, setLearner, Next.js router
- **Timeouts:** Login request: ~200-500ms. Cookie setting: <5ms. Dashboard fetch: ~200-500ms. Context update: ~1-5ms. Navigation: ~10-50ms. Total login flow: ~411-1060ms
- **Error Handling:** Login failures return 401. Dashboard errors logged. Missing learners handled gracefully. Context errors caught by error boundary. All errors fail closed
- **Security Considerations:** httpOnly cookie prevents XSS, credentials validated by backend, learner_id validated by APIs, context cleared on logout, fail-closed on authentication failure

**Trace text diagram:**
```
Guardian Login Flow
├── LoginPage form submission <-- 1a
│   └── AuthService.loginGuardian() <-- services.ts:71
│       └── fetchApi() wrapper <-- 1b
│           └── POST /api/auth/login <-- services.ts:73
│               └── Next.js API route handler <-- 1c
│                   ├── Extract request body <-- 1d
│                   └── backendFetch() to FastAPI <-- route.ts:8
│                       └── JWT response received <-- route.ts:15
│                           └── setSessionCookie() <-- 1e
├── Fetch parent dashboard <-- 1f
│   └── ParentService.getDashboard() <-- services.ts:177
│       └── GET /parents/dashboard
│           └── Learner list retrieved <-- page.tsx:93
└── Initialize learner context <-- 1g
    └── setLearner() updates context <-- page.tsx:73
        └── router.push() navigation <-- 1h
```

**Location ID: 1a**
- **Title:** Login Form Submission
- **Description:** User submits email/password credentials to authenticate as guardian
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:88

**Location ID: 1b**
- **Title:** API Login Request
- **Description:** POST to /api/auth/login endpoint with credentials via fetchApi wrapper
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/services.ts:64

**Location ID: 1c**
- **Title:** Next.js API Route Handler
- **Description:** Server-side route handler extracts request body for backend forwarding
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/auth/login/route.ts:7

**Location ID: 1d**
- **Title:** Backend API Call
- **Description:** Forward authentication request to FastAPI backend at /auth/login
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/auth/login/route.ts:8

**Location ID: 1e**
- **Title:** Session Cookie Storage
- **Description:** Store JWT access token in HTTP-only session cookie for authentication
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/auth/login/route.ts:25

**Location ID: 1f**
- **Title:** Fetch Parent Dashboard
- **Description:** Retrieve guardian's learner list and subscription info from /parents/dashboard
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:92

**Location ID: 1g**
- **Title:** Initialize Learner Context
- **Description:** Set active learner in global React context from first learner in dashboard
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:100

**Location ID: 1h**
- **Title:** Navigate to Dashboard
- **Description:** Redirect authenticated user to learner dashboard or original destination
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:111

### AI Guide: Guardian Login → JWT Token → Parent Dashboard → Learner Context → Navigation

**Motivation:**
The guardian login flow establishes both session authentication (via httpOnly cookie) and learner context (via LearnerContext). This dual setup enables guardian route protection through session validation and learner route protection through context state.

**Details:**

**Credential Submission and Backend Validation**
The login form submits credentials via AuthService.loginGuardian() [1a]. The request is proxied through a Next.js API route to the FastAPI backend for credential validation [1c]. On successful authentication, the backend returns a JWT access token.

**Session Cookie Storage**
The setSessionCookie() function stores the JWT in an httpOnly cookie [1e]. This provides secure session storage that prevents XSS access. The cookie is set with httpOnly and sameSite flags for security.

**Dashboard Fetch and Learner Selection**
After successful login, ParentService.getDashboard() fetches the guardian's learner profiles [1f]. The first learner from the dashboard is selected as the active learner. setLearner() populates the LearnerContext with the active learner profile [1g].

**Context Update and Navigation**
The context state update triggers all context consumers to re-render. The router.push() navigation redirects the user to the dashboard or their original destination [1h]. The dual-layer authentication (session cookie + learner context) is now established.

**Security Properties**
The system uses httpOnly cookies to prevent XSS access. Credentials are validated by the FastAPI backend. Learner_id is validated by backend APIs for all learner-specific requests. Context is cleared on logout to prevent unauthorized access. The system uses fail-closed authorization on authentication failure.

## Trace ID: 2
**Title:** Client API Call → Proxy Route → Backend Fetch → Response Unwrapping

**Description:** API communication layer showing how client-side calls flow through Next.js API routes to the FastAPI backend with envelope unwrapping

**Motivation:**
EduBoost Frontend implements a proxy-based API communication layer that routes client-side API calls through Next.js API routes to the FastAPI backend. This architecture enables server-side token management, CORS handling, and response envelope unwrapping. The fetchApi() wrapper in client.ts resolves the API endpoint to a proxy path (/api/backend/*), executes the fetch request with credentials and request ID headers, and unwraps the standardized API envelope response format. The Next.js API route at /api/backend/[...path] sanitizes the path, forwards the request to the backend via backendFetch(), and returns the response. The backendFetch() function constructs the full backend URL using the API_BASE_URL environment variable, sets the Authorization header from the session cookie, and executes the fetch request to the FastAPI backend. This proxy layer provides a clean separation between client and backend, enabling secure token management and standardized error handling.

**Details:**
- **API Communication Flow:** fetchApi() in client.ts → resolveRequestUrl() → fetch() with credentials → parseJson(response) → Envelope unwrapping → throw ApiError on error → Next.js API Route /api/backend/[...path] → proxy() handler → sanitizePath(params.path) → backendFetch(backendPath) → backendFetch() in server-client.ts → Construct backend URL → Set Authorization header → fetch(BASE_URL + endpoint) → FastAPI Backend
- **Proxy Layer Architecture:** Client calls go through Next.js API routes, path sanitization prevents injection attacks, Authorization header set from session cookie, envelope unwrapping standardizes response format, error normalization provides consistent error handling
- **Concurrent Request Handling:** Each API call is independent, no shared state between requests, request ID headers enable tracing, no distributed locks needed as operations are per-request
- **Covered Objects:** fetchApi wrapper, resolveRequestUrl, fetch API, parseJson, envelope unwrapping, ApiError, Next.js API route, proxy handler, sanitizePath, backendFetch, Authorization header, FastAPI backend
- **Timeouts:** URL resolution: <1ms. Client fetch: ~100-500ms. Response parsing: <5ms. Envelope unwrapping: <1ms. Proxy handling: ~5-10ms. Backend fetch: ~100-500ms. Total API call: ~211-1017ms
- **Error Handling:** Network errors throw ApiError, envelope errors normalized, backend errors standardized, all errors fail closed with clear messages
- **Security Considerations:** Session token in Authorization header, path sanitization prevents injection, request ID enables audit trail, CORS handled by Next.js, fail-closed on authentication failure

**Trace text diagram:**
```
Client API Call Flow
├── fetchApi() in client.ts <-- client.ts:13
│   ├── resolveRequestUrl() <-- 2a
│   ├── fetch() with credentials <-- 2b
│   ├── parseJson(response) <-- client.ts:26
│   └── Envelope unwrapping <-- 2f
│       └── throw ApiError on error <-- 2g
│
└── Next.js API Route /api/backend/[...path]
    ├── proxy() handler <-- route.ts:31
    │   ├── sanitizePath(params.path) <-- 2c
    │   └── backendFetch(backendPath) <-- 2d
    │
    └── backendFetch() in server-client.ts <-- server-client.ts:14
        ├── Construct backend URL <-- 2e
        ├── Set Authorization header <-- server-client.ts:22
        └── fetch(BASE_URL + endpoint) <-- server-client.ts:32
            └── FastAPI Backend <-- api_v2.py:200
```

**Location ID: 2a**
- **Title:** Resolve API Endpoint
- **Description:** Convert endpoint to proxy path /api/backend/* for Next.js routing
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/client.ts:18

**Location ID: 2b**
- **Title:** Client-Side Fetch
- **Description:** Execute fetch request with credentials and request ID header
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/client.ts:21

**Location ID: 2c**
- **Title:** Proxy Path Sanitization
- **Description:** Sanitize and construct backend path from catch-all route parameters
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/backend/[...path]/route.ts:35

**Location ID: 2d**
- **Title:** Backend Fetch with Token
- **Description:** Forward request to FastAPI backend with session token from cookies
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/api/backend/[...path]/route.ts:44

**Location ID: 2e**
- **Title:** Construct Backend URL
- **Description:** Build full backend URL using API_BASE_URL environment variable
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/server-client.ts:15

**Location ID: 2f**
- **Title:** Unwrap API Envelope
- **Description:** Extract data from standardized API envelope response format
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/client.ts:39

**Location ID: 2g**
- **Title:** Error Normalization
- **Description:** Convert backend error responses to normalized ApiError format
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/client.ts:36

### AI Guide: Client API Call → Proxy Route → Backend Fetch → Response Unwrapping

**Motivation:**
The proxy-based API communication layer routes client-side calls through Next.js API routes to the FastAPI backend, enabling server-side token management, CORS handling, and standardized response envelope unwrapping.

**Details:**

**Client-Side API Call**
The fetchApi() wrapper in client.ts resolves the API endpoint to a proxy path [2a]. It executes the fetch request with credentials and request ID headers [2b]. The response is parsed as JSON and the envelope is unwrapped to extract the data [2f]. Errors are normalized to ApiError format for consistent handling [2g].

**Next.js API Route Proxy**
The Next.js API route at /api/backend/[...path] handles the proxy logic [2d]. The proxy handler sanitizes the path to prevent injection attacks [2c]. It forwards the request to the backend via backendFetch() with the sanitized path.

**Backend Fetch and Authorization**
The backendFetch() function constructs the full backend URL using the API_BASE_URL environment variable [2e]. It sets the Authorization header from the session cookie for authentication [2d]. The fetch request is executed to the FastAPI backend.

**Response Handling**
The FastAPI backend returns a response in the standardized envelope format. The client-side wrapper unwraps the envelope to extract the data. Errors are normalized to provide consistent error handling across all API calls.

**Security Properties**
The system uses session tokens in Authorization headers for authentication. Path sanitization prevents injection attacks. Request ID headers enable audit trails. CORS is handled by Next.js. The system uses fail-closed authorization on authentication failure.

## Trace ID: 3
**Title:** Dashboard Page Load → Server Loader → API Calls → Client Hydration → State Sync

**Description:** Learner dashboard rendering flow from server-side data fetching through client-side hydration and React context synchronization

**Motivation:**
EduBoost Frontend implements a hybrid server/client rendering pattern for the learner dashboard to optimize performance and user experience. The server component (dashboard/page.tsx) fetches initial dashboard data via getLearnerDashboardShellData() before rendering, passing the shell data to the client component (DashboardClient.tsx). The client component hydrates the learner state from the server-provided initial data via useEffect. The fetchData() callback fetches mastery scores and gamification profile in parallel via Promise.all() for efficiency. The mastery data is transformed to percentage scores for UI display. The setMasteryData() update triggers a global context update, which in turn triggers the LearnerContext effect to refresh state. This hybrid approach provides fast initial page load from server data while ensuring fresh client-side data and context synchronization.

**Details:**
- **Dashboard Rendering Flow:** Server Component (dashboard/page.tsx) → getLearnerDashboardShellData() → <DashboardClient {...shellData} /> → Client Component (DashboardClient.tsx) → useEffect: hydrate initial data → if (!learner && initialLearner) → setLearner(initialLearner) → fetchData() callback → Promise.all([...]) → LearnerService.getMastery() → LearnerService.getGamificationProfile() → masteryRes.mastery.forEach() → transform to percentage scores → setMasteryData(() => {...}) → update global context → LearnerContext effect triggers → refreshState() → re-fetch mastery & gamification
- **Hybrid Rendering Architecture:** Server component fetches initial data for fast page load, client component hydrates state from server data, parallel API fetching reduces latency, context synchronization ensures consistency, data transformation for UI display
- **Concurrent Data Fetching:** Promise.all() fetches mastery and gamification in parallel, API calls are independent, no distributed locks needed as React handles state updates, context effects trigger on state changes
- **Covered Objects:** Server component, getLearnerDashboardShellData, DashboardClient, useEffect, setLearner, fetchData, Promise.all, LearnerService, mastery transformation, setMasteryData, LearnerContext, refreshState
- **Timeouts:** Server data fetch: ~200-500ms. Component render: ~5-20ms. Hydration: ~1-5ms. Parallel API fetch: ~200-500ms. Data transformation: <5ms. Context update: ~1-5ms. Total dashboard load: ~412-1040ms
- **Error Handling:** API failures logged, missing data handled gracefully, context errors caught by error boundary, all errors fail closed
- **Security Considerations:** Server-side data fetch validates authentication, learner_id validated by APIs, context cleared on logout, fail-closed on missing data

**Trace text diagram:**
```
Learner Dashboard Page Load Flow
├── Server Component (dashboard/page.tsx)
│   ├── getLearnerDashboardShellData() <-- 3a
│   └── <DashboardClient {...shellData} /> <-- 3b
│
└── Client Component (DashboardClient.tsx)
    ├── useEffect: hydrate initial data <-- DashboardClient.tsx:37
    │   └── if (!learner && initialLearner) <-- 3c
    │       └── setLearner(initialLearner) <-- DashboardClient.tsx:39
    │
    ├── fetchData() callback <-- DashboardClient.tsx:49
    │   ├── Promise.all([...]) <-- 3d
    │   │   ├── LearnerService.getMastery() <-- DashboardClient.tsx:59
    │   │   └── LearnerService.getGamificationProfile() <-- DashboardClient.tsx:60
    │   │
    │   ├── masteryRes.mastery.forEach() <-- 3e
    │   │   └── transform to percentage scores <-- DashboardClient.tsx:67
    │   │
    │   └── setMasteryData(() => {...}) <-- 3f
    │       └── update global context <-- DashboardClient.tsx:73
    │
    └── LearnerContext effect triggers
        └── refreshState() <-- 3g
            └── re-fetch mastery & gamification <-- LearnerContext.tsx:44
```

**Location ID: 3a**
- **Title:** Server Component Data Fetch
- **Description:** Next.js server component fetches initial dashboard data before rendering
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(learner)/dashboard/page.tsx:7

**Location ID: 3b**
- **Title:** Pass Shell Data to Client
- **Description:** Server component passes pre-fetched data to client component for hydration
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/(learner)/dashboard/page.tsx:8

**Location ID: 3c**
- **Title:** Initialize Learner from Props
- **Description:** Client component hydrates learner state from server-provided initial data
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/learner/DashboardClient.tsx:38

**Location ID: 3d**
- **Title:** Parallel Data Fetching
- **Description:** Fetch mastery scores and gamification profile in parallel for efficiency
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/learner/DashboardClient.tsx:58

**Location ID: 3e**
- **Title:** Transform Mastery Data
- **Description:** Convert mastery entries to percentage scores for UI display
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/learner/DashboardClient.tsx:66

**Location ID: 3f**
- **Title:** Update Context State
- **Description:** Update global learner context with fresh mastery and gamification data
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/learner/DashboardClient.tsx:64

**Location ID: 3g**
- **Title:** Context Refresh Trigger
- **Description:** LearnerContext effect triggers state refresh when learner changes
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:65

### AI Guide: Dashboard Page Load → Server Loader → API Calls → Client Hydration → State Sync

**Motivation:**
The hybrid server/client rendering pattern for the learner dashboard optimizes performance by fetching initial data server-side while ensuring fresh client-side data and context synchronization.

**Details:**

**Server-Side Data Fetching**
The server component (dashboard/page.tsx) fetches initial dashboard data via getLearnerDashboardShellData() before rendering [3a]. This provides fast initial page load by pre-fetching data on the server. The shell data is passed to the client component for hydration [3b].

**Client-Side Hydration**
The client component (DashboardClient.tsx) hydrates the learner state from the server-provided initial data via useEffect [3c]. If no learner exists in context but initialLearner is provided, setLearner() initializes the context [3c].

**Parallel Data Fetching**
The fetchData() callback fetches mastery scores and gamification profile in parallel via Promise.all() for efficiency [3d]. This reduces total latency compared to sequential fetching. The mastery data is transformed to percentage scores for UI display [3e].

**Context Synchronization**
The setMasteryData() update triggers a global context update [3f]. This in turn triggers the LearnerContext effect to refresh state via refreshState() [3g]. The context synchronization ensures consistency across all consumers.

**Performance and Security**
Parallel API fetching reduces total latency. Server-side data fetch validates authentication. Learner_id is validated by backend APIs. Context is cleared on logout. The system uses fail-closed authorization on missing data.

## Trace ID: 4
**Title:** Lesson Generation Request → Job Accepted → Polling Loop → Result Cache → Display

**Description:** Async AI lesson generation flow with job submission, status polling, result caching, and interactive lesson display

**Motivation:**
EduBoost Frontend implements async AI lesson generation to handle long-running content creation operations without blocking the UI. The LearnerService.generateLesson() function submits a job request to /lessons/generate and waits for completion via waitForJobResult(). The polling loop checks the job status at /jobs/{job_id} with 500ms intervals and a maximum of 60 attempts. When the job completes, the result is normalized to ensure required fields with fallback values for display. This async pattern prevents UI blocking during potentially long AI generation operations while providing progress feedback through polling. The polling interval balances responsiveness with backend load, and the timeout prevents indefinite waiting. The result normalization ensures the lesson has all required fields for display even if the backend omits some.

**Details:**
- **Lesson Generation Flow:** LearnerService.generateLesson() → Submit job request → POST /lessons/generate → Wait for completion → waitForJobResult() → Polling loop → Check status → GET /jobs/{job_id} → Completion check → return result → Poll delay → sleep(500ms) → Timeout after 60 attempts → Normalize result → Return LessonJobResult
- **Async Job Pattern:** Job submission returns job_id, polling loop checks status at intervals, completion detected via status field, timeout prevents indefinite waiting, result normalization ensures data consistency
- **Polling Strategy:** 500ms intervals balance responsiveness and load, 60 attempts = 30 second timeout, exponential backoff not implemented, network errors handled with retry
- **Covered Objects:** LearnerService, generateLesson, job submission, waitForJobResult, polling loop, job status check, sleep function, timeout handling, result normalization, LessonJobResult
- **Timeouts:** Job submission: ~100-300ms. Polling interval: 500ms. Status check: ~50-100ms. Total polling time: up to 30s. Result normalization: <5ms. Total generation: ~30.1-30.4s
- **Error Handling:** Job submission errors thrown immediately, polling errors logged, timeout throws error, result normalization provides fallbacks, all errors fail closed
- **Security Considerations:** Job requires authentication, job_id validated by backend, result data sanitized, fail-closed on timeout

**Trace text diagram:**
```
Async Lesson Generation Flow
├── LearnerService.generateLesson() <-- services.ts:117
│   ├── Submit job request <-- 4a
│   │   └── POST /lessons/generate <-- services.ts:118
│   └── Wait for completion <-- 4b
│       └── waitForJobResult() <-- client.ts:58
│           ├── Polling loop <-- 4c
│           │   ├── Check status <-- 4d
│           │   │   └── GET /jobs/{job_id} <-- client.ts:64
│           │   ├── Completion check <-- 4e
│           │   │   └── return result <-- client.ts:66
│           │   └── Poll delay <-- 4f
│           │       └── sleep(500ms) <-- client.ts:71
│           └── Timeout after 60 attempts <-- client.ts:73
└── Normalize result <-- 4g
    └── Return LessonJobResult <-- services.ts:122
```

**Location ID: 4a**
- **Title:** Submit Lesson Generation Job
- **Description:** POST to /lessons/generate with subject/topic to start async generation
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/services.ts:118

**Location ID: 4b**
- **Title:** Wait for Job Completion
- **Description:** Poll job status endpoint until lesson generation completes
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/services.ts:122

**Location ID: 4c**
- **Title:** Polling Loop Start
- **Description:** Begin polling loop with 500ms intervals and 60 attempt maximum
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/client.ts:63

**Location ID: 4d**
- **Title:** Check Job Status
- **Description:** GET /jobs/{job_id} to check if lesson generation is complete
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/client.ts:64

**Location ID: 4e**
- **Title:** Job Completion Check
- **Description:** Return result when job status indicates successful completion
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/client.ts:65

**Location ID: 4f**
- **Title:** Polling Interval Delay
- **Description:** Wait 500ms before next polling attempt to avoid overwhelming backend
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/client.ts:71

**Location ID: 4g**
- **Title:** Normalize Lesson Data
- **Description:** Ensure lesson has required fields with fallback values for display
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/services.ts:54

### AI Guide: Lesson Generation Request → Job Accepted → Polling Loop → Result Cache → Display

**Motivation:**
The async lesson generation pattern handles long-running AI content creation operations without blocking the UI, using job submission, status polling, and result normalization to provide a smooth user experience.

**Details:**

**Job Submission**
The LearnerService.generateLesson() function submits a job request to /lessons/generate with subject/topic parameters [4a]. The backend accepts the job and returns a job_id for tracking. The client then waits for completion via waitForJobResult() [4b].

**Polling Loop**
The waitForJobResult() function implements a polling loop that checks the job status at /jobs/{job_id} [4c]. The polling interval is 500ms to balance responsiveness with backend load [4f]. The loop has a maximum of 60 attempts, providing a 30-second timeout [4c].

**Status Check and Completion**
Each polling iteration checks the job status via GET /jobs/{job_id} [4d]. When the job status indicates successful completion, the result is returned [4e]. If the job fails, an error is thrown with the failure message.

**Timeout and Error Handling**
The polling loop throws an error after 60 attempts to prevent indefinite waiting [4c]. Network errors during polling are logged but don't immediately fail. The result normalization ensures the lesson has all required fields with fallback values [4g].

**Performance and Security**
The 500ms polling interval balances responsiveness with backend load. The 30-second timeout prevents indefinite waiting. Job submission requires authentication. Job_id is validated by the backend. Result data is sanitized for display. The system uses fail-closed authorization on timeout.

## Trace ID: 5
**Title:** Diagnostic Start → Item Fetch → Answer Collection → Submit → IRT Scoring → Gap Analysis

**Description:** Adaptive diagnostic assessment flow from item retrieval through answer submission and IRT-based mastery calculation with gap identification

**Motivation:**
EduBoost Frontend implements adaptive diagnostic assessments using Item Response Theory (IRT) to measure learner mastery and identify knowledge gaps. The InteractiveDiagnostic component handles the assessment flow from subject selection through answer collection to submission. The handleStart() function fetches diagnostic items for the learner, filters by subject, and limits to a maximum of 10 questions for reasonable assessment duration. The handleAnswer() function collects learner answers in an array and submits when complete via DiagnosticService.submit(). The backend performs IRT theta calculation on the answers to estimate learner ability. The result display converts the IRT theta score (-3 to +3) to percentage mastery (0-100%) for user-friendly display. This adaptive approach provides accurate mastery estimation with minimal questions while identifying specific knowledge gaps for targeted remediation.

**Details:**
- **Diagnostic Assessment Flow:** InteractiveDiagnostic Component → handleStart() - subject selection → Fetch items API call → Filter by subject → Limit to max questions → handleAnswer() - answer submission → Collect answer in array → Check if last question → Submit when complete → DiagnosticService.submit() → fetchApi POST call → Backend /diagnostics/submit → IRT theta calculation → Result Display → useMemo - theta to mastery % → Render gap report UI
- **Adaptive Assessment Architecture:** Items fetched by learner_id and subject, filtered to relevant content, limited to 10 questions for efficiency, answers collected in array, backend performs IRT scoring, theta converted to percentage for display
- **Concurrent Operations:** Assessment is sequential, no concurrent item fetching, answer collection is synchronous, submission is single request, no distributed locks needed
- **Covered Objects:** InteractiveDiagnostic, handleStart, handleAnswer, DiagnosticService, item fetching, subject filtering, answer collection, submission, IRT calculation, theta conversion, gap report UI
- **Timeouts:** Item fetch: ~200-500ms. Filtering: <5ms. Answer collection: ~1-5ms per answer. Submission: ~200-500ms. IRT calculation: ~100-300ms. Theta conversion: <1ms. Total assessment: ~501-1311ms
- **Error Handling:** Item fetch errors logged, missing items handled gracefully, submission errors displayed, IRT calculation errors logged, all errors fail closed
- **Security Considerations:** Items require authentication, learner_id validated by backend, answers validated server-side, IRT calculation secure, fail-closed on missing data

**Trace text diagram:**
```
Diagnostic Assessment Flow
├── InteractiveDiagnostic Component <-- InteractiveDiagnostic.tsx:15
│   ├── handleStart() - subject selection <-- InteractiveDiagnostic.tsx:43
│   │   ├── Fetch items API call <-- 5a
│   │   ├── Filter by subject <-- 5b
│   │   └── Limit to max questions <-- 5c
│   └── handleAnswer() - answer submission <-- InteractiveDiagnostic.tsx:65
│       ├── Collect answer in array <-- 5d
│       ├── Check if last question <-- InteractiveDiagnostic.tsx:73
│       └── Submit when complete <-- 5e
│           └── DiagnosticService.submit() <-- services.ts:203
│               └── fetchApi POST call <-- 5f
│                   └── Backend /diagnostics/submit
│                       └── IRT theta calculation
└── Result Display <-- InteractiveDiagnostic.tsx:91
    └── useMemo - theta to mastery % <-- 5g
        └── Render gap report UI <-- InteractiveDiagnostic.tsx:94
```

**Location ID: 5a**
- **Title:** Fetch Diagnostic Items
- **Description:** GET diagnostic items for learner from /diagnostics/items/{learner_id}
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:52

**Location ID: 5b**
- **Title:** Filter Items by Subject
- **Description:** Filter diagnostic items to match selected subject for focused assessment
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:53

**Location ID: 5c**
- **Title:** Limit Item Count
- **Description:** Cap diagnostic at 10 questions for reasonable assessment duration
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:54

**Location ID: 5d**
- **Title:** Collect Answer
- **Description:** Append learner's selected option to answers array for submission
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:70

**Location ID: 5e**
- **Title:** Submit Diagnostic Answers
- **Description:** POST answers to /diagnostics/submit for IRT scoring and gap analysis
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:81

**Location ID: 5f**
- **Title:** API Submit Call
- **Description:** Send learner_id and answers to backend for IRT theta calculation
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/lib/api/services.ts:204

**Location ID: 5g**
- **Title:** Convert Theta to Mastery
- **Description:** Transform IRT theta score (-3 to +3) to percentage mastery (0-100%)
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:40

### AI Guide: Diagnostic Start → Item Fetch → Answer Collection → Submit → IRT Scoring → Gap Analysis

**Motivation:**
The adaptive diagnostic assessment uses Item Response Theory (IRT) to measure learner mastery and identify knowledge gaps with minimal questions, providing accurate ability estimation and targeted remediation recommendations.

**Details:**

**Item Fetching and Filtering**
The handleStart() function fetches diagnostic items for the learner via GET /diagnostics/items/{learner_id} [5a]. Items are filtered by subject to focus the assessment on the selected topic [5b]. The item count is limited to 10 questions for reasonable assessment duration [5c].

**Answer Collection**
The handleAnswer() function collects learner answers in an array as they progress through the assessment [5d]. Each answer includes the item_id and selected option. The function checks if this is the last question to trigger submission [5e].

**Submission and IRT Scoring**
When all questions are answered, DiagnosticService.submit() POSTs the learner_id and answers to /diagnostics/submit [5f]. The backend performs IRT theta calculation on the answers to estimate learner ability. The IRT algorithm considers item difficulty and discrimination parameters.

**Result Display and Gap Analysis**
The result display converts the IRT theta score (-3 to +3) to percentage mastery (0-100%) via useMemo for user-friendly display [5g]. The gap report UI shows mastery levels by subject and identifies specific knowledge gaps for targeted remediation.

**Performance and Security**
Item fetching is efficient with subject filtering. The 10-question limit ensures reasonable duration. Answer collection is synchronous for simplicity. IRT calculation is performed server-side for security. Learner_id is validated by the backend. The system uses fail-closed authorization on missing data.

## Trace ID: 6
**Title:** Service Worker Install → Cache Precache → Fetch Intercept → Cache Strategy → Offline Fallback

**Description:** PWA offline capabilities with service worker lifecycle, cache management, and network/cache strategies for different route types

**Motivation:**
EduBoost Frontend implements Progressive Web App (PWA) capabilities with a service worker for offline functionality. The service worker lifecycle includes install, activate, and fetch events. During install, the service worker extracts the precache manifest from the Serwist build manifest, opens the precache cache, and caches all static assets. During activate, the service worker cleans old caches and claims clients to ensure fresh content. The fetch event intercepts all network requests and applies different caching strategies based on route type: API routes use network-only strategy (no caching), authenticated routes use network-only for fresh session data, public routes use network-first with cache fallback, and static assets use cache-first strategy. This multi-strategy approach provides optimal performance and offline availability while ensuring fresh data for dynamic content.

**Details:**
- **Service Worker Lifecycle:** Install Event → Extract precache manifest → Open precache cache → Cache static assets → Activate Event → Clean old caches → Claim clients → Fetch Event Interception → API routes → Network-only → Auth routes → Network-only → Public routes → Network-first → Attempt network fetch → Cache successful response → Fallback to cache on error → Static assets → Cache-first → Check cache → Fetch & cache on miss
- **Caching Strategy Architecture:** API routes bypass cache for fresh data, auth routes require network for session validation, public routes use network-first for freshness, static assets use cache-first for performance, offline fallback provides graceful degradation
- **Cache Management:** Precache during install for static assets, cache-first for static assets, network-first for public pages, cache update on successful network fetch, old cache cleanup on activate
- **Covered Objects:** Service worker, install event, activate event, fetch event, precache manifest, cache API, network requests, cache strategies, offline fallback
- **Timeouts:** Install event: ~500-2000ms. Activate event: ~100-500ms. Cache check: <10ms. Network fetch: ~100-500ms. Cache update: <10ms. Total request handling: ~110-520ms
- **Error Handling:** Network failures fall back to cache, cache misses trigger network fetch, offline fallback returns 503, all errors fail closed
- **Security Considerations:** API routes never cached, auth routes require network, cache keys validated, stale cache cleaned on activate, fail-closed on network failure

**Trace text diagram:**
```
Service Worker Lifecycle & Caching
├── Install Event <-- sw.ts:16
│   ├── Extract precache manifest <-- 6a
│   ├── Open precache cache <-- sw.ts:19
│   └── Cache static assets <-- 6b
├── Activate Event <-- sw.ts:27
│   ├── Clean old caches <-- sw.ts:33
│   └── Claim clients <-- sw.ts:35
└── Fetch Event Interception <-- sw.ts:41
    ├── API routes → Network-only <-- 6c
    ├── Auth routes → Network-only <-- 6d
    ├── Public routes → Network-first <-- sw.ts:58
    │   ├── Attempt network fetch <-- 6e
    │   ├── Cache successful response <-- 6f
    │   └── Fallback to cache on error <-- 6g
    └── Static assets → Cache-first <-- sw.ts:76
        ├── Check cache <-- sw.ts:79
        └── Fetch & cache on miss <-- sw.ts:81
```

**Location ID: 6a**
- **Title:** Extract Precache Manifest
- **Description:** Get list of static assets to precache from Serwist build manifest
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/sw.ts:18

**Location ID: 6b**
- **Title:** Precache Static Assets
- **Description:** Cache all static assets during service worker installation phase
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/sw.ts:20

**Location ID: 6c**
- **Title:** API Route Detection
- **Description:** Identify API requests for network-only strategy (no caching)
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/sw.ts:46

**Location ID: 6d**
- **Title:** Protected Route Check
- **Description:** Detect authenticated routes requiring network-only for fresh session data
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/sw.ts:52

**Location ID: 6e**
- **Title:** Network-First Fetch
- **Description:** Attempt network fetch for public routes with cache fallback on failure
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/sw.ts:62

**Location ID: 6f**
- **Title:** Update Cache on Success
- **Description:** Store successful network response in cache for offline availability
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/sw.ts:64

**Location ID: 6g**
- **Title:** Offline Cache Fallback
- **Description:** Serve cached version when network fails for offline functionality
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/src/app/sw.ts:67

### AI Guide: Service Worker Install → Cache Precache → Fetch Intercept → Cache Strategy → Offline Fallback

**Motivation:**
The service worker implements PWA offline capabilities with a multi-strategy caching approach, providing optimal performance and offline availability while ensuring fresh data for dynamic content.

**Details:**

**Service Worker Installation**
During the install event, the service worker extracts the precache manifest from the Serwist build manifest [6a]. It opens the precache cache and caches all static assets [6b]. This ensures core application assets are available offline from the first visit.

**Service Worker Activation**
During the activate event, the service worker cleans old caches to free storage space [6b]. It claims clients to ensure the new service worker controls all pages immediately [6b]. This ensures fresh content on updates.

**Fetch Event Interception**
The fetch event intercepts all network requests and applies different caching strategies based on route type. API routes use network-only strategy to ensure fresh data [6c]. Authenticated routes also use network-only for fresh session validation [6d].

**Public Routes Strategy**
Public routes use network-first strategy for freshness [6e]. The service worker attempts a network fetch first. On success, the response is cached for offline availability [6f]. On network failure, it falls back to the cached version [6g].

**Static Assets Strategy**
Static assets use cache-first strategy for performance [6b]. The service worker checks the cache first. On cache hit, it returns the cached asset immediately. On cache miss, it fetches from the network and caches the response for future use.

**Performance and Security**
Precaching ensures fast initial load. Network-first for public routes ensures freshness. Cache-first for static assets ensures performance. API routes bypass cache for security. Auth routes require network for session validation. The system uses fail-closed offline fallback.

## Trace ID: 7
**Title:** Route Request → Middleware Check → Session Cookie → Redirect or Allow

**Description:** Next.js middleware authentication guard protecting routes by checking session cookies and redirecting unauthenticated users to login

**Motivation:**
EduBoost Frontend implements Next.js middleware as the first line of defense for route protection. The middleware intercepts requests to protected routes before page handlers execute, providing request-level authentication. The middleware checks for the presence of the eduboost_session httpOnly cookie. If the cookie exists, the request is allowed to proceed to the page handler via NextResponse.next(). If the cookie is missing, the middleware constructs a redirect URL to the login page with a return path parameter, then returns a 307 redirect response. The middleware is configured via a matcher array that specifies which routes trigger middleware execution. This early interception improves security by preventing page rendering for unauthorized users and provides a better user experience by redirecting before loading the page. The dual-layer approach (middleware + RouteGuard) provides defense in depth.

**Details:**
- **Middleware Request Flow:** Incoming request to protected route → middleware() intercepts → Extract session cookie → Check if session exists → hasSession = true → NextResponse.next() → hasSession = false → buildRedirectUrl() → Construct login URL → Set redirect param → Return redirect → Middleware config → matcher: PROTECTED_MATCHERS → [/dashboard, /settings, ...]
- **Route Protection Architecture:** Middleware runs before page handlers, cookie presence checked for authentication, redirect preserves original destination, matcher configuration limits scope, dual-layer with RouteGuard for defense in depth
- **Concurrent Request Handling:** Middleware runs per-request, no shared state, cookie read is atomic, redirect construction is deterministic, no distributed locks needed
- **Covered Objects:** Next.js middleware, NextRequest, NextResponse, cookie store, PROTECTED_MATCHERS configuration, buildRedirectUrl helper, redirect URL construction
- **Timeouts:** Cookie check: <1ms. Redirect construction: ~1-5ms. Response generation: <1ms. Total middleware: ~2-7ms
- **Error Handling:** Missing cookie triggers redirect, cookie read failures logged, redirect construction failures logged, all errors fail closed
- **Security Considerations:** httpOnly cookie prevents XSS, early interception prevents page load, redirect preserves destination, fail-closed on missing cookie, matcher configuration limits scope

**Trace text diagram:**
```
Next.js Request Flow
├── Incoming request to protected route
│   └── middleware() intercepts <-- 7a
│       ├── Extract session cookie <-- 7b
│       ├── Check if session exists
│       │   ├── hasSession = true
│       │   │   └── NextResponse.next() <-- 7c
│       │   └── hasSession = false
│       │       └── buildRedirectUrl() <-- middleware.ts:22
│       │           ├── Construct login URL <-- 7d
│       │           ├── Set redirect param <-- 7e
│       │           └── Return redirect <-- 7f
└── Middleware config <-- middleware.ts:38
    └── matcher: PROTECTED_MATCHERS <-- middleware.ts:39
        └── [/dashboard, /settings, ...] <-- middleware.ts:7
```

**Location ID: 7a**
- **Title:** Middleware Entry Point
- **Description:** Next.js middleware intercepts requests to protected routes before rendering
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:29

**Location ID: 7b**
- **Title:** Check Session Cookie
- **Description:** Verify presence of JWT session cookie for authentication status
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:30

**Location ID: 7c**
- **Title:** Allow Authenticated Request
- **Description:** Pass request through to protected route if valid session exists
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:31

**Location ID: 7d**
- **Title:** Build Login Redirect
- **Description:** Construct login URL with redirect parameter to return after authentication
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:34

**Location ID: 7e**
- **Title:** Preserve Original Destination
- **Description:** Store original requested path in redirect query param for post-login navigation
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:25

**Location ID: 7f**
- **Title:** Redirect to Login
- **Description:** Redirect unauthenticated user to login page with return URL preserved
- **Path:LineNumber:** /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/frontend/middleware.ts:35

### AI Guide: Route Request → Middleware Check → Session Cookie → Redirect or Allow

**Motivation:**
Next.js middleware provides the first line of defense for route protection by intercepting requests before page handlers execute, ensuring request-level authentication and preventing unauthorized page rendering.

**Details:**

**Request Interception**
The middleware function intercepts requests to protected routes before page handlers execute [7a]. This early interception prevents unauthorized users from loading protected pages and provides a better user experience by redirecting before page render.

**Session Cookie Check**
The middleware checks for the presence of the eduboost_session httpOnly cookie [7b]. This cookie presence check is fast and doesn't require validation of the cookie value. The httpOnly flag prevents XSS access.

**Authentication Decision**
If the session cookie exists (hasSession is true), the middleware calls NextResponse.next() to allow the request to proceed to the page handler [7c]. This permits authenticated users to access the protected page.

**Redirect Construction**
When no session cookie is present, buildRedirectUrl() constructs a login URL with the original destination preserved as a query parameter [7d]. The redirect parameter stores the original requested path for post-login navigation [7e].

**Redirect Response**
The middleware returns NextResponse.redirect() with a 307 status code to redirect the user to the login page [7f]. The matcher configuration in config.middleware specifies which routes trigger middleware execution via the PROTECTED_MATCHERS array.

**Security Properties**
The middleware uses httpOnly cookies to prevent XSS access. Early interception prevents page load for unauthorized users. The redirect preserves the original destination for post-login navigation. The system uses fail-closed authorization when the cookie is missing. The matcher configuration limits the scope of middleware execution.
