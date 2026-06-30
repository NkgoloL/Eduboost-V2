# UI Registry

**Last updated:** 2026-06-09
**Implementation tracked in:** RoadMap.md Phase 3 (build health), Phase 13 (completeness)
**Component status:** Most shared components implemented; feature components in progress

Component inventory for EduBoost learner UI, parent portal, and admin interface.

## Learner UI Components

### Navigation & Layout
- Navbar | Top navigation | Implemented (Phase 2)
- Sidebar | Mobile bottom navigation | Implemented (Phase 2)
- Layout | Main page wrapper | Implemented (Phase 2)

### Auth
- LoginForm | Email/password login | Implemented
- RegisterForm | Learner registration | Implemented

### Ether Onboarding
- EtherQuestion | Single question card | Implemented
- EtherStepper | Progress through questions | Implemented
- EtherResults | Display learner archetype | Implemented

### Diagnostic Assessment
- DiagnosticSession | Main diagnostic UI | Implemented
- ItemRenderer | Render single item | Implemented
- ResponseForm | Input for answer | Implemented
- SessionProgress | Progress bar | Implemented

### Practice Sessions
- PracticeSession | Main practice UI | Implemented
- PracticeItem | Single practice item | Implemented
- PracticeResult | Feedback on response | Implemented
- SessionStats | Points, streak display | Implemented

### Study Plan
- StudyPlanView | Display current plan | Implemented
- TopicCard | Topic in study plan | Implemented
- LearnButton | Link to lesson | Implemented

### Gamification
- StreakCounter | Display current streak | Implemented
- BadgesDisplay | Show earned badges | Implemented
- PointsCounter | Show earned points | Implemented
- Leaderboard | Global leaderboard | Implemented (unauthenticated, Phase 2)

## Parent Portal Components

- ParentNavbar | Top navigation | Implemented
- ParentLogin | Parent authentication | Implemented
- ParentDashboard | Overview of children | Implemented
- ChildCard | Child profile + stats | Implemented
- MasteryHeatmap | CAPS topics grid | Implemented
- ProgressChart | Mastery over time | Implemented
- InsightsPanel | Actionable recommendations | Implemented

## Admin Components

- AdminSidebar | Left navigation | Implemented
- FileUpload | Upload content | Implemented
- ETLStatus | Pipeline status | Implemented
- ReviewQueue | Pending items | Implemented
- ItemReviewForm | Review checklist | Implemented
- CoverageVerification | Coverage checker | Implemented
- PromotionForm | Staging to Production | Implemented
- AuditLog | Searchable audit log | Implemented
- ConsentStatus | Learner consent view | Implemented

## Shared Components

- Button | Primary, secondary, danger | Implemented
- Input | Text, number, date inputs | Implemented
- Card | Container with shadow | Implemented
- Modal | Overlay dialog | Implemented
- Badge | Status/tag label | Implemented
- Alert | Information, warning, error | Implemented
- Table | Data table with sorting | Implemented
- Pagination | Prev/next, page jump | Implemented
- Dropdown | Select from options | Implemented
- Checkbox | Boolean input | Implemented
- ProgressBar | Visual progress | Implemented
- Spinner | Loading indicator | Implemented
- Toast | Notification pop-up | Implemented
- Avatar | User profile picture | Implemented
- Icon | SVG icon wrapper | Implemented
- Skeleton | Loading placeholder | Implemented
- EmptyState | No data message | Implemented

## Status Legend

- Not started
- In progress
- Implemented (code exists)
- Tested (unit tests pass)
- E2E verified (Playwright)
- Beta validated (real learner feedback)

## Verification Status

| Check | Status | Phase |
|-------|--------|:---:|
| TypeScript compilation | FAIL (Phase 3.2) | 3 |
| Vitest unit tests | FAIL (15 suites, Phase 3.3) | 3 |
| Playwright E2E | FAIL (Phase 13.1) | 13 |
| ESLint | Warning (Phase 9) | 9 |
| pnpm install --frozen-lockfile | FAIL (Phase 3.1) | 3 |
| Accessibility audit | Not done (Phase 13.4) | 13 |
| PWA verification | Not done (Phase 13.5) | 13 |

Update this file as RoadMap phases complete. Cross-reference RoadMap.md for the authoritative execution plan.
