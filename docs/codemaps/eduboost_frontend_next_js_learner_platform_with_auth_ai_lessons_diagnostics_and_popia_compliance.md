# EduBoost Frontend: Next.js Learner Platform with Auth, AI Lessons, Diagnostics & POPIA Compliance

A Next.js 15 TypeScript frontend featuring authentication flows, AI-generated lesson delivery, adaptive diagnostics with IRT scoring, gamification, parent dashboards with POPIA data rights, offline sync capabilities, and admin content factory tooling. Key entry points: login flow [1b], lesson generation [2c], diagnostic submission [3d], offline sync [5b], and parent data export [6c].

## Trace ID: 1
**Title:** Guardian Login → Learner Selection → Dashboard Navigation

**Description:** Authentication flow: form submission through JWT token storage, parent dashboard fetch, learner context initialization, and redirect to learner dashboard

**Motivation:**
EduBoost Frontend implements a guardian-centric authentication flow where parents/guardians authenticate and then select which learner to manage. The LoginPage component handles form submission with email/password credentials, calling AuthService.loginGuardian() which POSTs to /auth/login endpoint. The JWT access token is stored in localStorage via storeAccessToken() for subsequent authenticated requests. After successful authentication, the parent dashboard is fetched via ParentService.getDashboard() to retrieve the guardian's learner list and subscription info. The first learner from the dashboard is used to initialize the learner context via setLearner(), which triggers LearnerContext effect to persist the learner to localStorage and refresh state. Finally, the user is navigated to the dashboard via router.push("/dashboard"). This flow ensures secure authentication, proper session management, and seamless transition to the learner dashboard.

**Details:**
- **Execution Flow:** LoginPage component → Form submission handler → AuthService.loginGuardian() → fetchApi POST /auth/login → storeAccessToken() → Fetch parent dashboard → ParentService.getDashboard() → GET /parents/dashboard → Initialize learner context → setLearner() call → LearnerContext effect → localStorage.setItem() → refreshState() → Navigation → router.push("/dashboard")
- **Concurrency Safety:** Form submission is per-request. Token storage is synchronous. Dashboard fetch is async. Context updates are batched. No distributed locks needed
- **Covered Objects:** Authentication, JWT token storage, parent dashboard, learner context, localStorage, navigation
- **Timeouts:** Login request: ~200-500ms. Dashboard fetch: ~200-500ms. Context update: ~10-50ms. Total: ~410-1050ms
- **Migration Path:** From simple auth to guardian flow. Migration requires: 1) Add guardian login, 2) Implement learner selection, 3) Add context management, 4) Update navigation
- **Error Handling:** Login failures return 401. Dashboard errors logged. Context errors handled gracefully. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Store tokens securely. Validate credentials. Use HTTPS. Implement token refresh. Clear tokens on logout. Validate learner access

**Trace text diagram:**
```
Guardian Login Flow
├── LoginPage component <-- page.tsx:60
│   ├── Form submission handler <-- 1a
│   │   └── AuthService.loginGuardian() <-- 1b
│   │       └── fetchApi POST /auth/login <-- services.ts:72
│   │           └── storeAccessToken() <-- 1c
│   ├── Fetch parent dashboard <-- 1d
│   │   └── ParentService.getDashboard() <-- services.ts:181
│   │       └── GET /parents/dashboard
│   └── Initialize learner context <-- 1e
│       └── setLearner() call <-- page.tsx:92
│           └── LearnerContext effect <-- LearnerContext.tsx:65
│               ├── localStorage.setItem() <-- 1f
│               └── refreshState() <-- LearnerContext.tsx:68
└── Navigation <-- 1g
    └── router.push("/dashboard") <-- page.tsx:102
```

**Location ID: 1a**
- **Title:** Login Form Submission
- **Description:** User submits email/password credentials to authenticate as guardian
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:77

**Location ID: 1b**
- **Title:** API Login Request
- **Description:** POST to /auth/login endpoint with credentials
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:72

**Location ID: 1c**
- **Title:** JWT Token Storage
- **Description:** Store access token in localStorage for subsequent authenticated requests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:77

**Location ID: 1d**
- **Title:** Fetch Parent Dashboard
- **Description:** Retrieve guardian's learner list and subscription info
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:84

**Location ID: 1e**
- **Title:** Initialize Learner Context
- **Description:** Set active learner in global context from first learner in dashboard
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:92

**Location ID: 1f**
- **Title:** Persist Learner to Storage
- **Description:** Save learner profile to localStorage for session persistence
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:67

**Location ID: 1g**
- **Title:** Navigate to Dashboard
- **Description:** Redirect authenticated user to learner dashboard
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(auth)/login/page.tsx:102

### AI Guide: Guardian Login Flow

**Motivation:**
The guardian login flow authenticates parents/guardians and initializes learner context for dashboard navigation. This flow ensures that authenticated users can access their children's learning data while maintaining session persistence across page reloads.

**Details:**

**Authentication**
The login form submission processes user credentials through a form handler [1a]. The API login request POSTs to /auth/login for credential validation and receives a JWT token response [1b]. The JWT token is stored in localStorage for session persistence and authenticated requests [1c].

**Dashboard and Context**
After authentication, the parent dashboard is fetched to get the learner list, subscription info, and guardian data [1d]. The learner context is initialized by setting the active learner in global context for state management [1e]. The learner is persisted to storage using localStorage.setItem() for session persistence and context sync [1f].

**Navigation**
The user is navigated to the dashboard using router.push() for redirect to dashboard [1g]. This completes the login flow and provides access to the guardian's dashboard.

## Trace ID: 2
**Title:** AI Lesson Generation → Job Polling → Interactive Display → XP Award

**Description:** Lesson delivery flow: subject/topic selection triggers async generation job, polls for completion, caches result, displays interactive content, and awards gamification XP on completion

**Motivation:**
EduBoost Frontend implements async AI lesson generation with job polling for optimal user experience. When a user selects subject/topic in the UI, handleGenerate() is triggered, calling LearnerService.generateLesson() which POSTs to /lessons/generate. The backend accepts the async job and returns JobAcceptedResponse with a job_id. The frontend then calls waitForJobResult() which implements a polling loop at 500ms intervals, calling GET /jobs/{job_id} to check status until complete. Once the lesson is ready, cacheLessonSnapshot() stores it in localStorage for offline access. When the user completes the lesson, LearnerService.awardXP() POSTs to /gamification/award-xp to grant 35 XP. Finally, refreshState() calls Promise.all([getMastery, getGam]) to update the context with new XP/level. This async pattern prevents blocking the UI, provides progress feedback, and enables offline access.

**Details:**
- **Execution Flow:** User selects subject/topic in UI → handleGenerate() triggered → LearnerService.generateLesson() → POST /lessons/generate → Backend accepts async job → Returns JobAcceptedResponse → waitForJobResult() → Polling loop (500ms interval) → GET /jobs/{job_id} → Check status until complete → Lesson ready, cache & display → cacheLessonSnapshot() → Store in localStorage → User completes lesson → LearnerService.awardXP() → POST /gamification/award-xp → refreshState() → Promise.all([getMastery, getGam]) → Update context with new XP/level
- **Concurrency Safety:** Job polling is per-request. Caching is synchronous. XP award is atomic. Context updates are batched. No distributed locks needed
- **Covered Objects:** AI lesson generation, job polling, offline caching, gamification XP, context updates
- **Timeouts:** Lesson generation: ~1-5s. Polling: ~500ms intervals. Caching: ~10-50ms. XP award: ~200-500ms. Context update: ~200-500ms. Total: ~1.5-6.5s
- **Migration Path:** From sync to async generation. Migration requires: 1) Implement job polling, 2) Add caching, 3) Update UI for async, 4) Add XP award
- **Error Handling:** Generation failures logged. Polling timeouts handled. Caching errors logged. XP errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate lesson content. Cache securely. Award XP server-side. Validate completion. Check quotas. Filter sensitive data

**Trace text diagram:**
```
Lesson Generation Flow (Trace 2)
├── User selects subject/topic in UI
│   └── handleGenerate() triggered <-- page.tsx:42
│       └── LearnerService.generateLesson() <-- 2a
│           ├── POST /lessons/generate <-- 2b
│           │   └── Backend accepts async job
│           │       └── Returns JobAcceptedResponse
│           └── waitForJobResult() <-- 2c
│               └── Polling loop (500ms interval) <-- client.ts:188
│                   └── GET /jobs/{job_id} <-- 2d
│                       └── Check status until complete <-- client.ts:190
└── Lesson ready, cache & display
    ├── cacheLessonSnapshot() <-- 2e
    │   └── Store in localStorage <-- offlineSync.ts:69
    ├── User completes lesson
    │   └── LearnerService.awardXP() <-- 2f
    │       └── POST /gamification/award-xp <-- services.ts:141
    └── refreshState() <-- 2g
        └── Promise.all([getMastery, getGam]) <-- 2h
            └── Update context with new XP/level <-- LearnerContext.tsx:58
```

**Location ID: 2a**
- **Title:** Request Lesson Generation
- **Description:** Submit learner_id, subject, topic, and language to lesson generation service
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:53

**Location ID: 2b**
- **Title:** POST Lesson Job
- **Description:** Backend accepts job and returns job_id for async processing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:122

**Location ID: 2c**
- **Title:** Poll Job Until Complete
- **Description:** Poll /jobs/{job_id} endpoint every 500ms until lesson generation completes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:126

**Location ID: 2d**
- **Title:** Check Job Status
- **Description:** Fetch current job status and result payload from backend
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:189

**Location ID: 2e**
- **Title:** Cache Lesson for Offline
- **Description:** Store generated lesson in localStorage for offline access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:66

**Location ID: 2f**
- **Title:** Award Completion XP
- **Description:** Grant 35 XP to learner for completing the lesson
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:104

**Location ID: 2g**
- **Title:** Refresh Learner State
- **Description:** Update mastery data and gamification profile from backend
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:112

**Location ID: 2h**
- **Title:** Fetch Updated Progress
- **Description:** Parallel fetch of mastery scores and gamification profile
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:45

### AI Guide: AI Lesson Generation

**Motivation:**
Async AI lesson generation with job polling provides optimal user experience with progress feedback and offline caching. The async job pattern prevents long-running requests from blocking the UI, while polling provides status updates and offline caching ensures lessons are available without network connectivity.

**Details:**

**Job Submission and Polling**
The lesson generation request submits learner parameters via a service call [2a]. The backend accepts the job via POST and returns a job_id for async processing [2b]. The client polls the job until complete using a polling loop with 500ms intervals for status checks [2c]. The job status check fetches the status, result payload, and completion check [2d].

**Caching and XP**
The lesson is cached in localStorage for offline access and later sync [2e]. Completion XP is awarded (35 XP) with gamification update and server-side validation [2f]. The learner state is refreshed to update context, mastery data, and gamification profile [2g]. Updated progress is fetched in parallel for efficiency and context update [2h].
- Context stale: Check refresh

## Trace ID: 3
**Title:** Diagnostic Assessment → IRT Scoring → Gap Analysis → Study Plan Update

**Description:** Adaptive diagnostic flow: fetch IRT-calibrated items, collect answers, submit for theta estimation, receive ranked knowledge gaps, update mastery context, and redirect to personalized study plan

**Motivation:**
EduBoost Frontend implements adaptive diagnostic assessments using IRT (Item Response Theory) for accurate ability estimation. The InteractiveDiagnostic component handles the assessment flow: handleStart() selects subject and calls DiagnosticService.getItems() which GETs /diagnostics/items to fetch IRT-calibrated items with difficulty parameters. handleAnswer() accumulates learner's selected options for each diagnostic item. On the final question, DiagnosticService.submit() POSTs to /diagnostics/submit for backend IRT theta estimation. The results display converts theta to mastery % using the formula ((theta + 3) / 6) * 100 for UI display, and shows ranked knowledge gaps. The DiagnosticPage wrapper's onComplete callback updates mastery in context and navigates to the study plan. This adaptive approach provides accurate ability measurement, personalized gap identification, and seamless transition to remediation.

**Details:**
- **Execution Flow:** InteractiveDiagnostic Component → handleStart() - subject selection → DiagnosticService.getItems() → fetchApi GET /diagnostics/items → Backend: IRT item selection → handleAnswer() - per-question flow → Accumulate answer in array → On final question: → DiagnosticService.submit() → POST /diagnostics/submit → Backend: IRT theta estimation → Results display → Convert theta to mastery % → Show ranked knowledge gaps → DiagnosticPage wrapper → onComplete callback → Update mastery in context → Navigate to study plan → LearnerContext state update
- **Concurrency Safety:** Item fetch is per-request. Answer accumulation is synchronous. Submit is atomic. Context updates are batched. No distributed locks needed
- **Covered Objects:** Adaptive diagnostics, IRT scoring, theta estimation, gap analysis, mastery conversion, study plan navigation
- **Timeouts:** Item fetch: ~200-500ms. Answer collection: ~1-5ms per item. Submit: ~500-1000ms. Theta conversion: ~1-5ms. Context update: ~200-500ms. Total: ~1-3s
- **Migration Path:** From static to adaptive diagnostics. Migration requires: 1) Implement IRT items, 2) Add adaptive selection, 3) Implement theta estimation, 4) Add gap analysis
- **Error Handling:** Item fetch errors logged. Submit errors logged. Theta conversion errors handled. Context errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate item content. Secure answer submission. Validate theta calculation. Protect learner data. Audit diagnostic results. Filter sensitive data

**Trace text diagram:**
```
Diagnostic Assessment Flow
├── InteractiveDiagnostic Component <-- InteractiveDiagnostic.tsx:15
│   ├── handleStart() - subject selection <-- InteractiveDiagnostic.tsx:43
│   │   └── DiagnosticService.getItems() <-- 3a
│   │       └── fetchApi GET /diagnostics/items <-- 3b
│   │           └── Backend: IRT item selection
│   ├── handleAnswer() - per-question flow <-- InteractiveDiagnostic.tsx:65
│   │   ├── Accumulate answer in array <-- 3c
│   │   └── On final question: <-- InteractiveDiagnostic.tsx:73
│   │       └── DiagnosticService.submit() <-- 3d
│   │           └── POST /diagnostics/submit <-- 3e
│   │               └── Backend: IRT theta estimation
│   └── Results display <-- InteractiveDiagnostic.tsx:91
│       ├── Convert theta to mastery % <-- 3f
│       └── Show ranked knowledge gaps <-- InteractiveDiagnostic.tsx:119
└── DiagnosticPage wrapper <-- page.tsx:8
    ├── onComplete callback <-- page.tsx:19
    │   ├── Update mastery in context <-- 3g
    │   └── Navigate to study plan <-- 3h
    └── LearnerContext state update
```

**Location ID: 3a**
- **Title:** Fetch Diagnostic Items
- **Description:** Retrieve adaptive assessment items for selected subject
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:52

**Location ID: 3b**
- **Title:** GET Diagnostic Items API
- **Description:** Backend returns IRT-calibrated items with difficulty parameters
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:190

**Location ID: 3c**
- **Title:** Collect Answer
- **Description:** Accumulate learner's selected options for each diagnostic item
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:70

**Location ID: 3d**
- **Title:** Submit for IRT Scoring
- **Description:** POST answers to backend for theta estimation and gap identification
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:81

**Location ID: 3e**
- **Title:** Diagnostic Submit Endpoint
- **Description:** Backend runs IRT algorithm to compute theta_after and ranked_gaps
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:207

**Location ID: 3f**
- **Title:** Convert Theta to Mastery %
- **Description:** Transform IRT theta score to 0-100 mastery percentage for UI display
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:40

**Location ID: 3g**
- **Title:** Update Mastery Context
- **Description:** Store computed mastery score in global learner context
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/diagnostic/page.tsx:20

**Location ID: 3h**
- **Title:** Navigate to Study Plan
- **Description:** Redirect to personalized study plan page after diagnostic completion
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/diagnostic/page.tsx:21

### AI Guide: Diagnostic Assessment

**Motivation:**
Adaptive diagnostic assessments use IRT (Item Response Theory) for accurate ability estimation and gap analysis. This psychometric approach provides precise measurement of learner ability and identifies knowledge gaps for personalized remediation.

**Details:**

**Item Fetching**
Diagnostic items are retrieved with subject selection for IRT-calibrated adaptive items [3a]. The GET diagnostic items API returns items with difficulty parameters for adaptive selection [3b]. These items are selected based on the learner's estimated ability to maximize information gain.

**Answer Collection and Scoring**
Answers are accumulated in an array with per-question flow [3c]. The answers are submitted for IRT scoring via POST for theta estimation and gap identification [3d]. The diagnostic submit endpoint uses the backend IRT algorithm to compute theta_after and rank gaps [3e].

**Mastery and Navigation**
Theta is converted to mastery percentage (0-100) for UI display [3f]. The mastery context is updated by storing in context for global state and mastery score [3g]. The user is navigated to the study plan for personalized path and remediation [3h].
- Navigation errors: Check router

## Trace ID: 4
**Title:** API Error Handling → Token Refresh → Retry Logic → Normalized Error Display

**Description:** Resilient API client: intercepts 401 errors, attempts token refresh via refresh endpoint, retries original request with new token, normalizes error responses into ApiError objects for consistent UI handling

**Motivation:**
EduBoost Frontend implements a resilient API client with automatic token refresh and normalized error handling. The fetchApi() entrypoint executes HTTP requests with JWT token in Authorization header. On response, parseJson() parses the payload. If status is 401 and retryOnUnauthorized is true, refreshAccessToken() is called, which POSTs to /auth/refresh with httpOnly cookie to get new access token. The new token is stored via storeAccessToken(). The original request is retried with the new token (retryOnUnauthorized=false to prevent infinite loops). If the response is not OK, normalizeApiError() transforms various backend error formats into consistent ApiError structure, parsing envelope.error, FastAPI detail strings, and validation errors. This resilient pattern provides seamless token refresh, consistent error handling, and improved user experience.

**Details:**
- **Execution Flow:** fetchApi() entrypoint → fetch(url, headers + JWT) → await parseJson(response) → Error handling branch → if (status === 401 && retryOnUnauthorized) → refreshAccessToken() → POST /auth/refresh → parseJson(response) → storeAccessToken(token) → Retry: fetchApi(endpoint, retryOnUnauthorized=false) → if (!response.ok) → throw new ApiError(normalizeApiError()) → normalizeApiError() helper → Parse envelope.error → Parse FastAPI detail string → Parse validation errors → Return NormalizedApiError
- **Concurrency Safety:** Token refresh is atomic. Retry is sequential. Error normalization is stateless. No distributed locks needed
- **Covered Objects:** API error handling, token refresh, retry logic, error normalization, JWT management
- **Timeouts:** API request: ~200-500ms. Token refresh: ~200-500ms. Retry: ~200-500ms. Error normalization: ~1-5ms. Total: ~400-1505ms
- **Migration Path:** From simple fetch to resilient client. Migration requires: 1) Add token refresh, 2) Implement retry logic, 3) Normalize errors, 4) Update error handling
- **Error Handling:** 401 errors trigger refresh. Refresh failures logged. Retry failures handled. Normalized errors thrown. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Use httpOnly cookies. Validate refresh tokens. Prevent infinite retries. Normalize errors safely. Filter sensitive data. Handle token expiry

**Trace text diagram:**
```
API Request Flow with Token Refresh
├── fetchApi() entrypoint <-- client.ts:146
│   ├── fetch(url, headers + JWT) <-- 4a
│   ├── await parseJson(response) <-- client.ts:159
│   └── Error handling branch
│       ├── if (status === 401 && retryOnUnauthorized) <-- 4b
│       │   └── refreshAccessToken() <-- 4c
│       │       ├── POST /auth/refresh <-- 4d
│       │       ├── parseJson(response) <-- client.ts:136
│       │       └── storeAccessToken(token) <-- 4e
│       ├── Retry: fetchApi(endpoint, retryOnUnauthorized=false) <-- 4f
│       └── if (!response.ok) <-- client.ts:166
│           └── throw new ApiError(normalizeApiError()) <-- 4g
│
└── normalizeApiError() helper <-- client.ts:90
    ├── Parse envelope.error <-- client.ts:93
    ├── Parse FastAPI detail string <-- 4h
    ├── Parse validation errors <-- client.ts:101
    └── Return NormalizedApiError <-- client.ts:122
```

**Location ID: 4a**
- **Title:** Execute API Request
- **Description:** Send HTTP request with JWT token in Authorization header
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:158

**Location ID: 4b**
- **Title:** Detect Token Expiry
- **Description:** Intercept 401 Unauthorized responses for automatic token refresh
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:161

**Location ID: 4c**
- **Title:** Attempt Token Refresh
- **Description:** POST to /auth/refresh with httpOnly cookie to get new access token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:162

**Location ID: 4d**
- **Title:** Refresh Token Request
- **Description:** Backend validates refresh token cookie and issues new access token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:131

**Location ID: 4e**
- **Title:** Store New Token
- **Description:** Update localStorage with fresh access token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:142

**Location ID: 4f**
- **Title:** Retry Original Request
- **Description:** Re-execute failed request with new token (retryOnUnauthorized=false)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:163

**Location ID: 4g**
- **Title:** Normalize Error Response
- **Description:** Transform various backend error formats into consistent ApiError structure
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:167

**Location ID: 4h**
- **Title:** Extract Error Message
- **Description:** Parse FastAPI validation errors and detail strings into normalized format
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/client.ts:98

### AI Guide: API Error Handling

**Motivation:**
Resilient API client with automatic token refresh and normalized error handling provides seamless user experience. The automatic token refresh prevents session expiration from interrupting the user, while normalized error handling provides consistent error messages across all API failures.

**Details:**

**Token Refresh**
The API request executes with JWT in the header for authorization [4a]. Token expiry is detected by intercepting 401 responses, checking the retry flag, and triggering refresh [4b]. The token refresh attempts a POST to refresh with httpOnly cookie for new token [4c]. The refresh token request validates on the backend, issues a new token, and uses cookie-based storage [4d]. The new token is stored in localStorage for fresh token and authenticated requests [4e].

**Retry and Error Normalization**
The original request is retried with the new token, preventing infinite loops with sequential retry [4f]. Error responses are normalized to transform errors into a consistent structure with ApiError object [4g]. Error messages are extracted by parsing FastAPI errors, detail strings, and validation errors [4h]. This provides consistent error handling across all API failures.
- Error display: Check normalization

## Trace ID: 5
**Title:** Offline Lesson Completion → Queue → Online Detection → Backend Sync

**Description:** Offline-first sync: detect offline state, queue lesson completion events to localStorage, monitor online status, flush queued events to backend when connection restored

**Motivation:**
EduBoost Frontend implements offline-first sync for lesson completions to ensure functionality without network connectivity. The Lesson Page component checks network status via navigator.onLine before attempting lesson completion sync. If offline, queueLessonSync() is called via offlineSync.queueLessonSync(), which reads the current queue from localStorage, appends the event to the array, and persists to localStorage as JSON. When the sync service detects online status via flushOfflineLessonSync(), it verifies online status, reads queued events, and POSTs to backend sync endpoint via LearnerService.syncLessonResponses() which calls fetchApi("/lessons/sync"). The backend processes queued lesson completions and awards XP. Finally, the sync service clears the localStorage queue. This offline-first pattern ensures data integrity, seamless offline experience, and automatic sync when connectivity is restored.

**Details:**
- **Execution Flow:** Lesson Page Component → Check network status → Queue offline event → offlineSync.queueLessonSync() → Read current queue → Append event to array → Persist to localStorage → Sync Service (when online) → offlineSync.flushOfflineLessonSync() → Verify online status → Read queued events → POST to backend sync endpoint → LearnerService.syncLessonResponses() → fetchApi("/lessons/sync") → Clear localStorage queue
- **Concurrency Safety:** Queue operations are atomic. Online detection is synchronous. Sync is sequential. No distributed locks needed
- **Covered Objects:** Offline sync, localStorage queue, network detection, backend sync, lesson completion
- **Timeouts:** Network check: ~1-5ms. Queue operation: ~1-5ms. Sync operation: ~200-500ms. Total: ~202-510ms
- **Migration Path:** From online-only to offline-first. Migration requires: 1) Add network detection, 2) Implement queue, 3) Add sync service, 4) Handle conflicts
- **Error Handling:** Network errors logged. Queue errors handled. Sync errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate queued events. Encrypt localStorage. Handle conflicts. Validate sync results. Filter sensitive data. Audit sync operations

**Trace text diagram:**
```
Offline Lesson Completion Flow
├── Lesson Page Component
│   ├── Check network status <-- 5a
│   └── Queue offline event <-- 5b
│       └── offlineSync.queueLessonSync() <-- offlineSync.ts:35
│           ├── Read current queue <-- offlineSync.ts:36
│           ├── Append event to array <-- 5c
│           └── Persist to localStorage <-- 5d
│
└── Sync Service (when online)
    └── offlineSync.flushOfflineLessonSync() <-- offlineSync.ts:41
        ├── Verify online status <-- 5e
        ├── Read queued events <-- offlineSync.ts:47
        ├── POST to backend sync endpoint <-- 5f
        │   └── LearnerService.syncLessonResponses() <-- 5g
        │       └── fetchApi("/lessons/sync") <-- services.ts:135
        └── Clear localStorage queue <-- 5h
```

**Location ID: 5a**
- **Title:** Detect Offline State
- **Description:** Check navigator.onLine before attempting lesson completion sync
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:91

**Location ID: 5b**
- **Title:** Queue Offline Event
- **Description:** Add lesson completion event to localStorage sync queue
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/lesson/page.tsx:92

**Location ID: 5c**
- **Title:** Append to Queue
- **Description:** Add event to in-memory queue array
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:36

**Location ID: 5d**
- **Title:** Persist Queue to Storage
- **Description:** Serialize queue to localStorage as JSON
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:37

**Location ID: 5e**
- **Title:** Check Online Before Flush
- **Description:** Verify network connectivity before attempting sync
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:43

**Location ID: 5f**
- **Title:** Bulk Sync to Backend
- **Description:** POST queued events to /lessons/sync endpoint
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:52

**Location ID: 5g**
- **Title:** Sync Endpoint Call
- **Description:** Backend processes queued lesson completions and awards XP
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:134

**Location ID: 5h**
- **Title:** Clear Synced Queue
- **Description:** Remove successfully synced events from localStorage
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/offlineSync.ts:54

### AI Guide: Offline Sync

**Motivation:**
Offline-first sync ensures lesson completions work without network connectivity, with automatic sync when connection is restored. This pattern allows users to continue learning even without internet access, with their progress automatically synchronized when connectivity returns.

**Details:**

**Offline Detection and Queuing**
The offline state is detected by checking navigator.onLine for network detection and status check [5a]. Offline events are queued by adding to the sync queue in localStorage for event persistence [5b]. Events are appended to an in-memory array for queue management [5c]. The queue is persisted to storage by serializing to JSON in localStorage for data persistence [5d].

**Sync and Cleanup**
Connectivity is checked before flushing to verify network status and trigger sync [5e]. Queued events are bulk synced to the backend via POST for bulk operation and backend sync [5f]. The sync endpoint call handles backend processing, XP award, and completion handling [5g]. Synced events are cleared from the queue to remove synced events, perform queue cleanup, and update localStorage [5h].
- XP not awarded: Check sync

## Trace ID: 6
**Title:** Parent Dashboard → POPIA Data Export → Privacy Request Handling

**Description:** POPIA compliance flow: load parent trust dashboard with learner progress, trigger data export request, backend generates JSON/CSV bundle, display export status and download link

**Motivation:**
EduBoost Frontend implements POPIA (Protection of Personal Information Act) compliance features for data subject rights. The ParentDashboard component mounts and performs parallel data fetch: GET /parents/{id}/dashboard returns learner progress & IRT theta, and GET /parents/{id}/export returns export bundle links. Privacy action button clicks trigger export request handler which calls DataRightsService.exportLearner() to GET /popia/data-export/{id} with format parameter, causing the backend to generate JSON/CSV bundle. The UI updates with export filename and download availability. Erasure request handler calls DataRightsService.requestErasure() to POST /popia/deletion-request with audit reason, triggering audit log + deletion queue per POPIA Section 24 (right to be forgotten). This compliance flow ensures data subject rights, audit trails, and regulatory compliance.

**Details:**
- **Execution Flow:** ParentDashboard component mount → Parallel data fetch → GET /parents/{id}/dashboard → Returns learner progress & IRT theta → GET /parents/{id}/export → Returns export bundle links → Privacy action button click → Export request handler → DataRightsService.exportLearner() → GET /popia/data-export/{id} → Backend generates JSON/CSV → Update UI with filename → Erasure request handler → DataRightsService.requestErasure() → POST /popia/deletion-request → Audit log + deletion queue
- **Concurrency Safety:** Parallel fetch is concurrent. Export generation is async. Erasure is atomic. No distributed locks needed
- **Covered Objects:** POPIA compliance, data export, data erasure, parent dashboard, audit logs, deletion queue
- **Timeouts:** Dashboard fetch: ~200-500ms. Export fetch: ~200-500ms. Export generation: ~1-5s. Erasure request: ~200-500ms. Total: ~1.6-6.5s
- **Migration Path:** From basic dashboard to POPIA compliance. Migration requires: 1) Add export endpoints, 2) Implement erasure requests, 3) Add audit logging, 4) Update UI
- **Error Handling:** Fetch errors logged. Export errors logged. Erasure errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate guardian access. Audit all requests. Secure export generation. Validate erasure requests. Filter sensitive data. Comply with POPIA

**Trace text diagram:**
```
Parent Dashboard POPIA Compliance Flow
├── ParentDashboard component mount <-- ParentDashboard.tsx:16
│   ├── Parallel data fetch <-- 6a
│   │   ├── GET /parents/{id}/dashboard <-- 6b
│   │   │   └── Returns learner progress & IRT theta
│   │   └── GET /parents/{id}/export <-- services.ts:185
│   │       └── Returns export bundle links
│   └── Privacy action button click <-- ParentDashboard.tsx:57
│       ├── Export request handler <-- ParentDashboard.tsx:60
│       │   ├── DataRightsService.exportLearner() <-- 6c
│       │   │   └── GET /popia/data-export/{id} <-- 6d
│       │   │       └── Backend generates JSON/CSV
│       │   └── Update UI with filename <-- 6e
│       └── Erasure request handler <-- ParentDashboard.tsx:67
│           ├── DataRightsService.requestErasure() <-- 6f
│           └── POST /popia/deletion-request <-- 6g
│               └── Audit log + deletion queue
```

**Location ID: 6a**
- **Title:** Load Parent Dashboard
- **Description:** Parallel fetch of trust dashboard and export bundle for guardian
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/ParentDashboard.tsx:35

**Location ID: 6b**
- **Title:** Fetch Trust Dashboard
- **Description:** GET learner progress summaries, IRT theta, knowledge gaps, and AI insights
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:183

**Location ID: 6c**
- **Title:** Request Data Export
- **Description:** Trigger POPIA-compliant data export for specific learner
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/ParentDashboard.tsx:61

**Location ID: 6d**
- **Title:** Data Export API Call
- **Description:** GET /popia/data-export/{learnerId} with format parameter
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:164

**Location ID: 6e**
- **Title:** Display Export Status
- **Description:** Update UI with export filename and download availability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/ParentDashboard.tsx:62

**Location ID: 6f**
- **Title:** Request Data Erasure
- **Description:** POST erasure request under POPIA Section 24 (right to be forgotten)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/ParentDashboard.tsx:67

**Location ID: 6g**
- **Title:** Erasure Request API
- **Description:** POST /popia/deletion-request/{learnerId} with audit reason
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:166

### AI Guide: POPIA Data Export

**Motivation:**
POPIA compliance features enable data export and erasure for data subject rights. These features ensure that the platform complies with South Africa's Protection of Personal Information Act by giving guardians control over their children's data.

**Details:**

**Dashboard Loading**
The parent dashboard is loaded with parallel fetch for trust dashboard and export bundle [6a]. The trust dashboard fetches learner progress, IRT theta, and knowledge gaps [6b]. This provides guardians with visibility into their children's learning progress.

**Data Export**
Data export is requested to trigger export for POPIA compliance with learner-specific data [6c]. The data export API call uses GET export endpoint with format parameter for JSON/CSV [6d]. The export status is displayed in the UI with filename and download availability [6e].

**Data Erasure**
Data erasure is requested via POST for POPIA Section 24 right to be forgotten [6f]. The erasure request API uses POST deletion endpoint with audit reason and deletion queue [6g]. All requests are audited for compliance verification.

## Trace ID: 7
**Title:** App Initialization → Context Provider → localStorage Hydration → Route Guard

**Description:** Application bootstrap: root layout mounts LearnerProvider, reads persisted learner from localStorage, initializes global context, route guards check authentication state before rendering protected routes

**Motivation:**
EduBoost Frontend implements application bootstrap with context provider, localStorage hydration, and route guards for protected routes. The Root Layout (_app) mounts <LearnerProvider> wrapper which wraps the entire app in LearnerProvider for global state management. On mount, useEffect reads persisted learner from localStorage via localStorage.getItem(), JSON parses and sets learner via setLearner(), and calls refreshState() to fetch fresh state via Promise.all([...]) for mastery and gamification data. The Learner Layout (protected routes) checks if learner exists, and if not, uses <RouteGuard required="learner"> to evaluate route permission. RouteGuard checks allowed = Boolean(learner) and if not allowed, redirects via router.push("/"). The Parent Dashboard uses <RouteGuard required="parent"> with allowed = hasGuardianToken() and redirects to /login if not allowed. This bootstrap pattern ensures session persistence, protected routes, and proper authentication checks.

**Details:**
- **Execution Flow:** Root Layout (_app) → <LearnerProvider> wrapper → useEffect on mount → localStorage.getItem() → JSON.parse & setLearner() → refreshState() call → Promise.all([...]) → Learner Layout (protected routes) → if (!learner) check → <RouteGuard required="learner"> → allowed = Boolean(learner) → if (!allowed) → router.push("/") → Parent Dashboard (protected routes) → <RouteGuard required="parent"> → allowed = hasGuardianToken() → if (!allowed) → router.push("/login")
- **Concurrency Safety:** localStorage is synchronous. Context updates are batched. Route guards are deterministic. No distributed locks needed
- **Covered Objects:** App initialization, context provider, localStorage hydration, route guards, authentication checks
- **Timeouts:** localStorage read: ~1-5ms. JSON parse: ~1-5ms. Context update: ~10-50ms. State refresh: ~200-500ms. Route guard: ~1-5ms. Total: ~213-565ms
- **Migration Path:** From simple layout to guarded routes. Migration requires: 1) Add context provider, 2) Implement localStorage hydration, 3) Add route guards, 4. Update layouts
- **Error Handling:** localStorage errors handled gracefully. Parse errors logged. State refresh errors logged. Guard errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate localStorage data. Clear on logout. Check authentication. Protect routes. Validate tokens. Filter sensitive data

**Trace text diagram:**
```
Next.js App Initialization & Route Protection
├── Root Layout (_app) <-- layout.tsx:53
│   └── <LearnerProvider> wrapper <-- 7a
│       └── useEffect on mount <-- LearnerContext.tsx:30
│           ├── localStorage.getItem() <-- 7b
│           ├── JSON.parse & setLearner() <-- 7c
│           └── refreshState() call <-- 7d
│               └── Promise.all([...]) <-- LearnerContext.tsx:45
├── Learner Layout (protected routes) <-- layout.tsx:10
│   └── if (!learner) check <-- 7e
│       └── <RouteGuard required="learner"> <-- layout.tsx:21
│           ├── allowed = Boolean(learner) <-- 7f
│           └── if (!allowed) <-- RouteGuard.tsx:25
│               └── router.push("/") <-- 7g
└── Parent Dashboard (protected routes) <-- page.tsx:8
    └── <RouteGuard required="parent"> <-- page.tsx:12
        └── allowed = hasGuardianToken() <-- RouteGuard.tsx:22
            └── if (!allowed) <-- RouteGuard.tsx:25
                └── router.push("/login") <-- RouteGuard.tsx:26
```

**Location ID: 7a**
- **Title:** Mount Context Provider
- **Description:** Wrap entire app in LearnerProvider for global state management
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/layout.tsx:62

**Location ID: 7b**
- **Title:** Read Persisted Learner
- **Description:** Attempt to restore learner session from localStorage on mount
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:31

**Location ID: 7c**
- **Title:** Hydrate Learner State
- **Description:** Deserialize and set learner object in React context
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:34

**Location ID: 7d**
- **Title:** Fetch Fresh State
- **Description:** Load latest mastery and gamification data from backend
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/context/LearnerContext.tsx:68

**Location ID: 7e**
- **Title:** Check Learner Session
- **Description:** Verify learner exists in context before rendering learner routes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/layout.tsx:16

**Location ID: 7f**
- **Title:** Evaluate Route Permission
- **Description:** Check if user has required authentication for route (learner vs guardian)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:22

**Location ID: 7g**
- **Title:** Redirect Unauthorized
- **Description:** Navigate to login or home if authentication check fails
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/components/eduboost/RouteGuard.tsx:26

### AI Guide: App Initialization

**Motivation:**
Application bootstrap with context provider, localStorage hydration, and route guards ensures session persistence and protected routes. This initialization process restores the user's session from previous visits and ensures that protected routes are only accessible to authenticated users.

**Details:**

**Context and Hydration**
The context provider is mounted to wrap the app in provider for global state and context management [7a]. The persisted learner is read from localStorage using getItem() for session restoration and data persistence [7b]. The learner state is hydrated by JSON parsing and calling setLearner() for context update [7c].

**State Refresh**
Fresh state is fetched via refreshState() call with Promise.all() for backend fetch [7d]. This ensures that the frontend has the latest data from the backend while still providing instant session restoration from localStorage.

**Route Guards**
The learner session is checked to verify learner exists for protected routes and authentication check [7e]. Route permission is evaluated by checking required auth with boolean evaluation and permission logic [7f]. Unauthorized users are redirected using router.push() for login redirect and access denied [7g].

## Trace ID: 8
**Title:** Study Plan Generation → Job Polling → Schedule Normalization → Weekly View Render

**Description:** Personalized study plan flow: trigger async plan generation with gap_ratio parameter, poll job status, normalize schedule structure, render weekly calendar with gap-fill and grade-level activities

**Motivation:**
EduBoost Frontend implements personalized study plan generation with async job processing and schedule normalization. The plan page component mount triggers fetchPlan() callback which calls LearnerService.getStudyPlan() to POST /study-plans/generate with gap_ratio=0.4 for knowledge gap prioritization. The backend accepts the async job and waitForJobResult() polls /jobs/{job_id} until the plan is ready. The normalizeStudyPlan() function unifies days/schedule fields to handle backend variations in schedule field naming. The weekly calendar rendering extracts the schedule object, maps over days (Mon-Sun), gets items for each day, and renders study item cards with onClick handler to navigate to lesson with pre-filled subject and topic. The week_focus and grade info are displayed. This personalized approach provides adaptive scheduling, gap prioritization, and seamless lesson navigation.

**Details:**
- **Execution Flow:** Plan page component mount → fetchPlan() callback → LearnerService.getStudyPlan() → POST /study-plans/generate → Backend accepts job (gap_ratio=0.4) → waitForJobResult() polling → Poll /jobs/{job_id} until complete → normalizeStudyPlan() → Unify days/schedule fields → Render weekly calendar → Extract schedule object → Map over days (Mon-Sun) → Get items for each day → Render study item cards → onClick handler → router.push(lessonHref) → Display week_focus & grade info
- **Concurrency Safety:** Job polling is per-request. Normalization is stateless. Rendering is synchronous. No distributed locks needed
- **Covered Objects:** Study plan generation, job polling, schedule normalization, weekly calendar, gap prioritization
- **Timeouts:** Plan generation: ~1-3s. Polling: ~500ms intervals. Normalization: ~1-5ms. Rendering: ~10-50ms. Total: ~1.5-3.5s
- **Migration Path:** From static to personalized plans. Migration requires: 1) Implement job polling, 2) Add normalization, 3. Render calendar, 4) Add navigation
- **Error Handling:** Generation failures logged. Polling timeouts handled. Normalization errors logged. Rendering errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate plan data. Normalize safely. Render securely. Validate navigation. Filter sensitive data. Audit plan generation

**Trace text diagram:**
```
Study Plan Page Load
├── Plan page component mount
│   └── fetchPlan() callback <-- 8a
│       └── LearnerService.getStudyPlan()
│           ├── POST /study-plans/generate <-- 8b
│           │   └── Backend accepts job (gap_ratio=0.4) <-- services.ts:114
│           ├── waitForJobResult() polling <-- 8c
│           │   └── Poll /jobs/{job_id} until complete <-- client.ts:189
│           └── normalizeStudyPlan() <-- 8d
│               └── Unify days/schedule fields <-- services.ts:47
└── Render weekly calendar
    ├── Extract schedule object <-- 8e
    ├── Map over days (Mon-Sun) <-- page.tsx:142
    │   └── Get items for each day <-- 8f
    │       └── Render study item cards <-- page.tsx:165
    │           └── onClick handler <-- 8g
    │               └── router.push(lessonHref)
    └── Display week_focus & grade info <-- page.tsx:114
```

**Location ID: 8a**
- **Title:** Request Study Plan
- **Description:** Trigger study plan generation for learner based on diagnostic results
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/plan/page.tsx:49

**Location ID: 8b**
- **Title:** POST Study Plan Job
- **Description:** Backend accepts async job with gap_ratio=0.4 for knowledge gap prioritization
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:112

**Location ID: 8c**
- **Title:** Poll Until Plan Ready
- **Description:** Wait for backend to compute personalized weekly schedule
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:116

**Location ID: 8d**
- **Title:** Normalize Schedule Format
- **Description:** Handle backend variations in schedule field naming (days vs schedule)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/lib/api/services.ts:45

**Location ID: 8e**
- **Title:** Extract Weekly Schedule
- **Description:** Get day-to-day activity mapping from normalized plan response
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/plan/page.tsx:81

**Location ID: 8f**
- **Title:** Get Day Activities
- **Description:** Retrieve list of study items for each day of the week
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/plan/page.tsx:143

**Location ID: 8g**
- **Title:** Navigate to Lesson
- **Description:** Click study item to start lesson with pre-filled subject and topic
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/frontend/src/app/(learner)/plan/page.tsx:197

### AI Guide: Study Plan Generation

**Motivation:**
Personalized study plan generation with async job processing and schedule normalization provides adaptive scheduling. The study plan is generated based on diagnostic results with gap prioritization, using async job processing to prevent long-running requests from blocking the UI.

**Details:**

**Job Submission and Polling**
The study plan is requested to trigger generation with diagnostic-based gap prioritization [8a]. The backend accepts the job via POST with gap_ratio=0.4 for async processing [8b]. The client polls until the plan is ready by polling job status, waiting for completion, and checking ready status [8c].

**Schedule Normalization**
The schedule format is normalized to unify fields and handle variations between days and schedule formats [8d]. The weekly schedule is extracted to get the schedule object with day mapping and activity data [8e]. Day activities are retrieved to get items, per-day lists, and study items [8f].

**Navigation**
Users navigate to lessons via click handler using router.push() with pre-filled params [8g]. This provides seamless navigation from the study plan calendar to individual lessons.
