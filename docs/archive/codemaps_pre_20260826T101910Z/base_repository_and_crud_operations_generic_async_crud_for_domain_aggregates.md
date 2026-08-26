# Base Repository and CRUD Operations: Generic Async CRUD for Domain Aggregates

Maps the repository pattern implementation from the generic BaseRepository class through concrete implementations to API/service usage. Core infrastructure at [1a-1e], concrete extensions at [2a-2e], session management at [3a-3d], API integration at [4a-4d], and service layer usage at [5a-5d].

## Trace ID: 1
**Title:** BaseRepository Generic CRUD Operations

**Description:** Core infrastructure - defines the generic async CRUD methods inherited by all domain repositories

**Motivation:**
EduBoost V2 implements a generic repository pattern using Python generics (TypeVar ModelT bound to Base) to provide type-safe async CRUD operations for all domain entities. The BaseRepository class defines standard CRUD methods (get, get_or_404, create, update, delete) that are inherited by concrete domain repositories, eliminating code duplication and ensuring consistent data access patterns. The get method executes SQLAlchemy 2.0 select queries with async support, returning scalar_one_or_none() for optional results. The get_or_404 method wraps get() and raises a typed NotFoundError when the entity is not found, converting database nulls to domain exceptions for proper API error handling. The create method instantiates models from kwargs, adds them to the session, flushes to get the ID without committing, and refreshes the instance. This pattern balances performance (flush without commit) with data integrity (transaction management).

**Details:**
- **Execution Flow:** Class Definition → Read Operations → get(id, db) → execute select query → return scalar_one_or_none() → get_or_404(id, db) → call self.get() → raise NotFoundError if None → Create Operation → create(db, **kwargs) → instantiate model → add to session → flush to DB → refresh instance → Update & Delete Operations → update(instance, db, **kwargs) → setattr for each field → add to session → flush & refresh → delete(instance, db) → db.delete() & flush
- **Concurrency Safety:** SQLAlchemy async sessions are thread-safe when used correctly. Each request gets its own session. Repository methods are stateless. No distributed locks needed as database handles concurrency. Transactions provide isolation between operations
- **Covered Objects:** BaseRepository class, Generic type parameter ModelT, SQLAlchemy 2.0 select syntax, async session management, scalar_one_or_none(), NotFoundError exception, model instantiation, session add/flush/refresh, update operations, delete operations
- **Timeouts:** Query execution: ~10-100ms depending on query complexity. Flush operation: ~10-50ms. Refresh operation: ~10-50ms. Total CRUD operation: ~30-200ms depending on operation
- **Migration Path:** From ad-hoc data access to repository pattern. Migration requires: 1) Create BaseRepository class, 2) Define generic CRUD methods, 3) Create concrete repositories extending base, 4) Update services to use repositories, 5) Remove ad-hoc database code
- **Error Handling:** Query failures raise SQLAlchemy exceptions. Not found errors raise NotFoundError. Flush failures raise database errors. All errors propagate to caller. Exception handling at service layer for business logic
- **Security Considerations:** Repository methods should not contain business logic. Input validation should happen before repository calls. SQL injection prevented by SQLAlchemy ORM. Sensitive data should be filtered at query level. Access control should be enforced at service layer

**Trace text diagram:**
```
BaseRepository[ModelT] Generic CRUD
├── Class Definition <-- 1a
├── Read Operations
│   ├── get(id, db) <-- base.py:23
│   │   ├── execute select query <-- 1b
│   │   └── return scalar_one_or_none() <-- base.py:25
│   └── get_or_404(id, db) <-- base.py:27
│       ├── call self.get() <-- 1f
│       └── raise NotFoundError if None <-- 1g
├── Create Operation
│   ├── create(db, **kwargs) <-- base.py:50
│   │   ├── instantiate model <-- 1c
│   │   ├── add to session <-- 1d
│   │   ├── flush to DB <-- 1e
│   │   └── refresh instance <-- base.py:54
└── Update & Delete Operations
    ├── update(instance, db, **kwargs) <-- base.py:57
    │   ├── setattr for each field <-- base.py:59
    │   ├── add to session <-- base.py:60
    │   └── flush & refresh <-- base.py:61
    └── delete(instance, db) <-- base.py:65
        └── db.delete() & flush <-- base.py:66
```

**Location ID: 1a**
- **Title:** Generic Repository Base Class
- **Description:** Type-safe generic repository using SQLAlchemy models
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:18

**Location ID: 1b**
- **Title:** Get Operation
- **Description:** Async query execution to fetch single entity by ID
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:24

**Location ID: 1c**
- **Title:** Create Operation
- **Description:** Instantiate model from kwargs and prepare for persistence
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:51

**Location ID: 1d**
- **Title:** Add to Session
- **Description:** Stage new instance in SQLAlchemy session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:52

**Location ID: 1e**
- **Title:** Flush Without Commit
- **Description:** Persist to DB and get ID without committing transaction
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:53

**Location ID: 1f**
- **Title:** Get or 404 Pattern
- **Description:** Reuse get() method for existence check
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:29

**Location ID: 1g**
- **Title:** Raise Domain Exception
- **Description:** Convert None result to typed exception for API layer
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:31

### AI Guide: BaseRepository Generic CRUD Operations

**Motivation:**
The BaseRepository class exists to standardize common persistence operations across EduBoost's domain model. It prevents each repository from re-implementing the same SQLAlchemy create/read/update/delete mechanics and makes repository behavior easier for agents and developers to predict.

**Details:**

**Generic Type Safety**
The BaseRepository class uses Python generics (TypeVar ModelT bound to Base) to provide type-safe async CRUD operations for all domain entities [1a]. This generic binding ensures that concrete repositories inherit type-safe operations while eliminating code duplication.

**Read Operations**
The get method executes SQLAlchemy 2.0 select queries with async support, returning scalar_one_or_none() for optional results [1b]. The get_or_404 method wraps get() and raises a typed NotFoundError when the entity is not found [1f][1g], converting database nulls to domain exceptions for proper API error handling.

**Create Operations**
The create method instantiates models from kwargs, adds them to the session, flushes to get the ID without committing, and refreshes the instance [1c][1d][1e]. This pattern balances performance (flush without commit) with data integrity (transaction management). The add operation stages the instance in the session without immediate commit, enabling transaction control.

**Update and Delete Operations**
The update method uses setattr for each field, adds to session, and flushes & refreshes. The delete method calls db.delete() and flushes. These operations follow the same flush-without-commit pattern as create, ensuring consistent transaction boundaries.

## Trace ID: 2
**Title:** Concrete Repository Extensions

**Description:** Data access layer - shows how domain repositories extend BaseRepository with custom queries and business logic

**Motivation:**
EduBoost V2 uses concrete repository classes that extend BaseRepository to provide domain-specific data access while inheriting generic CRUD operations. The LearnerRepository extends BaseRepository[Learner] and binds the generic ModelT to the concrete Learner ORM model, providing type-safe operations for learner entities. The get_by_id method wraps the inherited get() method with UUID conversion, providing a convenient API for string-based IDs. The DiagnosticRepository similarly extends BaseRepository[DiagnosticSession] and provides domain-specific methods like create_session that wrap inherited create() with domain-specific parameters. This inheritance pattern eliminates code duplication while allowing domain-specific customization. All BaseRepository methods are available to concrete repositories, providing a consistent data access interface across the application.

**Details:**
- **Execution Flow:** BaseRepository[ModelT] (app/core/base.py) → Generic type parameter binding → Inherited CRUD methods → Concrete Repository Extensions → LearnerRepository → class declaration → model = Learner binding → get_by_id() wrapper → calls self.get(UUID(...)) → DiagnosticRepository → class declaration → model = DiagnosticSession binding → create_session() wrapper → calls self.create(...) → Inheritance Flow → BaseRepository methods available to all concrete repositories
- **Concurrency Safety:** Each repository instance is stateless. Sessions are injected per request. Repository methods are thread-safe. No shared state between instances. Database handles concurrency
- **Covered Objects:** BaseRepository inheritance, generic type binding, LearnerRepository, DiagnosticRepository, model binding, custom methods, UUID conversion, domain-specific parameters
- **Timeouts:** Repository instantiation: ~1-5ms. Method call overhead: ~1-5ms. Inherited method execution: ~30-200ms. Total operation: ~30-210ms
- **Migration Path:** From ad-hoc queries to repository pattern. Migration requires: 1) Create concrete repository classes, 2) Extend BaseRepository, 3) Bind model type parameter, 4) Add custom methods, 5) Update services to use repositories
- **Error Handling:** Inherited methods propagate errors. Custom methods can add validation. Type errors caught at compile time. UUID conversion errors handled. All errors propagate to service layer
- **Security Considerations:** Custom methods should validate inputs. Domain-specific logic should be in services. Repository should not contain business rules. Access control enforced at service layer. Sensitive data filtered at query level

**Trace text diagram:**
```
Repository Pattern Hierarchy
├── BaseRepository[ModelT] (app/core/base.py) <-- base.py:18
│   ├── Generic type parameter binding <-- base.py:15
│   └── Inherited CRUD methods
│
├── Concrete Repository Extensions
│   ├── LearnerRepository
│   │   ├── class declaration <-- 2a
│   │   ├── model = Learner binding <-- 2b
│   │   └── get_by_id() wrapper <-- learner_repository.py:27
│   │       └── calls self.get(UUID(...)) <-- 2c
│   │
│   └── DiagnosticRepository
│       ├── class declaration <-- 2d
│       ├── model = DiagnosticSession binding <-- diagnostic_repository.py:17
│       └── create_session() wrapper <-- diagnostic_repository.py:34
│           └── calls self.create(...) <-- 2e
│
└── Inheritance Flow
    └── BaseRepository methods available
        to all concrete repositories
```

**Location ID: 2a**
- **Title:** Learner Repository Declaration
- **Description:** Extends BaseRepository with Learner model type parameter
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/learner_repository.py:15

**Location ID: 2b**
- **Title:** Model Binding
- **Description:** Binds generic ModelT to concrete Learner ORM model
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/learner_repository.py:16

**Location ID: 2c**
- **Title:** Custom Get Method
- **Description:** Delegates to inherited get() with UUID conversion
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/learner_repository.py:29

**Location ID: 2d**
- **Title:** Diagnostic Repository
- **Description:** Another concrete repository for diagnostic sessions
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/diagnostic_repository.py:16

**Location ID: 2e**
- **Title:** Domain-Specific Create
- **Description:** Wraps inherited create() with domain-specific parameters
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/diagnostic_repository.py:48

### AI Guide: Concrete Repository Extensions

**Motivation:**
Concrete repository classes extend BaseRepository to provide domain-specific data access while inheriting generic CRUD operations. This inheritance pattern eliminates code duplication while allowing domain-specific customization, ensuring all repositories share a consistent data access interface.

**Details:**

**Type Binding and Inheritance**
The LearnerRepository extends BaseRepository[Learner] and binds the generic ModelT to the concrete Learner ORM model [2a][2b]. This binding provides type-safe operations for learner entities while inheriting all BaseRepository methods. The DiagnosticRepository similarly extends BaseRepository[DiagnosticSession] with its own model binding [2d].

**Custom Method Wrappers**
The get_by_id method wraps the inherited get() method with UUID conversion, providing a convenient API for string-based IDs [2c]. The create_session method wraps inherited create() with domain-specific parameters [2e]. These wrappers provide domain-specific convenience while delegating to the base implementation.

**Inheritance Benefits**
All BaseRepository methods are available to concrete repositories, providing a consistent data access interface across the application. This inheritance ensures that new repositories automatically get CRUD operations without re-implementation.

## Trace ID: 3
**Title:** Async Database Session Lifecycle

**Description:** Infrastructure layer - manages async session creation, dependency injection, and transaction boundaries

**Motivation:**
EduBoost V2 uses SQLAlchemy 2.0 with asyncpg driver for async database operations. The create_async_engine function initializes the asyncpg-backed SQLAlchemy engine with connection pooling. The async_sessionmaker creates a session factory with expire_on_commit=False to prevent detached instance errors, autocommit=False for transaction control, and autoflush=False for explicit flush control. The get_db function is a FastAPI dependency that yields an async session per request, managing the request-scoped transaction lifecycle. On success, the session commits automatically. On exception, the session rolls back and re-raises the exception. This pattern ensures proper transaction boundaries, automatic cleanup, and error handling for all database operations. The session context manager ensures resources are released even if exceptions occur.

**Details:**
- **Execution Flow:** Application Startup → create_async_engine() → asyncpg driver connection → async_sessionmaker() → expire_on_commit=False → autocommit=False → autoflush=False → Per-Request Lifecycle → get_db() dependency → AsyncSessionLocal() context → yield session to route → Success path → session.commit() → Exception path → session.rollback() → re-raise exception
- **Concurrency Safety:** Connection pool manages concurrent connections. Each request gets isolated session. Sessions are not shared between requests. Database handles transaction isolation. No distributed locks needed
- **Covered Objects:** async engine creation, asyncpg driver, session factory, session configuration, FastAPI dependency injection, transaction management, commit/rollback, exception handling
- **Timeouts:** Engine creation: ~100-500ms. Session creation: ~10-50ms. Query execution: ~10-100ms. Commit: ~10-50ms. Rollback: ~10-50ms. Total request: ~50-500ms
- **Migration Path:** From sync to async SQLAlchemy. Migration requires: 1) Install asyncpg driver, 2) Create async engine, 3) Configure session factory, 4) Update dependency injection, 5) Convert queries to async
- **Error Handling:** Connection failures raise SQLAlchemy errors. Transaction failures trigger rollback. Exception handling ensures cleanup. Errors re-raised for service layer. All errors logged with context
- **Security Considerations:** Connection string should use environment variables. Pool size should be configured appropriately. Sessions should not be shared. Credentials should not be hardcoded. Connection limits should be enforced

**Trace text diagram:**
```
Database Configuration & Session Lifecycle
├── Application Startup
│   ├── create_async_engine() <-- 3a
│   │   └── asyncpg driver connection
│   └── async_sessionmaker() <-- 3b
│       └── expire_on_commit=False <-- database.py:43
│           └── autocommit=False <-- database.py:44
│           └── autoflush=False <-- database.py:45
└── Per-Request Lifecycle
    └── get_db() dependency <-- database.py:61
        ├── AsyncSessionLocal() context <-- 3c
        │   └── yield session to route <-- database.py:65
        ├── Success path
        │   └── session.commit() <-- 3d
        └── Exception path <-- database.py:67
            └── session.rollback() <-- 3e
                └── re-raise exception <-- database.py:69
```

**Location ID: 3a**
- **Title:** Async Engine Creation
- **Description:** Initialize asyncpg-backed SQLAlchemy engine
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:39

**Location ID: 3b**
- **Title:** Session Factory
- **Description:** Create async session factory with autocommit disabled
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:41

**Location ID: 3c**
- **Title:** Session Context Manager
- **Description:** FastAPI dependency yields session per request
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:63

**Location ID: 3d**
- **Title:** Auto-Commit on Success
- **Description:** Commits transaction if no exception raised
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:66

**Location ID: 3e**
- **Title:** Auto-Rollback on Error
- **Description:** Ensures transaction rollback on any exception
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:68

### AI Guide: Async Database Session Lifecycle

**Motivation:**
The async database session lifecycle manages connection pooling, session creation, and transaction boundaries for all database operations. Using SQLAlchemy 2.0 with asyncpg driver provides async support while the session factory and dependency injection ensure proper resource management and transaction control.

**Details:**

**Engine and Session Factory**
The create_async_engine function initializes the asyncpg-backed SQLAlchemy engine with connection pooling [3a]. The async_sessionmaker creates a session factory with expire_on_commit=False to prevent detached instance errors, autocommit=False for transaction control, and autoflush=False for explicit flush control [3b].

**Dependency Injection**
The get_db function is a FastAPI dependency that yields an async session per request, managing the request-scoped transaction lifecycle [3c]. The session context manager ensures resources are released even if exceptions occur.

**Transaction Management**
On success, the session commits automatically [3d]. On exception, the session rolls back and re-raises the exception [3e]. This pattern ensures proper transaction boundaries, automatic cleanup, and error handling for all database operations.

## Trace ID: 4
**Title:** Repository Usage in API Routes

**Description:** Presentation layer - demonstrates dependency injection and repository usage in FastAPI endpoints

**Motivation:**
EduBoost V2 uses FastAPI dependency injection to provide async database sessions to API routes. The get_db dependency yields an AsyncSession per request, which is injected into route handlers. The create_learner route handler receives the session via dependency injection and instantiates a LearnerRepository with the injected session. The repository's create method is called to persist the learner, which internally uses BaseRepository.create() to instantiate the model, add it to the session, flush to get the ID, and refresh the instance. The resulting ORM model is converted to a Pydantic response schema using model_validate() for type-safe serialization. After the route handler completes, the get_db dependency automatically commits the transaction on success or rolls back on exception. This pattern ensures clean separation of concerns, proper transaction management, and type-safe API responses.

**Details:**
- **Execution Flow:** POST /learners endpoint → FastAPI dependency injection → get_db() yields AsyncSession → create_learner() route handler → LearnerRepository(db) init → repo.create() call → BaseRepository.create() → instance = Learner(**kwargs) → db.add(instance) → await db.flush() → LearnerResponse.model_validate() → get_db() cleanup → await session.commit()
- **Concurrency Safety:** Each request gets isolated session. Repository instances are request-scoped. No shared state between requests. Database handles concurrency. FastAPI manages dependency lifecycle
- **Covered Objects:** FastAPI dependency injection, async session, repository instantiation, repository create call, BaseRepository create, model instantiation, session add/flush, Pydantic response validation, transaction commit
- **Timeouts:** Dependency injection: ~1-5ms. Repository instantiation: ~1-5ms. Create operation: ~30-100ms. Response validation: ~1-5ms. Commit: ~10-50ms. Total request: ~50-200ms
- **Migration Path:** From manual session management to dependency injection. Migration requires: 1) Create get_db dependency, 2) Inject session into routes, 3) Instantiate repositories with session, 4) Use repository methods, 5. Convert ORM to Pydantic responses
- **Error Handling:** Dependency injection failures fail request. Repository errors propagate to handler. Validation errors raise HTTP exceptions. Transaction errors trigger rollback. All errors return proper HTTP responses
- **Security Considerations:** Dependency injection should not expose secrets. Response validation should filter sensitive data. Input validation should happen before repository. Access control should be enforced. Session should not be shared between requests

**Trace text diagram:**
```
FastAPI Request Lifecycle
└── POST /learners endpoint <-- learners.py:24
    ├── FastAPI dependency injection
    │   └── get_db() yields AsyncSession <-- 4a
    ├── create_learner() route handler <-- learners.py:25
    │   ├── LearnerRepository(db) init <-- 4b
    │   ├── repo.create() call <-- 4c
    │   │   └── BaseRepository.create() <-- base.py:50
    │   │       ├── instance = Learner(**kwargs) <-- base.py:51
    │   │       ├── db.add(instance) <-- base.py:52
    │   │       └── await db.flush() <-- base.py:53
    │   └── LearnerResponse.model_validate() <-- 4d
    └── get_db() cleanup
        └── await session.commit() <-- database.py:66
```

**Location ID: 4a**
- **Title:** Session Dependency Injection
- **Description:** FastAPI injects async session from get_db dependency
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:27

**Location ID: 4b**
- **Title:** Repository Instantiation
- **Description:** Create repository instance with injected session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:30

**Location ID: 4c**
- **Title:** Repository Create Call
- **Description:** Invoke inherited create() method from BaseRepository
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:31

**Location ID: 4d**
- **Title:** Response Model Validation
- **Description:** Convert ORM model to Pydantic response schema
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:37

### AI Guide: Repository Usage in API Routes

**Motivation:**
API routes use dependency injection to receive async sessions and instantiate repositories for data access. This pattern ensures clean separation of concerns, proper transaction management, and type-safe API responses while keeping route handlers thin.

**Details:**

**Session Injection**
The get_db dependency yields an AsyncSession per request, which is injected into route handlers [4a]. This ensures each request gets an isolated session with proper lifecycle management.

**Repository Instantiation**
The create_learner route handler receives the session via dependency injection and instantiates a LearnerRepository with the injected session [4b]. The repository's create method is called to persist the learner [4c], which internally uses BaseRepository.create() to instantiate the model, add it to the session, flush to get the ID, and refresh the instance.

**Response Validation**
The resulting ORM model is converted to a Pydantic response schema using model_validate() for type-safe serialization [4d]. After the route handler completes, the get_db dependency automatically commits the transaction on success or rolls back on exception.

## Trace ID: 5
**Title:** Repository Usage in Service Layer

**Description:** Business logic layer - shows constructor injection and repository usage in application services

**Motivation:**
EduBoost V2 uses constructor injection to provide repositories to application services, enabling testability and separation of concerns. The DiagnosticServiceV2 accepts repositories as constructor dependencies, storing them as instance variables for use in business logic methods. The run_diagnostic method delegates data access to the learner_repository.get_by_id() method, keeping business logic separate from data access. The GamificationServiceV2 similarly accepts repositories and calls domain-specific repository methods like get_profile_rows(). FastAPI dependency injection is used to create repository instances via factory functions like get_lesson_repository(), which receives an AsyncSession via Depends(get_db) and returns a LessonRepository(db). This pattern enables unit testing by allowing mock repositories to be injected, keeps business logic clean of data access details, and provides a clear separation between service layer and data access layer.

**Details:**
- **Execution Flow:** DiagnosticServiceV2 → __init__() constructor → stores repository references → run_diagnostic() method → await learner_repository.get_by_id() → GamificationServiceV2 → __init__() constructor → stores repository reference → get_profile() method → await repository.get_profile_rows() → FastAPI Dependency Injection → get_lesson_repository() factory → receives AsyncSession via Depends(get_db) → returns LessonRepository(db)
- **Concurrency Safety:** Service instances are request-scoped. Repositories are injected per request. No shared state between instances. Database handles concurrency. Constructor injection is thread-safe
- **Covered Objects:** Service classes, constructor injection, repository references, business logic methods, domain-specific repository methods, FastAPI dependency injection, factory functions
- **Timeouts:** Service instantiation: ~1-5ms. Repository call: ~30-200ms. Business logic: varies by complexity. Total service operation: ~50-500ms
- **Migration Path:** From ad-hoc data access to service layer. Migration requires: 1) Create service classes, 2) Add constructor injection, 3) Move business logic to services, 4) Delegate data access to repositories, 5) Update API routes to use services
- **Error Handling:** Repository errors propagate to services. Business logic errors raised appropriately. Validation errors handled in services. All errors propagate to API layer. Services can add context to errors
- **Security Considerations:** Services should enforce access control. Business logic should validate inputs. Repositories should not contain business rules. Sensitive data filtered at service level. Constructor injection enables testing

**Trace text diagram:**
```
Service Layer Repository Usage
├── DiagnosticServiceV2 <-- diagnostic_service_v2.py:6
│   ├── __init__() constructor <-- 5a
│   │   └── stores repository references <-- diagnostic_service_v2.py:8
│   └── run_diagnostic() method <-- diagnostic_service_v2.py:12
│       └── await learner_repository.get_by_id() <-- 5b
│
├── GamificationServiceV2 <-- gamification_service_v2.py:8
│   ├── __init__() constructor <-- gamification_service_v2.py:9
│   │   └── stores repository reference <-- gamification_service_v2.py:10
│   └── get_profile() method <-- gamification_service_v2.py:12
│       └── await repository.get_profile_rows() <-- 5c
│
└── FastAPI Dependency Injection
    └── get_lesson_repository() factory <-- 5d
        ├── receives AsyncSession via Depends(get_db) <-- lesson_repository.py:167
        └── returns LessonRepository(db) <-- lesson_repository.py:169
```

**Location ID: 5a**
- **Title:** Service Constructor Injection
- **Description:** Accept repositories as constructor dependencies
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_service_v2.py:7

**Location ID: 5b**
- **Title:** Repository Query in Service
- **Description:** Service delegates data access to repository
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_service_v2.py:13

**Location ID: 5c**
- **Title:** Custom Repository Method
- **Description:** Service calls domain-specific repository query
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/gamification_service_v2.py:13

**Location ID: 5d**
- **Title:** Repository Factory Function
- **Description:** FastAPI dependency for direct repository injection
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/lesson_repository.py:168

### AI Guide: Repository Usage in Service Layer

**Motivation:**
Services use constructor injection to receive repositories, enabling testability and separation of concerns. This pattern allows unit testing with mock repositories, keeps business logic clean of data access details, and provides a clear separation between service layer and data access layer.

**Details:**

**Constructor Injection**
The DiagnosticServiceV2 accepts repositories as constructor dependencies, storing them as instance variables for use in business logic methods [5a]. The GamificationServiceV2 similarly accepts repositories and stores them as instance variables.

**Data Access Delegation**
The run_diagnostic method delegates data access to the learner_repository.get_by_id() method [5b], keeping business logic separate from data access. The get_profile method calls domain-specific repository methods like get_profile_rows() [5c].

**Factory Functions**
FastAPI dependency injection is used to create repository instances via factory functions like get_lesson_repository() [5d], which receives an AsyncSession via Depends(get_db) and returns a LessonRepository(db). This enables services to receive pre-configured repository instances while maintaining testability.

## Trace ID: 6
**Title:** Alternative Repository Patterns

**Description:** Legacy and specialized patterns - repositories using raw SQL, asyncpg pools, or manual session management

**Motivation:**
EduBoost V2 contains alternative repository patterns that deviate from the BaseRepository pattern for various reasons. The GuardianRepository uses a manual pattern without BaseRepository inheritance, directly managing session operations like db.add() and db.flush(). The AssessmentRepository uses raw SQL with text() for complex queries that are difficult to express in ORM, providing performance optimization for specific use cases. The ConsentRepository uses asyncpg connection pools instead of SQLAlchemy for specialized async operations, bypassing the ORM layer for direct database access. The ItemBankRepository uses a class-based pattern without BaseRepository extension, managing sessions manually. These alternative patterns exist due to legacy code, performance requirements, or specialized use cases. The codebase is gradually migrating to the BaseRepository pattern for consistency, but these alternatives remain where they provide specific value.

**Details:**
- **Execution Flow:** Legacy Manual Pattern (repositories.py) → GuardianRepository class → create() method → self.db.add(guardian) → await self.db.flush() → Raw SQL Pattern (assessment_repository.py) → AssessmentRepository class → list_assessments() method → session.execute(text(...)) → SQL query string → AsyncPG Pool Pattern (consent_repository.py) → ConsentRepository class → __init__(pool: asyncpg.Pool) → get_active_for_learner() → await self._pool.fetchrow(...) → Class-Based Without Inheritance → ItemBankRepository class → __init__(db: AsyncSession) → get_item() method → await self.db.execute(...)
- **Concurrency Safety:** Manual patterns require careful session management. AsyncPG pools manage connections. Raw SQL uses database concurrency. No distributed locks needed. Each pattern handles concurrency differently
- **Covered Objects:** Manual session management, raw SQL execution, asyncpg connection pools, class-based repositories, legacy patterns, specialized patterns, performance optimization
- **Timeouts:** Manual operations: ~30-200ms. Raw SQL: ~10-100ms. AsyncPG operations: ~10-50ms. Total operation varies by pattern
- **Migration Path:** From alternative patterns to BaseRepository. Migration requires: 1) Identify alternative patterns, 2) Create BaseRepository extension, 3) Migrate methods, 4) Update usage, 5) Remove legacy code
- **Error Handling:** Manual patterns require explicit error handling. Raw SQL errors need translation. AsyncPG errors differ from SQLAlchemy. All patterns need proper exception handling
- **Security Considerations:** Raw SQL requires parameterization. AsyncPG pools need connection limits. Manual patterns need session cleanup. Legacy code may have security issues. Audit for SQL injection risks

**Trace text diagram:**
```
Repository Pattern Variations in EduBoost V2

Legacy Manual Pattern (repositories.py)
├── GuardianRepository class <-- 6a
│   └── create() method <-- repositories.py:30
│       └── self.db.add(guardian) <-- 6b
│           └── await self.db.flush() <-- repositories.py:33

Raw SQL Pattern (assessment_repository.py)
└── AssessmentRepository class <-- assessment_repository.py:14
    └── list_assessments() method <-- assessment_repository.py:15
        └── session.execute(text(...)) <-- 6c
            └── SQL query string <-- assessment_repository.py:24

AsyncPG Pool Pattern (consent_repository.py)
└── ConsentRepository class <-- consent_repository.py:17
    ├── __init__(pool: asyncpg.Pool) <-- 6d
    └── get_active_for_learner() <-- consent_repository.py:21
        └── await self._pool.fetchrow(...) <-- consent_repository.py:24

Class-Based Without Inheritance
└── ItemBankRepository class <-- item_bank_repository.py:22
    ├── __init__(db: AsyncSession) <-- 6e
    └── get_item() method <-- item_bank_repository.py:33
        └── await self.db.execute(...) <-- item_bank_repository.py:35
```

**Location ID: 6a**
- **Title:** Manual Repository Pattern
- **Description:** Legacy pattern without BaseRepository inheritance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:26

**Location ID: 6b**
- **Title:** Direct Session Usage
- **Description:** Manually manages session without base class helpers
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:32

**Location ID: 6c**
- **Title:** Raw SQL Execution
- **Description:** Uses text() for raw SQL instead of ORM
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/assessment_repository.py:23

**Location ID: 6d**
- **Title:** AsyncPG Pool Pattern
- **Description:** Uses asyncpg connection pool instead of SQLAlchemy
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/consent_repository.py:18

**Location ID: 6e**
- **Title:** Class-Based Without Inheritance
- **Description:** Session-based repository without BaseRepository extension
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:28

### AI Guide: Alternative Repository Patterns

**Motivation:**
The codebase contains alternative repository patterns that deviate from BaseRepository for legacy, performance, or specialized reasons. These patterns exist due to historical code, performance requirements for complex queries, or specialized use cases that benefit from direct database access.

**Details:**

**Manual Pattern Without Inheritance**
The GuardianRepository uses a manual pattern without BaseRepository inheritance, directly managing session operations like db.add() and db.flush() [6a][6b]. This legacy pattern lacks the benefits of the base class but remains in the codebase for historical reasons.

**Raw SQL for Performance**
The AssessmentRepository uses raw SQL with text() for complex queries that are difficult to express in ORM [6c]. This provides performance optimization for specific use cases where ORM query generation would be inefficient.

**AsyncPG Pool Pattern**
The ConsentRepository uses asyncpg connection pools instead of SQLAlchemy for specialized async operations [6d], bypassing the ORM layer for direct database access. This pattern offers performance benefits for specific async operations.

**Class-Based Without BaseRepository**
The ItemBankRepository uses a class-based pattern without BaseRepository extension, managing sessions manually [6e]. These alternative patterns are gradually being migrated to BaseRepository for consistency, but remain where they provide specific value.
