# EduBoost V2 Core Infrastructure: Runtime Primitives & Cross-Cutting Concerns

Maps the foundational layer of EduBoost V2, covering application bootstrap, authentication/authorization, LLM orchestration, health monitoring, POPIA consent enforcement, and error handling. Key entry points: app startup [1b], JWT validation [3c], authorization checks [4c], LLM generation [5d], and consent gates [7c].

## Trace ID: 1
**Title:** Application Bootstrap & Initialization

**Description:** Core infrastructure setup when the FastAPI application starts, loading configuration, initializing logging, registering middleware and exception handlers.

**Motivation:**
EduBoost V2 requires a robust application bootstrap process to initialize all cross-cutting concerns before handling requests. The configuration layer uses Pydantic BaseSettings to load environment variables and .env file settings into a singleton settings object, providing type-safe configuration access. Structured logging with structlog is configured early to ensure all subsequent log entries include context (request_id, app_env, app_version) for distributed tracing. The database layer initializes SQLAlchemy async engine with connection pooling for efficient database access. FastAPI application setup registers global exception handlers for consistent error responses across all endpoints. Middleware stack registration adds RequestIDMiddleware for request tracing, TimingMiddleware for performance monitoring, and StructuredLoggingMiddleware for request lifecycle logging. This bootstrap process ensures all infrastructure components are properly initialized before the application accepts requests.

**Details:**
- **Configuration Layer and Settings Singleton:** The bootstrap creates a settings singleton using Pydantic BaseSettings.from_env() to load environment variables and .env file settings [1a]. This provides type-safe configuration access and ensures that all configuration is loaded from environment variables rather than hardcoded values. Settings loading takes ~10-50ms. The settings singleton is read-only after initialization, providing thread-safe configuration access across the application.
- **Logging Infrastructure and Structlog Configuration:** Structured logging is configured early using configure_logging() call and structlog.configure() to ensure all subsequent log entries include context for distributed tracing [1b-1c]. The system uses JSON renderer for production and console renderer for development, with contextvars merge processors to include request_id, app_env, and app_version in all log entries. Logging configuration takes ~10-50ms and is thread-safe.
- **Database Layer and Connection Pooling:** The database layer initializes SQLAlchemy async engine with connection pooling for efficient database access [1f]. Connection pool setup and async session factory creation take ~100-500ms. The database engine manages connection pooling automatically, providing efficient database access without manual connection management. Database connection failures fail startup to ensure the application only starts when database connectivity is available.
- **FastAPI Application Setup and Exception Handling:** FastAPI application setup registers global exception handlers for consistent error responses across all endpoints [1d-1e]. Handlers are set up for specific error types including EduBoostError, HTTPException, ValidationError, and Global Exception. Handler registration takes ~10-50ms and is registered once at startup. This ensures that all errors are caught and converted to standardized API responses, providing consistent error handling across all endpoints.
- **Middleware Stack Registration and Cross-Cutting Concerns:** Middleware stack registration adds RequestIDMiddleware for request tracing, TimingMiddleware for performance monitoring, and StructuredLoggingMiddleware for request lifecycle logging. Middleware registration takes ~10-50ms and is thread-safe. The middleware stack provides cross-cutting concerns like request ID injection, timing, and metrics recording, ensuring that all requests are traced and monitored consistently. Total bootstrap takes ~150-700ms.

**Trace text diagram:**
```
EduBoost V2 Application Bootstrap
├── Configuration Layer
│   └── Settings singleton creation <-- 1a
│       └── Pydantic BaseSettings.from_env() <-- config.py:58
├── Logging Infrastructure
│   ├── configure_logging() call <-- 1b
│   └── structlog.configure() <-- 1c
│       ├── JSON renderer (production) <-- logging.py:22
│       ├── Console renderer (dev) <-- logging.py:24
│       └── Contextvars merge processors <-- logging.py:27
├── Database Layer
│   └── SQLAlchemy engine creation <-- 1f
│       ├── Connection pool setup <-- database.py:35
│       └── Async session factory <-- database.py:41
├── FastAPI Application Setup
│   ├── Exception handler registration <-- 1d
│   │   └── register_exception_handlers() <-- 1e
│   │       ├── EduBoostError handler <-- exceptions.py:153
│   │       ├── HTTPException handler <-- exceptions.py:163
│   │       ├── ValidationError handler <-- exceptions.py:175
│   │       └── Global Exception handler <-- exceptions.py:215
│   └── Middleware stack registration
│       ├── RequestIDMiddleware <-- middleware.py:22
│       ├── TimingMiddleware <-- middleware.py:42
│       └── StructuredLoggingMiddleware <-- middleware.py:62
```

**Location ID: 1a**
- **Title:** Settings Singleton Creation
- **Description:** Pydantic settings loaded from environment variables and .env file
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/config.py:243

**Location ID: 1b**
- **Title:** Structured Logging Initialization
- **Description:** Sets up structlog with JSON output for production, console for dev
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:31

**Location ID: 1c**
- **Title:** Structlog Configuration
- **Description:** Configures processors for contextvars, timestamps, and JSON rendering
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/logging.py:46

**Location ID: 1d**
- **Title:** Exception Handler Registration
- **Description:** Registers global exception handlers for consistent error responses
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:17

**Location ID: 1e**
- **Title:** Exception Handler Setup
- **Description:** Attaches handlers for EduBoostError, HTTPException, ValidationError, etc.
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:150

**Location ID: 1f**
- **Title:** Database Engine Creation
- **Description:** Creates SQLAlchemy async engine with connection pooling
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:39

### AI Guide: Application Bootstrap & Initialization

**Motivation:**
The application bootstrap process initializes all cross-cutting concerns before handling requests. This ensures that configuration, logging, database connections, exception handling, and middleware are all properly set up before the application begins serving traffic. The bootstrap process must complete before routes are registered to ensure all dependencies are available, providing a robust foundation for the application.

**Details:**

**Configuration and Logging**
The bootstrap creates a settings singleton using Pydantic settings from environment variables, providing type-safe configuration [1a]. This ensures that configuration is loaded from environment variables rather than hardcoded values, improving security and flexibility. Structured logging is configured early using structlog, with JSON output for production and console output for development [1b]. The structlog configuration adds processors for context, timestamps, and JSON formatting to support distributed tracing [1c], ensuring that all log entries include necessary context for debugging and monitoring.

**Exception Handling and Consistent Error Responses**
Global exception handlers are registered once to provide consistent error responses across all endpoints [1d]. Handlers are set up for specific error types including EduBoostError, HTTPException, and ValidationError [1e]. This ensures that all errors are caught and converted to standardized API responses, providing consistent error handling across all endpoints and improving the developer experience and debugging capabilities.

**Database and Middleware for Cross-Cutting Concerns**
The database engine is created with SQLAlchemy async engine, connection pooling, and session factory [1f]. This provides efficient database access with automatic connection pooling. Middleware is added for cross-cutting concerns like request ID injection, timing, and metrics recording. The middleware stack provides request tracing, performance monitoring, and request lifecycle logging, ensuring that all requests are traced and monitored consistently for operational visibility and debugging.

## Trace ID: 2
**Title:** JWT Token Creation & Storage (Login Flow)

**Description:** Authentication flow from login request through password verification to JWT token generation and secure storage in Redis.

**Motivation:**
EduBoost V2 implements JWT-based authentication with secure token storage in Redis for session management. The login flow begins with password verification using bcrypt.checkpw() for constant-time comparison, preventing timing attacks. Access tokens are JWT-encoded with claims (sub, role, jti, exp) and signed using the current JWT signing key from the keyring, enabling key rotation without invalidating all tokens. Refresh tokens are JWT-encoded with a 7-day expiration and family_id for token rotation detection, allowing secure token refresh while preventing replay attacks. Tokens are stored in Redis as SHA-256 hashes to prevent token leakage if Redis is compromised. The refresh token is stored with a TTL matching its expiration, and user session tracking maps users to their refresh token families. This system provides secure, scalable authentication with token revocation support and key rotation capabilities.

**Details:**
- **Password Verification and Constant-Time Comparison:** The login flow begins with password verification using bcrypt.checkpw() for constant-time comparison, preventing timing attacks [2a]. Password verification takes ~100-300ms. This constant-time comparison ensures that password verification cannot be used to extract password information through timing analysis, providing security against timing-based attacks.
- **Access Token Generation and Keyring Signing:** Access tokens are JWT-encoded with claims (sub, role, jti, exp) and signed using the current JWT signing key from the keyring [2b]. JWT encoding takes ~10-50ms. The keyring enables key rotation without invalidating all tokens, providing flexibility for key management while maintaining security.
- **Refresh Token Generation and Family ID:** Refresh tokens are JWT-encoded with a 7-day expiration and family_id for token rotation detection [2c]. JWT encoding for refresh takes ~10-50ms. The family_id allows the system to detect token reuse and prevent replay attacks, providing secure token refresh capabilities.
- **Token Persistence in Redis and SHA-256 Hashing:** Tokens are stored in Redis as SHA-256 hashes to prevent token leakage if Redis is compromised [2d]. Redis storage takes ~10-50ms. The refresh token is stored with a TTL matching its expiration, ensuring automatic cleanup and preventing unbounded growth of the token store.
- **User Session Tracking and Family Mapping:** User session tracking maps users to their refresh token families for session management and rotation detection [2e]. This mapping enables the system to track all active sessions for a user and implement family-based token revocation. Total login takes ~120-400ms.

**Trace text diagram:**
```
Login/Authentication Flow
├── User Login Request
│   └── Password Verification
│       └── bcrypt.checkpw() <-- 2a
│           └── constant-time comparison
├── Access Token Generation
│   └── JWT encoding with claims
│       ├── build payload (sub, role, jti, exp) <-- security.py:52
│       └── jwt.encode() with keyring <-- 2b
│           └── signs with current_jwt_signing_key()
├── Refresh Token Generation
│   └── JWT encoding for refresh
│       ├── build payload (family_id, 7-day exp) <-- security.py:66
│       └── jwt.encode() with keyring <-- 2c
│           └── signs with current_jwt_signing_key()
└── Token Persistence in Redis
    ├── Hash refresh token (SHA-256) <-- refresh_tokens.py:25
    ├── Store hashed token <-- 2d
    │   └── cache_set(_refresh_key(jti), hashed)
    └── Track user session <-- 2e
        └── cache_set(_user_session_key(), family_id)
```

**Location ID: 2a**
- **Title:** Password Verification
- **Description:** Constant-time bcrypt comparison of plaintext against stored hash
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:37

**Location ID: 2b**
- **Title:** Access Token Creation
- **Description:** Encodes JWT with user_id, role, jti, expiration using keyring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:61

**Location ID: 2c**
- **Title:** Refresh Token Creation
- **Description:** Creates refresh token with 7-day expiration and family_id for rotation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:75

**Location ID: 2d**
- **Title:** Refresh Token Storage
- **Description:** Stores hashed refresh token in Redis with TTL for rotation tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:68

**Location ID: 2e**
- **Title:** User Session Tracking
- **Description:** Maps user to refresh token family for session management
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:70

### AI Guide: JWT Token Creation & Storage (Login Flow)

**Motivation:**
The login flow creates JWT tokens with secure storage in Redis for session management. Using bcrypt for password verification prevents timing attacks, while JWT tokens signed with a keyring enable key rotation without invalidating all tokens. This system provides secure, scalable authentication with token revocation support and key rotation capabilities.

**Details:**

**Password Verification and Timing Attack Prevention**
Password verification uses bcrypt.checkpw() for constant-time comparison, preventing timing attacks [2a]. This ensures that password verification cannot be used to extract password information through timing analysis, providing security against timing-based attacks. The constant-time comparison is critical for preventing attackers from gaining information about password hashes through response time analysis.

**Token Generation and Keyring-Based Signing**
Access tokens are JWT-encoded with claims (sub, role, jti, exp) and signed using the current JWT signing key from the keyring [2b]. Refresh tokens are JWT-encoded with a 7-day expiration and family_id for token rotation detection [2c]. The keyring enables key rotation without invalidating all tokens, providing flexibility for key management while maintaining security. The family_id allows the system to detect token reuse and prevent replay attacks, providing secure token refresh capabilities.

**Secure Storage and Hash-Based Protection**
Tokens are stored in Redis as SHA-256 hashes to prevent token leakage if Redis is compromised [2d]. The refresh token is stored with a TTL matching its expiration, ensuring automatic cleanup and preventing unbounded growth of the token store. User session tracking maps users to their refresh token families for session management and rotation detection [2e]. This hash-based storage ensures that even if Redis is compromised, the actual token values are not exposed, providing defense-in-depth for token security.

## Trace ID: 3
**Title:** JWT Validation & Revocation Check (Protected Route)

**Description:** Request authentication flow: token extraction, JWT decoding with keyring, revocation check in Redis, and user payload resolution.

**Motivation:**
EduBoost V2 implements comprehensive JWT validation with revocation checks for secure authentication. The FastAPI dependency get_current_user() extracts the Bearer token from the Authorization header and decodes it using decode_jwt_with_keyring(), which delegates to the JWT keyring service for multi-key validation. The keyring service verifies the signature using the current or previous signing key, enabling key rotation without invalidating valid tokens. Revocation checks include is_token_revoked(jti) to check if the specific token has been revoked (stored in Redis under revoked_jti:{jti}) and is_user_revoked(user_id) to check if all tokens for a user have been globally revoked (stored in Redis under revoked_user:{user_id}). On successful validation, the JWT payload with user_id, role, and custom claims is returned. On failure, an HTTPException 401 is raised. This system provides secure authentication with token revocation support and key rotation capabilities.

**Details:**
- **Token Extraction and FastAPI Dependency:** The FastAPI dependency get_current_user() extracts the Bearer token from the Authorization header for authentication [3a]. Token extraction takes ~1-5ms. This dependency is used on protected routes to ensure that only authenticated requests can access sensitive endpoints.
- **JWT Decoding and Keyring Validation:** The token is decoded using decode_jwt_with_keyring(), which delegates to the JWT keyring service for multi-key validation [3b]. JWT decoding takes ~10-50ms. The keyring service verifies the signature using the current or previous signing key, enabling key rotation without invalidating valid tokens. This multi-key validation ensures that tokens signed with previous keys remain valid during key rotation transitions.
- **Revocation Checks and Redis Lookups:** Revocation checks include is_token_revoked(jti) to check if the specific token has been revoked (stored in Redis under revoked_jti:{jti}) and is_user_revoked(user_id) to check if all tokens for a user have been globally revoked (stored in Redis under revoked_user:{user_id}) [3c-3d]. Redis checks take ~10-50ms. These checks ensure that revoked tokens cannot be used to access protected resources, providing comprehensive token revocation support.
- **Payload Resolution and Error Handling:** On successful validation, the JWT payload with user_id, role, and custom claims is returned [3e]. On failure, an HTTPException 401 is raised. Total validation takes ~20-105ms. This error handling ensures that authentication failures return consistent error responses, improving the developer experience and debugging capabilities.

**Trace text diagram:**
```
JWT Validation & Revocation Check Flow
│
├── FastAPI Request Handler
│   └── get_current_user() dependency <-- 3a
│       ├── Extract Bearer token from header <-- security.py:94
│       └── decode_token(credentials) <-- 3a
│           │
│           ├── decode_jwt_with_keyring() <-- 3b
│           │   ├── JWT keyring service
│           │   └── Verify signature with current/prev key <-- security.py:80
│           │
│           └── Revocation checks
│               ├── is_token_revoked(jti) <-- 3c
│               │   └── Redis GET revoked_jti:{jti} <-- 3d
│               │
│               ├── is_user_revoked(user_id) <-- 3e
│               │   └── Redis GET revoked_user:{user_id} <-- token_revocation.py:107
│               │
│               └── return validated payload <-- 3f
│                   └── {sub, role, jti, exp, ...}
│
└── On failure: HTTPException 401 <-- security.py:82
```

**Location ID: 3a**
- **Title:** Token Decoding Entry Point
- **Description:** FastAPI dependency extracts and decodes Bearer token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:100

**Location ID: 3b**
- **Title:** Keyring-Based JWT Decode
- **Description:** Delegates to JWT keyring service for multi-key validation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:80

**Location ID: 3c**
- **Title:** JTI Revocation Check
- **Description:** Queries Redis blacklist to check if token has been revoked
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:108

**Location ID: 3d**
- **Title:** Redis Revocation Lookup
- **Description:** Checks if JTI exists in revoked_jti: prefix keys
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:75

**Location ID: 3e**
- **Title:** User-Level Revocation Check
- **Description:** Checks if all tokens for user have been globally revoked
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:117

**Location ID: 3f**
- **Title:** Return Validated Claims
- **Description:** Returns JWT payload with user_id, role, and custom claims
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:124

### AI Guide: JWT Validation & Revocation Check (Protected Route)

**Motivation:**
JWT validation with revocation checks ensures secure authentication by verifying token signatures and checking for token revocation on every request. This provides both per-token and user-level revocation capabilities. The FastAPI dependency get_current_user() extracts the Bearer token from the Authorization header and decodes it using decode_jwt_with_keyring(), which delegates to the JWT keyring service for multi-key validation. The keyring service verifies the signature using the current or previous signing key, enabling key rotation without invalidating valid tokens. Revocation checks include is_token_revoked(jti) to check if the specific token has been revoked (stored in Redis under revoked_jti:{jti}) and is_user_revoked(user_id) to check if all tokens for a user have been globally revoked (stored in Redis under revoked_user:{user_id}). On successful validation, the JWT payload with user_id, role, and custom claims is returned. On failure, an HTTPException 401 is raised. This system provides secure authentication with token revocation support and key rotation capabilities.

**Details:**

**Token Extraction and FastAPI Dependency**
The FastAPI dependency extracts the Bearer token as the entry point for validation [3a]. The decode operation delegates to the keyring service for multi-key validation, enabling key rotation [3b]. This ensures that tokens signed with old keys can still be validated during the rotation period. The dependency pattern provides a clean, declarative way to enforce authentication across multiple routes without duplicating authentication logic.

**Revocation Checks and Redis-Based Token Blacklisting**
The JTI revocation check uses a Redis lookup to verify per-token revocation [3c]. The Redis check uses the revoked_jti prefix for atomic operation [3d]. User-level revocation checks enable global token invalidation for mass revocation scenarios [3e]. These checks ensure that revoked tokens cannot be used to access protected resources. The Redis-based storage provides fast lookups for revocation status, ensuring that revocation checks do not significantly impact request performance.

**Claims Return and Consistent Error Handling**
After successful validation, the dependency returns the validated user payload containing role and claims for use by routes [3f]. This provides the route handler with authenticated user information without exposing the raw token. On failure, an HTTPException 401 is raised. This error handling ensures that authentication failures return consistent error responses, improving the developer experience and debugging capabilities. The structured error responses provide clear feedback about why authentication failed, aiding in troubleshooting and security monitoring.

## Trace ID: 4
**Title:** Authorization Policy Enforcement (RBAC)

**Description:** Object-level authorization check flow: current user resolution, policy evaluation, and audit logging for privileged access.

**Motivation:**
EduBoost V2 implements role-based access control (RBAC) with object-level authorization checks and audit logging for POPIA compliance. The authorization assertion dependency helper enforces learner access policy before route execution, ensuring only authorized users can access learner data. The policy evaluation entry point determines whether the actor role (ADMIN, GUARDIAN, LEARNER) permits access to the learner resource based on ownership relationships. Privileged access audit logging emits structured log entries with event, actor_id, role, resource_id, and jti for compliance requirements. The structured audit event includes all relevant context for security auditing. When policy checks fail, an HTTP 403 is raised. This system provides fine-grained access control with comprehensive audit trails for regulatory compliance.

**Details:**
- **Authorization Assertion and Pre-Execution Check:** The authorization assertion dependency helper enforces learner access policy before route execution as a pre-execution check [4a]. Policy evaluation takes ~10-50ms. This ensures that authorization decisions are made before any business logic executes, providing a security guarantee that unauthorized requests are rejected early in the request lifecycle.
- **Policy Evaluation and Role-Based Access Control:** The policy evaluation entry evaluates whether the actor role (ADMIN, GUARDIAN, LEARNER) permits access to the learner resource based on ownership relationships [4b]. The policy evaluation checks role permissions, performs object-level checks, and verifies ownership. This provides fine-grained access control that considers both the user's role and their specific relationship to the resource.
- **Privileged Access Audit and POPIA Compliance:** Privileged access audit logging emits structured log entries with event, actor_id, role, resource_id, and jti for POPIA compliance [4c-4d]. Audit logging takes ~1-5ms. The structured audit event includes all relevant context for security auditing, providing a complete record of who accessed what and when for regulatory compliance.
- **Authorization Failure and Secure Denial:** When policy checks fail, an HTTP 403 is raised [4e]. This fails securely by denying access by default and providing clear feedback to the client about why access was denied. Total check takes ~20-105ms. This error handling ensures that authorization failures return consistent error responses, improving the developer experience and debugging capabilities.

**Location ID: 4a**
- **Title:** Authorization Assertion
- **Description:** Dependency helper enforces learner access policy before route executes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:105

**Location ID: 4b**
- **Title:** Policy Evaluation Entry
- **Description:** Evaluates whether actor role permits access to learner resource
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:294

**Location ID: 4c**
- **Title:** Privileged Access Audit
- **Description:** Logs admin access to learner data for POPIA compliance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:75

**Location ID: 4d**
- **Title:** Structured Audit Event
- **Description:** Emits structured log with event, actor_id, role, resource_id, jti
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:55

**Location ID: 4e**
- **Title:** Authorization Failure
- **Description:** Raises HTTP 403 when policy check fails
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:268

### AI Guide: Authorization Policy Enforcement (RBAC)

**Motivation:**
RBAC with object-level authorization ensures users can only access resources they're authorized for. The policy evaluation checks role permissions, object ownership, and logs all authorization decisions for security auditing and POPIA compliance. The authorization assertion dependency helper enforces learner access policy before route execution, ensuring only authorized users can access learner data. The policy evaluation entry point determines whether the actor role (ADMIN, GUARDIAN, LEARNER) permits access to the learner resource based on ownership relationships. Privileged access audit logging emits structured log entries with event, actor_id, role, resource_id, and jti for compliance requirements. When policy checks fail, an HTTP 403 is raised. This system provides fine-grained access control with comprehensive audit trails for regulatory compliance.

**Details:**

**Policy Enforcement and Pre-Execution Authorization**
The authorization assertion dependency helper enforces policy before route execution as a pre-execution check [4a]. The policy evaluation entry evaluates role permissions, performs object-level checks, and verifies ownership [4b]. This ensures that authorization decisions are made before any business logic executes, providing a security guarantee that unauthorized requests are rejected early in the request lifecycle. The pre-execution check pattern ensures that authorization is enforced consistently across all protected routes without requiring manual authorization checks in each route handler.

**Audit Logging and POPIA Compliance**
Privileged access is logged for admin access to maintain POPIA compliance and a security audit trail [4c]. The structured audit event includes event context with actor and resource details [4d]. This provides a complete record of who accessed what and when, which is essential for regulatory compliance and security monitoring. The structured logging format ensures that audit logs are machine-readable and can be easily analyzed for compliance reporting and security investigations.

**Failure Handling and Secure Denial**
Authorization failure raises HTTP 403 with a clear error message [4e]. This fails securely by denying access by default and providing clear feedback to the client about why access was denied. The secure-by-default approach ensures that if authorization cannot be determined, access is denied, preventing unauthorized access due to misconfiguration or errors. The clear error messages improve the developer experience and debugging capabilities while maintaining security.

## Trace ID: 5
**Title:** LLM Lesson Generation Pipeline

**Description:** AI content generation flow: quota enforcement, semantic cache lookup, LLM provider call, judiciary validation, and cache storage.

**Motivation:**
EduBoost V2 implements an AI lesson generation pipeline with quota enforcement, semantic caching, and content validation. The pipeline begins with cache key generation using SHA-256 hash of lesson parameters for semantic caching, enabling reuse of previously generated lessons. A semantic cache lookup checks Redis for cached lessons with the same parameters, reducing API costs and improving response time. AI quota enforcement atomically increments daily request counters and checks against limits (20 for free tier), preventing abuse. The LLM provider call uses Google/Groq/Anthropic with automatic fallback and retry for reliability. Judiciary validation validates LLM output against Pydantic schema and content policy, scanning for blocked patterns (violence, explicit content, etc.). Validated lessons are cached in Redis with 7-day TTL. This system provides cost-effective, reliable AI content generation with safety controls.

**Details:**
- **Cache Key Generation and Semantic Caching:** The pipeline begins with cache key generation using SHA-256 hash of lesson parameters for semantic caching [5a]. Cache key generation is deterministic. This enables reuse of previously generated lessons, reducing API costs and improving response time for identical requests.
- **Semantic Cache Lookup and Cost Optimization:** A semantic cache lookup checks Redis for cached lessons with the same parameters [5b]. Cache lookup takes ~10-50ms. This reduces API costs and improves response time by returning cached results when available, providing cost optimization for AI content generation.
- **AI Quota Enforcement and Abuse Prevention:** AI quota enforcement atomically increments daily request counters and checks against limits (20 for free tier) [5c]. Quota check takes ~10-50ms. This prevents abuse and ensures fair usage of AI resources, protecting against excessive API costs.
- **LLM Provider Call and Fallback Mechanism:** The LLM provider call uses Google/Groq/Anthropic with automatic fallback and retry for reliability [5d]. LLM call takes ~1-5s. The fallback mechanism ensures reliability by automatically switching to alternative providers if the primary provider fails, providing resilience against provider outages.
- **Judiciary Validation and Content Policy:** Judiciary validation validates LLM output against Pydantic schema and content policy, scanning for blocked patterns (violence, explicit content, etc.) [5e-5f]. Validation takes ~10-50ms. This ensures that all generated content meets safety standards and complies with content policies, preventing harmful content from being served to users.
- **Cache Validated Lesson and TTL Management:** Validated lessons are cached in Redis with 7-day TTL [5g]. Cache storage takes ~10-50ms. This enables reuse of validated lessons while ensuring that cached content is refreshed periodically. Total pipeline takes ~1-5.5s.

**Location ID: 5a**
- **Title:** Cache Key Generation
- **Description:** Creates SHA-256 hash of lesson parameters for semantic caching
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:214

**Location ID: 5b**
- **Title:** Semantic Cache Lookup
- **Description:** Checks Redis for previously generated lesson with same parameters
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:215

**Location ID: 5c**
- **Title:** AI Quota Enforcement
- **Description:** Atomically increments daily request counter and checks limit
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:221

**Location ID: 5d**
- **Title:** LLM Provider Call
- **Description:** Calls Google/Groq/Anthropic with automatic fallback and retry
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:252

**Location ID: 5e**
- **Title:** Judiciary Validation
- **Description:** Validates LLM output against Pydantic schema and content policy
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:268

**Location ID: 5f**
- **Title:** Content Policy Check
- **Description:** Scans for blocked patterns (violence, explicit content, etc.)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/judiciary.py:45

**Location ID: 5g**
- **Title:** Cache Validated Lesson
- **Description:** Stores validated lesson in Redis with 7-day TTL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:295

### AI Guide: LLM Lesson Generation Pipeline

**Motivation:**
The AI lesson generation pipeline provides cost-effective, reliable content generation with safety controls. Semantic caching reduces API costs and improves response time, while quota enforcement prevents abuse and validation ensures content safety. This system provides cost-effective, reliable AI content generation with safety controls, balancing performance, cost, and safety.

**Details:**

**Semantic Caching and Cost Optimization**
Cache key generation uses SHA-256 hash of parameters for semantic caching with deterministic keys [5a]. The semantic cache lookup checks Redis to reduce API costs and improve response time [5b]. This ensures that identical generation requests return cached results instead of calling the LLM provider, providing significant cost savings for AI content generation. The deterministic cache key generation ensures that identical requests always map to the same cache key, enabling efficient cache hit detection.

**Quota Enforcement and Abuse Prevention**
AI quota enforcement uses atomic counter increment with a daily limit check to prevent abuse [5c]. The Redis pipeline creation enables atomic INCR + EXPIRE operations to prevent race conditions. This ensures that quota limits are enforced accurately even under concurrent load, preventing quota circumvention through race conditions. The atomic counter ensures thread-safe quota checks under concurrent load.

**Generation and Validation with Safety Controls**
The LLM provider call uses provider abstraction with fallback and retry for reliability [5d]. Judiciary validation uses Pydantic schema validation and content policy checks for safety [5e]. The content policy check scans for blocked patterns to detect harmful content [5f]. Validated lessons are cached in Redis with a 7-day TTL for reuse [5g]. This multi-layered validation ensures that all generated content meets safety standards and complies with content policies, preventing harmful content from being served to users. The provider abstraction enables easy addition of new providers and load balancing across multiple providers for improved performance and reliability.

## Trace ID: 6
**Title:** Deep Health Check Execution

**Description:** Readiness probe flow: checks critical dependencies (Postgres, Redis, migrations, audit) and optional components (LLM, judiciary) with metrics recording.

**Motivation:**
EduBoost V2 implements a comprehensive deep health check system for readiness probes and monitoring. The /ready endpoint handler coordinates gather_deep_health() to check all system components. Critical checks include check_postgres() which executes a simple SELECT 1 query to verify database connection and updates pool metrics, check_redis() which sends a PING command to verify Redis availability, check_migrations() which queries the alembic_version table to verify migrations are applied, and check_audit_repository() which verifies the audit_events table is accessible for POPIA compliance. Optional checks include check_llm_provider() and check_judiciary() for non-critical components. The overall status is determined as "ok", "degraded", or "error" based on critical check results. Prometheus metrics are recorded via _record_readiness_metrics() which updates readiness_component_status gauges for monitoring. This system provides comprehensive health monitoring for deployment orchestration and alerting.

**Details:**
- **Critical Checks and Database Connectivity:** The /ready endpoint handler coordinates gather_deep_health() to check all system components [6a]. Critical checks include check_postgres() which executes a simple SELECT 1 query to verify database connection and updates pool metrics [6b]. Postgres check takes ~10-50ms. This ensures that the application can connect to the database and that the connection pool is healthy, providing early detection of database connectivity issues.
- **Redis Connectivity and Migration Status:** check_redis() sends a PING command to verify Redis availability [6c]. Redis check takes ~10-50ms. check_migrations() queries the alembic_version table to verify migrations are applied [6d]. Migration check takes ~10-50ms. These checks ensure that critical infrastructure components are accessible and that the database schema is up to date, preventing deployment of code that requires unapplied migrations.
- **Audit Repository and POPIA Compliance:** check_audit_repository() verifies the audit_events table is accessible for POPIA compliance [6e]. Audit check takes ~10-50ms. This ensures that the audit logging infrastructure is functional, which is critical for regulatory compliance and security auditing.
- **Optional Checks and Non-Critical Components:** Optional checks include check_llm_provider() and check_judiciary() for non-critical components [6f-6g]. Optional checks take ~50-200ms. These checks verify that non-critical components are available without failing the overall health check if they are unavailable, allowing the application to remain operational even if optional components are degraded.
- **Status Determination and Metrics Recording:** The overall status is determined as "ok", "degraded", or "error" based on critical check results. Prometheus metrics are recorded via _record_readiness_metrics() which updates readiness_component_status gauges for monitoring. Total health check takes ~50-400ms. This status determination enables deployment orchestration systems to make informed decisions about traffic routing and pod restarts based on application health.

**Trace text diagram:**
```
Deep Health Check System
├── /ready endpoint handler
│   └── gather_deep_health() <-- 6a
│       ├── Critical Checks
│       │   ├── check_postgres() <-- health.py:18
│       │   │   ├── AsyncSessionLocal() session <-- health.py:20
│       │   │   ├── SELECT 1 query <-- 6b
│       │   │   └── update pool metrics <-- health.py:25
│       │   ├── check_redis() <-- health.py:36
│       │   │   └── redis.ping() <-- 6c
│       │   ├── check_migrations() <-- health.py:114
│       │   │   └── SELECT from alembic_version <-- 6d
│       │   └── check_audit_repository() <-- health.py:147
│       │       └── SELECT 1 FROM audit_events <-- 6e
│       ├── Optional Checks
│       │   ├── check_llm_provider() <-- health.py:52
│       │   └── check_judiciary() <-- health.py:161
│       ├── Determine overall status <-- health.py:206
│       │   └── "ok" | "degraded" | "error" <-- health.py:209
│       └── _record_readiness_metrics() <-- 6f
│           └── readiness_component_status.set() <-- health.py:181
└── Prometheus /metrics scrape
    └── exposes readiness gauges
```

**Location ID: 6a**
- **Title:** Health Check Orchestration
- **Description:** Coordinates all health checks and determines overall system status
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:190

**Location ID: 6b**
- **Title:** Postgres Connectivity Check
- **Description:** Executes simple query to verify database connection
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:21

**Location ID: 6c**
- **Title:** Redis Connectivity Check
- **Description:** Sends PING command to verify Redis availability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:39

**Location ID: 6d**
- **Title:** Migration Status Check
- **Description:** Queries alembic_version table to verify migrations applied
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:127

**Location ID: 6e**
- **Title:** Audit Repository Check
- **Description:** Verifies audit_events table is accessible for POPIA compliance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:155

**Location ID: 6f**
- **Title:** Prometheus Metrics Recording
- **Description:** Updates readiness_component_status gauge for monitoring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:218

### AI Guide: Deep Health Check Execution

**Motivation:**
Deep health checks provide comprehensive system monitoring for readiness probes. They check critical dependencies like PostgreSQL and Redis, verify migration status, and record metrics for monitoring integration. The /ready endpoint handler coordinates gather_deep_health() to check all system components. Critical checks include check_postgres() which executes a simple SELECT 1 query to verify database connection and updates pool metrics, check_redis() which sends a PING command to verify Redis availability, check_migrations() which queries the alembic_version table to verify migrations are applied, and check_audit_repository() which verifies the audit_events table is accessible for POPIA compliance. Optional checks include check_llm_provider() and check_judiciary() for non-critical components. The overall status is determined as "ok", "degraded", or "error" based on critical check results. Prometheus metrics are recorded via _record_readiness_metrics() which updates readiness_component_status gauges for monitoring. This system provides comprehensive health monitoring for deployment orchestration and alerting.

**Details:**

**Orchestration and Status Determination**
The health check orchestration coordinates all checks and determines the overall status [6a]. This ensures that the application reports a single health status that reflects the state of all critical dependencies. The orchestration logic distinguishes between critical and optional checks, allowing the application to remain operational even if optional components are degraded, while ensuring that critical component failures prevent the application from being marked as ready.

**Dependency Checks and Infrastructure Health**
The PostgreSQL connectivity check uses a SELECT 1 query to verify connection and updates pool metrics [6b]. The Redis connectivity check uses a PING command to verify availability and updates metrics [6c]. These checks ensure that the application can communicate with its critical dependencies. The inclusion of pool metrics in the PostgreSQL check provides early detection of connection pool exhaustion before it becomes a problem, enabling proactive intervention.

**Compliance Checks and Schema Verification**
The migration status check queries alembic_version to verify migrations and ensure compliance [6d]. The audit repository check queries audit_events for POPIA compliance and accessibility verification [6e]. These checks ensure that the database schema is up to date and audit trails are accessible, preventing deployment of code that requires unapplied migrations and ensuring that regulatory compliance infrastructure is functional.

**Metrics Recording and Monitoring Integration**
Prometheus metrics recording updates gauges for monitoring integration and status tracking [6f]. This enables the monitoring system to track health check results over time and alert on failures. The metrics-based approach provides visibility into component-level health, enabling targeted troubleshooting and alerting. The readiness gauges can be used by deployment orchestration systems to make informed decisions about traffic routing and pod restarts based on application health.

## Trace ID: 7
**Title:** POPIA Consent Gate Enforcement

**Description:** Consent enforcement flow: learner_id extraction, consent record lookup, policy evaluation, and access blocking for expired/missing consent.

**Motivation:**
EduBoost V2 implements POPIA (Protection of Personal Information Act) consent enforcement to ensure parental consent is obtained before accessing learner data. The consent gate invocation is a FastAPI dependency that enforces consent before learner data access, ensuring consistent enforcement across all routes. The consent record lookup queries the database for an active parental consent record. The consent policy evaluation determines the consent state (granted, expired, withdrawn, renewal_required) based on the record and current time. The expiration check compares the consent expiration timestamp against the current time. Metrics recording increments a Prometheus counter for consent gate blocks to monitor enforcement. Access denial raises an HTTP 403 when active consent is missing. This system ensures compliance with POPIA requirements for processing personal information of minors.

**Details:**
- **Consent Gate Invocation and FastAPI Dependency:** The consent gate invocation is a FastAPI dependency that enforces consent before learner data access [7a]. This ensures consistent enforcement across all protected endpoints, preventing unauthorized access to learner data without parental consent. The dependency pattern provides a clean, declarative way to enforce consent across multiple routes without duplicating consent logic.
- **Consent Record Lookup and Database Query:** The consent record lookup queries the database for an active parental consent record [7b]. Consent lookup takes ~10-50ms. This retrieves the consent record for the specific learner, enabling the system to determine whether consent has been granted, expired, or withdrawn. The database query ensures that the consent status is based on the current state of the consent record.
- **Consent Policy Evaluation and State Determination:** The consent policy evaluation determines the consent state (granted, expired, withdrawn, renewal_required) based on the record and current time [7c]. Policy evaluation takes ~1-5ms. This state machine logic ensures that consent is only considered valid if it meets all criteria, including being active and not expired. The policy evaluation provides a clear, deterministic consent state that can be used for access control decisions.
- **Expiration Check and Time-Based Validation:** The expiration check compares the consent expiration timestamp against the current time [7d]. Expiration check takes ~1-5ms. This ensures that consent is only considered valid if it has not expired, preventing access based on outdated consent records. The time-based validation ensures that consent records are automatically invalidated when they reach their expiration date.
- **Metrics Recording and Monitoring:** Metrics recording increments a Prometheus counter for consent gate blocks to monitor enforcement [7e]. Metrics recording takes ~1-5ms. This enables monitoring of consent enforcement patterns, providing visibility into how often consent is denied and enabling proactive management of consent-related issues.
- **Access Denial and Secure Blocking:** Access denial raises an HTTP 403 when active consent is missing [7f]. This fails securely by denying access by default when consent is not valid, ensuring POPIA compliance. Total consent check takes ~13-65ms. The clear error response provides feedback to the client about why access was denied while maintaining regulatory compliance.

**Location ID: 7a**
- **Title:** Consent Gate Invocation
- **Description:** FastAPI dependency enforces consent before learner data access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:106

**Location ID: 7b**
- **Title:** Consent Record Lookup
- **Description:** Queries database for active parental consent record
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:80

**Location ID: 7c**
- **Title:** Consent Policy Evaluation
- **Description:** Determines consent state (granted/expired/withdrawn/renewal_required)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/consent_policy.py:58

**Location ID: 7d**
- **Title:** Expiration Check
- **Description:** Compares consent expiration timestamp against current time
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/consent_policy.py:104

**Location ID: 7e**
- **Title:** Metrics Recording
- **Description:** Increments Prometheus counter for consent gate blocks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:83

**Location ID: 7f**
- **Title:** Access Denial
- **Description:** Raises HTTP 403 when active consent is missing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:84

### AI Guide: POPIA Consent Gate Enforcement

**Motivation:**
POPIA consent enforcement ensures parental consent before accessing learner data. The consent gate checks for active consent records, evaluates consent policy including expiration, and blocks access when consent is not valid. The consent gate invocation is a FastAPI dependency that enforces consent before learner data access, ensuring consistent enforcement across all routes. The consent record lookup queries the database for an active parental consent record. The consent policy evaluation determines the consent state (granted, expired, withdrawn, renewal_required) based on the record and current time. The expiration check compares the consent expiration timestamp against the current time. Metrics recording increments a Prometheus counter for consent gate blocks to monitor enforcement. Access denial raises an HTTP 403 when active consent is missing. This system ensures compliance with POPIA requirements for processing personal information of minors.

**Details:**

**Consent Gate and Consistent Enforcement**
The consent gate invocation is a FastAPI dependency that enforces consent before access consistently across all protected endpoints [7a]. The consent record lookup performs a database query for the learner-specific active consent record [7b]. This ensures that consent is enforced consistently across all routes that access learner data, preventing unauthorized access due to inconsistent enforcement. The dependency pattern provides a clean, declarative way to enforce consent without duplicating consent logic in each route handler.

**Policy Evaluation and State Machine**
The consent policy evaluation determines the consent state using policy logic and a state machine [7c]. The expiration check uses timestamp comparison with the current time to detect expired consent [7d]. This ensures that consent is only considered valid if it is both active and not expired. The state machine approach provides a clear, deterministic consent state that can be used for access control decisions, ensuring that all consent-related logic is centralized and consistent.

**Metrics Recording and Monitoring**
Metrics recording uses a Prometheus counter to track consent blocks for monitoring [7e]. This enables monitoring of consent enforcement patterns, providing visibility into how often consent is denied and enabling proactive management of consent-related issues. The metrics can be used to identify trends in consent denials, detect potential issues with consent collection processes, and ensure that POPIA compliance is being maintained effectively.

**Access Denial and Secure Blocking**
Access denial returns an HTTP 403 response with a clear error message when consent is not valid [7f]. This provides clear feedback to the client while maintaining POPIA compliance. The secure-by-default approach ensures that if consent cannot be verified, access is denied, preventing unauthorized access due to consent verification failures. The clear error messages improve the developer experience and debugging capabilities while maintaining regulatory compliance.

## Trace ID: 8
**Title:** Exception to Standardized API Response

**Description:** Error handling flow: exception raised in route, caught by global handler, wrapped in ApiEnvelope format with field errors and request_id.

**Motivation:**
EduBoost V2 implements standardized error handling to ensure consistent API responses across all endpoints. The domain error handler catches EduBoostError subclasses (NotFoundError, ConsentRequiredError, etc.) and converts them to standardized responses. The validation error handler transforms Pydantic validation errors into field-level error messages, extracting field path, message, and error code. Field error construction extracts relevant information from Pydantic errors for client consumption. The error envelope creation wraps errors in ApiEnvelope format with code, message, field_errors, and remediation information. The JSON response return returns standardized error responses with appropriate HTTP status codes. This system provides consistent error responses with actionable information for clients, improving developer experience and debugging.

**Details:**
- **Domain Error Handler and Exception Catching:** The domain error handler catches EduBoostError subclasses (NotFoundError, ConsentRequiredError, etc.) and converts them to standardized responses [8a]. Exception handling takes ~1-5ms. This ensures that domain-specific errors are caught and converted to appropriate HTTP responses, providing consistent error handling across all endpoints. The handler pattern centralizes error conversion logic, preventing inconsistent error responses.
- **Validation Error Handler and Pydantic Transformation:** The validation error handler transforms Pydantic validation errors into field-level error messages [8b]. This extracts field path, message, and error code from Pydantic errors for client consumption. The transformation ensures that validation errors are presented in a structured, client-friendly format, enabling frontend applications to display field-specific error messages.
- **Field Error Construction and Client Consumption:** Field error construction extracts relevant information from Pydantic errors for client consumption [8c]. Error construction takes ~1-5ms. This ensures that field errors include all necessary information for client-side validation feedback, including the field path, error message, and error code. The structured field errors enable frontend applications to display precise validation feedback to users.
- **Error Envelope Creation and Standardized Format:** The error envelope creation wraps errors in ApiEnvelope format with code, message, field_errors, and remediation information [8d]. This provides a consistent error response format across all endpoints, enabling clients to parse errors uniformly. The envelope format includes remediation information to help clients understand how to resolve errors.
- **JSON Response Return and HTTP Status Codes:** The JSON response return returns standardized error responses with appropriate HTTP status codes [8e]. Response generation takes ~1-5ms. This ensures that error responses include the correct HTTP status code for the error type, enabling clients to handle errors appropriately based on the status code. Total error handling takes ~3-15ms.

**Location ID: 8a**
- **Title:** Domain Error Handler
- **Description:** Catches EduBoostError subclasses (NotFoundError, ConsentRequiredError, etc.)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:154

**Location ID: 8b**
- **Title:** Validation Error Handler
- **Description:** Transforms Pydantic validation errors into field-level error messages
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:176

**Location ID: 8c**
- **Title:** Field Error Construction
- **Description:** Extracts field path, message, and error code from Pydantic error
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:113

**Location ID: 8d**
- **Title:** Error Envelope Creation
- **Description:** Wraps error in ApiEnvelope with code, message, field_errors, remediation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:136

**Location ID: 8e**
- **Title:** JSON Response Return
- **Description:** Returns standardized error response with appropriate HTTP status code
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:134

### AI Guide: Exception to Standardized API Response

**Motivation:**
Standardized error handling ensures consistent API responses across all endpoints. By catching exceptions, constructing error envelopes with field-level details, and returning appropriate HTTP status codes, the system provides clear, actionable error responses to clients. The domain error handler catches EduBoostError subclasses (NotFoundError, ConsentRequiredError, etc.) and converts them to standardized responses. The validation error handler transforms Pydantic validation errors into field-level error messages, extracting field path, message, and error code. Field error construction extracts relevant information from Pydantic errors for client consumption. The error envelope creation wraps errors in ApiEnvelope format with code, message, field_errors, and remediation information. The JSON response return returns standardized error responses with appropriate HTTP status codes. This system provides consistent error responses with actionable information for clients, improving developer experience and debugging.

**Details:**

**Exception Handlers and Centralized Error Conversion**
The domain error handler catches EduBoostError subclasses for domain-specific errors with consistent handling [8a]. The validation error handler transforms Pydantic errors to provide field-level messages and validation feedback [8b]. These handlers ensure that all errors are converted to a standardized format, preventing inconsistent error responses across endpoints. The centralized handler pattern ensures that error conversion logic is maintained in one place, reducing the risk of inconsistencies.

**Error Construction and Structured Field Feedback**
Field error construction extracts field information including path, message, and error codes [8c]. The error envelope creation wraps errors in ApiEnvelope with a standardized format and remediation information [8d]. This provides clients with structured error data they can use to fix issues. The structured field errors enable frontend applications to display precise validation feedback to users, improving the user experience and reducing debugging time.

**Response Generation and HTTP Semantics**
The JSON response return returns an HTTP response with the appropriate status code and JSON format [8e]. This ensures that errors are returned with the correct HTTP semantics while maintaining a consistent response structure across all endpoints. The appropriate HTTP status codes enable clients to handle errors programmatically based on the status code, while the consistent JSON format ensures that error parsing logic is uniform across all endpoints.

## Trace ID: 9
**Title:** Request Lifecycle Middleware Chain

**Description:** Middleware execution flow: request_id injection, timing measurement, structured logging, and Prometheus metrics recording.

**Motivation:**
EduBoost V2 implements a middleware chain for request lifecycle management, observability, and performance monitoring. Request ID generation creates or extracts a correlation ID from the X-Request-ID header for distributed tracing across services. Context variables binding attaches request_id, app_env, and app_version to all log entries via structlog contextvars. Timing start records a high-precision timestamp before request processing for latency measurement. Request counter increment increments a Prometheus counter with method, endpoint, and status labels for request volume tracking. Latency histogram recording records request duration in a Prometheus histogram for percentile tracking (p50, p95, p99). Structured request log emits a JSON log with request_id, method, path, status, duration_ms, and client_ip for request lifecycle tracing. This middleware chain provides comprehensive observability for debugging, monitoring, and performance analysis.

**Details:**
- **Request ID Generation and Distributed Tracing:** Request ID generation creates or extracts a correlation ID from the X-Request-ID header for distributed tracing across services [9a]. Request ID generation takes ~1-5ms. This enables tracing of requests across multiple services, providing visibility into the complete request lifecycle and enabling debugging of distributed systems issues.
- **Context Variables Binding and Structured Logging:** Context variables binding attaches request_id, app_env, and app_version to all log entries via structlog contextvars [9b]. Context binding takes ~1-5ms. This ensures that all log entries include the necessary context for distributed tracing, enabling correlation of log entries across services and providing comprehensive observability.
- **Timing Start and Latency Measurement:** Timing start records a high-precision timestamp before request processing for latency measurement [9c]. Timing takes ~1-5ms. This enables accurate measurement of request processing time, providing visibility into performance characteristics and enabling detection of performance regressions.
- **Request Counter Increment and Volume Tracking:** Request counter increment increments a Prometheus counter with method, endpoint, and status labels for request volume tracking [9d]. Metrics recording takes ~1-5ms. This enables monitoring of request volume patterns, providing visibility into traffic patterns and enabling capacity planning.
- **Latency Histogram Recording and Percentile Tracking:** Latency histogram recording records request duration in a Prometheus histogram for percentile tracking (p50, p95, p99) [9e]. This enables monitoring of latency distribution, providing visibility into performance characteristics and enabling detection of performance outliers.
- **Structured Request Log and Request Lifecycle Tracing:** Structured request log emits a JSON log with request_id, method, path, status, duration_ms, and client_ip for request lifecycle tracing [9f]. Logging takes ~1-5ms. This provides comprehensive request lifecycle tracing, enabling debugging and monitoring of request patterns. Total middleware overhead takes ~5-25ms.

**Location ID: 9a**
- **Title:** Request ID Generation
- **Description:** Creates or extracts correlation ID for request tracing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:26

**Location ID: 9b**
- **Title:** Context Variables Binding
- **Description:** Attaches request_id, app_env, app_version to all log entries
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:28

**Location ID: 9c**
- **Title:** Timing Start
- **Description:** Records high-precision timestamp before request processing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:46

**Location ID: 9d**
- **Title:** Request Counter Increment
- **Description:** Increments Prometheus counter with method, endpoint, status labels
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:55

**Location ID: 9e**
- **Title:** Latency Histogram Recording
- **Description:** Records request duration in Prometheus histogram for percentile tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:56

**Location ID: 9f**
- **Title:** Structured Request Log
- **Description:** Emits JSON log with request_id, method, path, status, duration_ms, client_ip
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:71

### AI Guide: Request Lifecycle Middleware Chain

**Motivation:**
The middleware chain provides request lifecycle management, observability, and performance monitoring. Request ID injection enables distributed tracing, while timing measurement and metrics recording provide visibility into system performance. Request ID generation creates or extracts a correlation ID from the X-Request-ID header for distributed tracing across services. Context variables binding attaches request_id, app_env, and app_version to all log entries via structlog contextvars. Timing start records a high-precision timestamp before request processing for latency measurement. Request counter increment increments a Prometheus counter with method, endpoint, and status labels for request volume tracking. Latency histogram recording records request duration in a Prometheus histogram for percentile tracking (p50, p95, p99). Structured request log emits a JSON log with request_id, method, path, status, duration_ms, and client_ip for request lifecycle tracing. This middleware chain provides comprehensive observability for debugging, monitoring, and performance analysis.

**Details:**

**Request ID and Context for Distributed Tracing**
Request ID generation creates or extracts an ID for distributed tracing and correlation across services [9a]. Context variables binding attaches request_id, app_env, and app_version to logs for structured context [9b]. This ensures that all log entries can be correlated to specific requests, enabling tracing of requests across multiple services and providing comprehensive observability for debugging distributed systems issues.

**Timing Measurement and Performance Monitoring**
The timing start uses a high-precision timestamp for latency measurement and performance tracking [9c]. This enables accurate measurement of request processing time for performance monitoring and SLA compliance. The high-precision timing enables detection of even small performance regressions, ensuring that performance issues are identified early before they impact users.

**Metrics Recording and Volume Tracking**
The request counter increment uses a Prometheus counter for volume tracking with method and status labels [9d]. The latency histogram recording uses a Prometheus histogram for percentile tracking including p50, p95, and p99 [9e]. These metrics enable comprehensive monitoring of request volume and performance, providing visibility into traffic patterns and enabling capacity planning. The labeled metrics enable filtering by method, endpoint, and status, providing granular visibility into request patterns.

**Structured Logging and Request Lifecycle Tracing**
The structured request log creates a JSON log entry with request lifecycle information for debugging support [9f]. This provides a complete record of each request for troubleshooting and analysis. The structured JSON format enables machine-readable log entries that can be easily parsed and analyzed by log aggregation systems, providing comprehensive request lifecycle tracing and enabling efficient debugging and monitoring.

## Trace ID: 10
**Title:** AI Quota Enforcement (Rate Limiting)

**Description:** Daily AI request quota flow: Redis counter increment, limit comparison, and HTTP 429 response with retry-after header.

**Motivation:**
EduBoost V2 implements AI quota enforcement to control API costs and prevent abuse. The quota check entry validates that a user hasn't exceeded their daily AI request limit. Atomic counter increment uses Redis pipeline for atomic INCR + EXPIRE operations, ensuring accurate quota tracking even under concurrent requests. The Redis pipeline creation ensures the increment and expiration happen atomically, preventing race conditions. Limit comparison checks if usage exceeds FREE_DAILY_REQUEST_QUOTA (20 for free tier) against the counter value. When quota is exceeded, an HTTP 429 exception is raised with a Retry-After header set to seconds until tomorrow, providing clear guidance to clients. This system provides cost control and abuse prevention while providing clear feedback to users.

**Details:**
- **Quota Check Entry and Validation:** The quota check entry validates that a user hasn't exceeded their daily AI request limit [10a]. Quota check takes ~10-50ms. This ensures that users cannot exceed their allocated quota, providing cost control and preventing abuse. The validation happens before any AI processing, ensuring that quota limits are enforced early in the request lifecycle.
- **Atomic Counter Increment and Redis Pipeline:** Atomic counter increment uses Redis pipeline for atomic INCR + EXPIRE operations, ensuring accurate quota tracking even under concurrent requests [10b]. Redis operations take ~10-50ms. The Redis pipeline creation ensures the increment and expiration happen atomically, preventing race conditions. This atomic operation ensures that quota tracking is accurate even under high concurrency, preventing quota circumvention through race conditions.
- **Limit Comparison and Quota Enforcement:** Limit comparison checks if usage exceeds FREE_DAILY_REQUEST_QUOTA (20 for free tier) against the counter value [10c]. This provides configurable quota limits based on user tier, enabling differentiated service levels. The limit comparison is deterministic and fast, ensuring that quota enforcement does not significantly impact request performance.
- **Quota Exceeded Exception and Client Feedback:** When quota is exceeded, an HTTP 429 exception is raised with a Retry-After header set to seconds until tomorrow [10d]. This provides clear guidance to clients about when they can retry, improving the user experience. The Retry-After header enables clients to implement intelligent retry logic, reducing unnecessary retry attempts. Total quota check takes ~20-100ms.

**Location ID: 10a**
- **Title:** Quota Check Entry
- **Description:** Validates user hasn't exceeded daily AI request limit
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/rate_limiter.py:37

**Location ID: 10b**
- **Title:** Atomic Counter Increment
- **Description:** Increments Redis counter with 24-hour TTL for daily quota
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/rate_limiter.py:45

**Location ID: 10c**
- **Title:** Redis Pipeline Creation
- **Description:** Creates pipeline for atomic INCR + EXPIRE operations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/redis.py:51

**Location ID: 10d**
- **Title:** Limit Comparison
- **Description:** Checks if usage exceeds FREE_DAILY_REQUEST_QUOTA (20 for free tier)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/rate_limiter.py:47

**Location ID: 10e**
- **Title:** Quota Exceeded Exception
- **Description:** Raises HTTP 429 with Retry-After header set to seconds until tomorrow
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/rate_limiter.py:48

### AI Guide: AI Quota Enforcement (Rate Limiting)

**Motivation:**
AI quota enforcement controls API costs and prevents abuse through daily request limits. Using atomic Redis operations ensures accurate quota tracking even under concurrent load, while clear 429 responses provide feedback to clients. The quota check entry validates that a user hasn't exceeded their daily AI request limit. Atomic counter increment uses Redis pipeline for atomic INCR + EXPIRE operations, ensuring accurate quota tracking even under concurrent requests. The Redis pipeline creation ensures the increment and expiration happen atomically, preventing race conditions. Limit comparison checks if usage exceeds FREE_DAILY_REQUEST_QUOTA (20 for free tier) against the counter value. When quota is exceeded, an HTTP 429 exception is raised with a Retry-After header set to seconds until tomorrow, providing clear guidance to clients. This system provides cost control and abuse prevention while providing clear feedback to users.

**Details:**

**Quota Check and Atomic Operations**
The quota check entry validates the quota limit with a user-specific check for daily enforcement [10a]. The atomic counter increment uses a Redis counter with a 24-hour TTL as an atomic operation [10b]. This ensures that quota tracking is accurate even when multiple requests arrive simultaneously. The atomic operations prevent race conditions and ensure quota accuracy under concurrent load, preventing quota circumvention through race conditions.

**Redis Pipeline and Atomic Execution**
The Redis pipeline creation enables atomic INCR + EXPIRE operations with pipeline execution to prevent race conditions [10c]. This ensures that the counter increment and TTL setting happen atomically, preventing the counter from existing without an expiration time. The pipeline-based atomic execution ensures that quota tracking is consistent and that counters are automatically cleaned up after their TTL expires, preventing unbounded growth of quota tracking data.

**Limit Enforcement and Client Feedback**
The limit comparison checks against the FREE_DAILY_REQUEST_QUOTA for limit enforcement [10d]. When the quota is exceeded, a quota exceeded exception returns an HTTP 429 response with a Retry-After header for clear feedback [10e]. This provides clients with actionable information about when they can retry. The Retry-After header enables clients to implement intelligent retry logic, reducing unnecessary retry attempts and improving system efficiency. The clear error messages help users understand why their request was denied and when they can try again.
