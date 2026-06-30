# EduBoost V2 API Documentation and Response Envelope System

This map covers the API documentation generation pipeline (Sphinx and MkDocs), OpenAPI schema generation and validation, and the V2 response envelope system that wraps all API responses in a canonical structure. Key entry points include the Sphinx build command [1a], OpenAPI generation script [3b], and the envelope route wrapper [4c].

## Trace ID: 1
**Title:** Sphinx API Documentation Build Pipeline

**Description:** Sphinx system that generates HTML API reference from Python docstrings using autodoc extensions

**Trace text diagram:**
```
Sphinx API Documentation Build Pipeline
├── Developer runs `make html` command
│   └── Makefile html target <-- 1a
│       └── sphinx-build -b html invocation
│           ├── Load Sphinx configuration
│           │   ├── conf.py reads extensions list <-- 1b
│           │   └── napoleon_google_docstring=True <-- 1c
│           ├── Parse RST source files
│           │   ├── index.rst root document <-- index.rst:1
│           │   │   └── .. toctree:: directive <-- 1d
│           │   └── api/core.rst module docs <-- core.rst:1
│           │       └── .. automodule:: directive <-- 1e
│           ├── autodoc extracts Python docstrings
│           │   └── Reads app.core.config members <-- core.rst:16
│           └── Generate HTML output
│               └── docs/api/build/html/index.html
```

**Location ID: 1a**
**Title:** Sphinx Build Command Execution
**Description:** Makefile target that invokes sphinx-build to generate HTML from RST source files
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/api/Makefile:17

**Location ID: 1b**
**Title:** Sphinx Extensions Registration
**Description:** Registers autodoc, napoleon, viewcode extensions for docstring extraction
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/api/source/conf.py:17

**Location ID: 1c**
**Title:** Google-Style Docstring Parser Configuration
**Description:** Enables parsing of Google-format docstrings from Python source files
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/api/source/conf.py:37

**Location ID: 1d**
**Title:** Navigation Tree Definition
**Description:** Defines hierarchical navigation structure for API reference sections
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/api/source/index.rst:20

**Location ID: 1e**
**Title:** Autodoc Module Extraction Directive
**Description:** Sphinx directive that extracts all members from app.core.config module
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/api/source/api/core.rst:15

### AI Guide: Sphinx API Documentation Build Pipeline

**Motivation:**
Sphinx API documentation provides comprehensive HTML reference for Python modules. autodoc extension automatically extracts docstrings from source code. napoleon extension enables Google-style docstring parsing. RST source files organize documentation structure. This pipeline transforms Python docstrings into browsable HTML documentation for developers. The Makefile html target invokes sphinx-build to generate HTML from RST source files. conf.py registers extensions for docstring extraction and Google-style parsing. index.rst serves as the root document with navigation structure. api/core.rst uses automodule directive to extract module documentation. This system provides automated, comprehensive API documentation generation.

**Details:**

**Build Process Orchestration and CI Integration**
Makefile html target invokes sphinx-build with -b html flag [1a]. This generates static HTML site from RST sources. Build process outputs to docs/api/build/html/ directory. Command-line interface enables automated documentation generation in CI pipelines. The automated build process ensures that documentation is always up-to-date with the codebase, reducing the risk of documentation drift.

**Configuration and Extensions for Docstring Extraction**
conf.py registers essential extensions: sphinx.ext.autodoc for automatic docstring extraction [1b], sphinx.ext.napoleon for Google-style docstring parsing [1c], sphinx.ext.viewcode for source code links. These extensions enable comprehensive documentation generation without manual markup. The extension-based architecture allows for flexible documentation generation, enabling support for different docstring formats and additional features like source code linking.

**Source Organization and Navigation Structure**
index.rst serves as root document with toctree directive for navigation [1d]. api/core.rst uses automodule directive to extract documentation from app.core.config module [1e]. RST format provides semantic structure for documentation organization. The hierarchical organization enables developers to navigate the documentation intuitively, with clear separation between different modules and components.

**Output Generation and Developer Experience**
autodoc extracts Python docstrings and renders them as HTML documentation. Google-style docstrings are parsed into structured sections. Generated HTML includes navigation, search, and cross-references. This output provides developer-friendly API reference. The generated documentation includes features like search functionality, cross-references between modules, and source code links, significantly improving the developer experience.

## Trace ID: 2
**Title:** MkDocs Site Generation with mkdocstrings

**Description:** MkDocs system that builds operational documentation site with inline API references using mkdocstrings plugin

**Trace text diagram:**
```
MkDocs Site Generation Pipeline
├── Makefile entry point
│   └── mkdocs serve <-- 2a
│       └── Reads mkdocs.yml configuration
│           ├── Plugin registration <-- mkdocs.yml:53
│           │   └── mkdocstrings plugin <-- 2b
│           │       └── Python handler config <-- 2c
│           └── Navigation structure <-- mkdocs.yml:27
│               └── API Reference section <-- 2d
│                   └── Reference markdown files
│                       └── docs/reference/core.md <-- core.md:1
│                           └── ::: directive <-- 2e
│                               └── Extract docstrings
│                                   └── Render HTML output
```

**Location ID: 2a**
**Title:** MkDocs Development Server Launch
**Description:** Makefile target that starts live-reload development server for documentation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/Makefile:62

**Location ID: 2b**
**Title:** mkdocstrings Plugin Registration
**Description:** Enables inline Python API documentation rendering within Markdown files
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/mkdocs.yml:55

**Location ID: 2c**
**Title:** Python Handler Configuration
**Description:** Configures Python-specific docstring extraction with Google style support
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/mkdocs.yml:57

**Location ID: 2d**
**Title:** API Reference Navigation Section
**Description:** Defines API Reference section in site navigation hierarchy
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/mkdocs.yml:44

**Location ID: 2e**
**Title:** mkdocstrings Extraction Directive
**Description:** Triple-colon syntax triggers mkdocstrings to extract and render module documentation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/reference/core.md:6

### AI Guide: MkDocs Site Generation with mkdocstrings

**Motivation:**
MkDocs site generation creates operational documentation with integrated API references. mkdocstrings plugin enables inline Python documentation extraction. Material theme provides professional presentation. Live reload development server supports efficient authoring. This system combines narrative documentation with automatic API reference generation. The Makefile target docs launches mkdocs serve with live reload. mkdocs.yml registers mkdocstrings plugin for Python documentation extraction. Navigation structure defines API Reference section. docs/reference/core.md uses ::: directive to extract module documentation. This system provides a cohesive documentation site with both narrative and reference content.

**Details:**

**Development Workflow and Live Reload**
Makefile target docs launches mkdocs serve with live reload [2a]. Development server automatically rebuilds on file changes. Material theme provides instant preview of styling. This workflow enables efficient documentation authoring with immediate feedback. The live reload capability significantly improves the documentation authoring experience by providing instant visual feedback on changes.

**Plugin Configuration and Docstring Extraction**
mkdocs.yml registers mkdocstrings plugin for Python documentation extraction [2b]. Python handler configuration enables Google-style docstring parsing [2c]. Plugin options specify source paths and extraction settings. This configuration enables seamless API documentation integration. The plugin-based architecture allows for flexible documentation generation, enabling support for different docstring formats and customization of the extraction process.

**Content Organization and Navigation Structure**
Navigation structure defines API Reference section in site hierarchy [2d]. docs/reference/core.md uses ::: directive to extract module documentation [2e]. Triple-colon syntax specifies which Python modules to document. This organization integrates API docs with narrative documentation. The integrated approach ensures that API documentation is seamlessly woven into the broader documentation site, providing a cohesive user experience.

**Output Generation and Professional Presentation**
mkdocstrings automatically extracts docstrings from Python modules. Google-style docstrings render as structured documentation. Material theme provides professional styling. This integration creates cohesive documentation site with both narrative and reference content. The Material theme provides a modern, responsive design that enhances the readability and accessibility of the documentation across different devices and screen sizes.

## Trace ID: 3
**Title:** OpenAPI Schema Generation and CI Validation

**Description:** Script that generates OpenAPI schema from FastAPI app and CI workflow that validates schema drift

**Trace text diagram:**
```
OpenAPI Schema Generation and CI Validation Pipeline
├── GitHub Actions Workflow
│   └── openapi-contract job <-- 3a
│       └── runs: generate_openapi.py --check <-- openapi-contract.yml:74
│
└── OpenAPI Generation Script
    ├── main() orchestrator <-- generate_openapi.py:103
    │   ├── load_app(spec) <-- 3b
    │   │   └── importlib.import_module() <-- generate_openapi.py:37
    │   │       └── app.api_v2 module loaded
    │   │           └── FastAPI() instantiation <-- 3c
    │   │               └── Router registration loop <-- 3d
    │   │                   └── app.include_router() <-- api_v2.py:325
    │   ├── render_openapi(app) <-- generate_openapi.py:108
    │   │   └── app.openapi() call <-- 3e
    │   │       └── generates OpenAPI schema dict
    │   └── check_openapi(path, content) <-- generate_openapi.py:111
    │       └── existing != content check <-- 3f
    │           ├── True → CI fails <-- generate_openapi.py:69
    │           └── False → CI passes <-- generate_openapi.py:71
```

**Location ID: 3a**
**Title:** CI OpenAPI Contract Check
**Description:** GitHub Actions step that validates generated schema matches committed version
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/openapi-contract.yml:74

**Location ID: 3b**
**Title:** FastAPI App Module Import
**Description:** Dynamically imports app.api_v2 module to access FastAPI application
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/generate_openapi.py:37

**Location ID: 3c**
**Title:** FastAPI Application Instantiation
**Description:** Creates FastAPI app with title, version, and OpenAPI tags configuration
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:207

**Location ID: 3d**
**Title:** Router Registration Loop
**Description:** Iterates through API prefixes and registers all routers to FastAPI app
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:323

**Location ID: 3e**
**Title:** OpenAPI Schema Extraction
**Description:** Calls FastAPI's openapi() method to generate complete OpenAPI specification
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/generate_openapi.py:48

**Location ID: 3f**
**Title:** Schema Drift Detection
**Description:** Compares generated schema with committed version to detect drift
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/generate_openapi.py:63

### AI Guide: OpenAPI Schema Generation and CI Validation

**Motivation:**
OpenAPI schema generation provides complete API contract documentation for consumers and tools. Dynamic app loading enables schema extraction without import side effects. CI validation prevents API changes without documentation updates. Deterministic JSON rendering ensures stable diffs. This system transforms API definitions from code to documented contracts. The GitHub Actions openapi-contract job validates schema consistency. The generate_openapi.py script dynamically imports the FastAPI app and generates the OpenAPI schema. Schema drift detection compares generated schema with committed version. This system ensures documentation stays synchronized with implementation.

**Details:**

**CI Integration and Schema Validation**
GitHub Actions openapi-contract job validates schema consistency [3a]. Runs generate_openapi.py --check to compare generated vs committed schema. CI failure blocks merge when schema drift is detected. This integration ensures documentation stays synchronized with implementation. The CI-based validation prevents API changes without corresponding documentation updates, ensuring that the API contract is always accurate and up-to-date.

**Dynamic App Loading and Safe Schema Extraction**
load_app() uses importlib.import_module() to dynamically import app.api_v2 module [3b]. Prevents import side effects during schema generation. Retrieves FastAPI app instance for introspection. This approach enables safe schema extraction without triggering application initialization side effects, ensuring that schema generation is isolated from application runtime behavior.

**Schema Extraction Process and Comprehensive Contract Generation**
FastAPI app instantiation configures title, version, and OpenAPI tags [3c]. Router registration loop adds all routers to app [3d]. app.openapi() call generates complete OpenAPI specification [3e]. This process extracts comprehensive API contract. The dynamic app construction ensures that the schema reflects the complete API surface, including all registered routers and endpoints.

**Drift Detection and Deterministic Rendering**
check_openapi() compares generated schema with committed version [3f]. Mismatch triggers CI failure with descriptive error message. This validation prevents API changes without corresponding documentation updates. Deterministic JSON rendering ensures stable diffs. The deterministic rendering ensures that schema changes are only detected when the actual API contract changes, preventing false positives due to formatting differences.

## Trace ID: 4
**Title:** API Response Envelope Wrapping Flow

**Description:** EnvelopedRoute system that automatically wraps API responses in canonical V2 envelope structure

**Trace text diagram:**
```
API Response Envelope Wrapping Flow
├── Router Definition
│   └── APIRouter(route_class=EnvelopedRoute) <-- 4a
│
├── Request Handling Pipeline
│   ├── EnvelopedRoute.get_route_handler() <-- envelope_route.py:75
│   │   └── enveloped_handler() wrapper <-- 4b
│   │       ├── await original_handler(request) <-- 4c
│   │       ├── Check if JSONResponse <-- envelope_route.py:81
│   │       ├── Parse response body <-- envelope_route.py:85
│   │       ├── _is_already_enveloped() check <-- 4d
│   │       ├── Extract request_id from state <-- envelope_route.py:92
│   │       └── _wrap() call <-- 4e
│   │           └── Build envelope dict with: <-- envelope_route.py:57
│   │               ├── "data": body <-- envelope_route.py:58
│   │               ├── "error": None <-- envelope_route.py:59
│   │               └── "meta": {...} <-- envelope_route.py:60
│   └── Return JSONResponse with wrapped content <-- envelope_route.py:101
│
└── Envelope Model Definition
    └── ApiEnvelope[DataT] Pydantic model <-- 4f
        ├── data: DataT | None <-- api_v2_models.py:63
        ├── error: ApiError | None <-- api_v2_models.py:64
        └── meta: ApiMeta <-- api_v2_models.py:65
```

**Location ID: 4a**
**Title:** Router with EnvelopedRoute Class
**Description:** Creates APIRouter with custom route_class that wraps responses in envelopes
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/auth.py:71

**Location ID: 4b**
**Title:** Enveloped Handler Wrapper
**Description:** Custom route handler that intercepts responses to wrap them in envelopes
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/envelope_route.py:78

**Location ID: 4c**
**Title:** Original Handler Execution
**Description:** Calls the original endpoint handler to get the response
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/envelope_route.py:79

**Location ID: 4d**
**Title:** Envelope Detection Check
**Description:** Checks if response is already wrapped to avoid double-wrapping
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/envelope_route.py:89

**Location ID: 4e**
**Title:** Envelope Wrapping Call
**Description:** Wraps bare response body in canonical ApiEnvelope structure
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/envelope_route.py:100

**Location ID: 4f**
**Title:** ApiEnvelope Model Definition
**Description:** Pydantic model defining canonical V2 response envelope structure
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:56

### AI Guide: API Response Envelope Wrapping Flow

**Motivation:**
Response envelope system provides canonical structure for all API responses. EnvelopedRoute automatically wraps responses without manual intervention. Double-wrapping prevention preserves already formatted responses. Request ID tracking enables request correlation. This system transforms raw responses into consistent, trackable API contracts. APIRouter instances use route_class=EnvelopedRoute for automatic response wrapping. The enveloped_handler wrapper intercepts responses. Double-wrapping prevention checks preserve already formatted responses. Request ID extraction enables correlation tracking. The _wrap() function builds canonical envelope structure. This system ensures consistent response format across all endpoints.

**Details:**

**Router Configuration and Automatic Enforcement**
APIRouter instances use route_class=EnvelopedRoute for automatic response wrapping [4a]. This configuration applies envelope wrapping to all routes in the router. No manual wrapping required in endpoint handlers. Automatic enforcement ensures consistent response format. The configuration-based approach ensures that all responses are wrapped consistently without requiring manual intervention in each endpoint handler.

**Request Processing Pipeline and Transparent Transformation**
EnvelopedRoute.get_route_handler() returns enveloped_handler wrapper [4b]. Original handler executes to generate response [4c]. Response type checking ensures only JSON responses are wrapped [4d]. This pipeline provides transparent response transformation. The transparent transformation ensures that endpoint handlers can return raw responses without worrying about envelope formatting, while the system automatically applies the canonical structure.

**Envelope Construction and Double-Wrapping Prevention**
_is_already_enveloped() check prevents double-wrapping responses [4d]. Request ID extraction from request state enables correlation tracking [4e]. _wrap() function builds canonical envelope with data, error, and meta fields [4e]. This construction ensures consistent response structure. The double-wrapping prevention ensures that responses that are already in envelope format are not wrapped again, preserving the integrity of pre-formatted responses.

**Model Definition and Type Safety**
ApiEnvelope[DataT] Pydantic model defines envelope structure with generic data type [4f]. data field holds response payload, error field holds error information, meta field holds metadata. Type safety ensures envelope integrity. The generic type parameter enables type-safe envelope construction for different response types, ensuring that the envelope structure is validated at compile time.

## Trace ID: 5
**Title:** Error Response Envelope Generation

**Description:** Exception handling system that converts raised exceptions into canonical V2 error envelopes

**Trace text diagram:**
```
Error Response Envelope Generation Pipeline
├── FastAPI App Initialization
│   └── register_exception_handlers(app) <-- 5a
│       └── Registers global handlers for all exceptions
│
├── Domain Exception Hierarchy
│   ├── EduBoostError base class <-- 5b
│   │   ├── status_code: int = 500 <-- exceptions.py:26
│   │   ├── error_code: str = "internal_error" <-- exceptions.py:27
│   │   └── __init__(message, details) <-- exceptions.py:29
│   └── NotFoundError subclass <-- 5c
│       ├── status_code = 404 <-- exceptions.py:36
│       └── error_code = "not_found" <-- exceptions.py:37
│
└── Envelope Construction
    ├── ApiError model <-- 5e
    │   ├── code: str <-- api_v2_models.py:38
    │   ├── message: str <-- api_v2_models.py:39
    │   ├── field_errors: list[FieldError] <-- api_v2_models.py:40
    │   └── remediation: str | None <-- api_v2_models.py:41
    └── fail() helper function <-- 5d
        └── Returns ApiErrorEnvelope <-- api_v2_models.py:109
            ├── data: None <-- api_v2_models.py:77
            ├── error: ApiError <-- api_v2_models.py:78
            └── meta: ApiMeta <-- api_v2_models.py:65
```

**Location ID: 5a**
**Title:** Exception Handlers Registration
**Description:** Registers global exception handlers for FastAPI application
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:219

**Location ID: 5b**
**Title:** Base Domain Exception Class
**Description:** Base exception class for all EduBoost domain errors with status_code and error_code
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:23

**Location ID: 5c**
**Title:** NotFoundError Exception Definition
**Description:** Specific exception type with 404 status code and not_found error code
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:35

**Location ID: 5d**
**Title:** Error Envelope Builder Function
**Description:** Helper function that constructs canonical error envelope with ApiError payload
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:95

**Location ID: 5e**
**Title:** ApiError Model Definition
**Description:** Pydantic model defining canonical V2 error payload structure
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:35

### AI Guide: Error Response Envelope Generation

**Motivation:**
Error response envelope system provides consistent error handling across all API endpoints. Global exception handlers automatically convert exceptions to canonical format. Domain exception hierarchy enables structured error classification. fail() helper function simplifies error envelope creation. This system transforms unstructured exceptions into consistent, actionable error responses. The register_exception_handlers(app) function registers global handlers for all exception types. EduBoostError base class defines structure for domain exceptions. NotFoundError subclass provides specific error handling. ApiError model defines canonical error payload. fail() helper function simplifies error envelope creation. This system ensures consistent error format across all endpoints.

**Details:**

**Global Exception Handling and Centralized Error Conversion**
register_exception_handlers(app) registers global handlers for all exception types [5a]. Handlers catch exceptions and convert them to error envelopes. This ensures consistent error format across all endpoints without individual handler code. The centralized exception handling ensures that all errors are converted to the canonical format, preventing inconsistent error responses across different endpoints.

**Domain Exception Hierarchy and Structured Classification**
EduBoostError base class defines structure for all domain exceptions [5b]. Includes status_code and error_code fields for HTTP mapping. NotFoundError subclass provides specific 404 error handling [5c]. This hierarchy enables structured error classification. The hierarchical exception structure enables type-specific error handling while maintaining a consistent base structure for all errors.

**Error Envelope Construction and Simplified Creation**
ApiError model defines canonical error payload structure [5e]. Includes code, message, field_errors, and remediation fields. fail() helper function simplifies error envelope creation [5d]. Returns ApiErrorEnvelope with data: None and error populated. The helper function simplifies error envelope creation, reducing boilerplate code and ensuring consistent error envelope structure across the codebase.

**Consistent Error Format and Consumer Experience**
All errors follow same envelope structure as successful responses. Error codes provide machine-readable error identification. Messages provide human-readable error descriptions. Remediation offers guidance for error resolution. This consistency enables reliable error handling by API consumers. The consistent error format enables API consumers to implement uniform error handling logic, reducing integration complexity and improving reliability.

## Trace ID: 6
**Title:** FastAPI Router Registration and Mounting

**Description:** Application startup flow that imports and registers all V2 routers under multiple API prefixes

**Trace text diagram:**
```
FastAPI Application Startup & Router Registration
├── app/api_v2.py module initialization
│   ├── Import router modules <-- 6a
│   │   ├── from app.api_v2_routers import auth <-- api_v2.py:240
│   │   ├── from app.api_v2_routers import learners <-- api_v2.py:252
│   │   └── [other routers...]
│   ├── Define API prefix constants <-- 6b
│   │   ├── API_V2 = "/api/v2" <-- api_v2.py:262
│   │   └── API_PREFIXES = (API_V2, "/v2") <-- api_v2.py:263
│   ├── Build ROUTER_REGISTRY tuple <-- 6c
│   │   ├── ("auth", auth.router) <-- api_v2.py:266
│   │   ├── ("learners", learners.router) <-- api_v2.py:269
│   │   └── [other router entries...]
│   └── Router registration loop
│       └── for prefix in API_PREFIXES: <-- api_v2.py:323
│           └── for router in ROUTER_REGISTRY: <-- api_v2.py:324
│               └── app.include_router() <-- 6d
│
└── app/api_v2_routers/learners.py
    └── router = APIRouter() <-- 6e
        ├── route_class=EnvelopedRoute
        ├── prefix="/learners"
        └── tags=["learners"]
```

**Location ID: 6a**
**Title:** Router Module Imports
**Description:** Imports all router modules from api_v2_routers package
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:239

**Location ID: 6b**
**Title:** API Prefix Constants
**Description:** Defines primary and alternate API path prefixes for V2 endpoints
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:262

**Location ID: 6c**
**Title:** Router Registry Tuple
**Description:** Defines ordered tuple of all routers to be registered with the app
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:264

**Location ID: 6d**
**Title:** Router Inclusion Call
**Description:** Registers each router with FastAPI app under both /api/v2 and /v2 prefixes
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:324

**Location ID: 6e**
**Title:** Learners Router Definition
**Description:** Creates learners router with EnvelopedRoute for automatic response wrapping
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:20

### AI Guide: FastAPI Router Registration and Mounting

**Motivation:**
Router registration system provides organized API endpoint management. Multiple API prefixes enable flexible versioning. ROUTER_REGISTRY enables centralized router management. EnvelopedRoute ensures consistent response formatting. This system transforms individual routers into cohesive API surface. The app/api_v2.py module imports all router modules. API prefix constants define primary and alternate prefixes. ROUTER_REGISTRY tuple defines ordered collection of routers. Nested loops register each router under all API prefixes. Individual routers use APIRouter with EnvelopedRoute. This system provides organized API endpoint management with flexible versioning.

**Details:**

**Router Module Import Strategy and Centralized Registration**
app/api_v2.py imports all router modules from api_v2_routers package [6a]. Centralized imports enable comprehensive router registration. Import organization supports modular router development. This strategy ensures all routers are available for registration. The centralized import strategy ensures that all routers are registered consistently, preventing missing routers due to import errors.

**API Prefix Configuration and Flexible Versioning**
API_V2 constant defines primary prefix "/api/v2" [6b]. API_PREFIXES tuple includes both "/api/v2" and "/v2" for compatibility. Multiple prefixes support different client preferences. This configuration enables flexible API versioning. The multiple prefix support enables backward compatibility and flexibility for different client integration patterns.

**Router Registry Management and Ordered Registration**
ROUTER_REGISTRY tuple defines ordered collection of all routers [6c]. Each entry includes router name and router instance. Ordered registration enables predictable route priority. Centralized registry simplifies router management. The ordered registration ensures that route priority is predictable and consistent, preventing conflicts between overlapping routes.

**Registration Process and Comprehensive Coverage**
Nested loops register each router under all API prefixes [6d]. app.include_router() handles route mounting with specified prefix. This process ensures consistent API surface across all prefixes. Comprehensive registration provides complete API coverage. The nested loop approach ensures that all routers are registered under all configured prefixes, providing a consistent API surface regardless of the prefix used.

**Router Configuration and Consistent Behavior**
Individual routers like learners.py use APIRouter with EnvelopedRoute [6e]. Route class enables automatic response wrapping. Prefix and tags provide route organization and documentation. This configuration ensures consistent router behavior. The consistent router configuration ensures that all endpoints follow the same patterns for response formatting and documentation, improving the developer experience and API consistency.
