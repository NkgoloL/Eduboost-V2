# UI Rules

**Last updated:** 2026-06-09
**Current state tracked in:** RoadMap.md Phase 13, TODO.md GAP-3

Design and styling guidelines for EduBoost learner UI, parent portal, and admin interface.

## Design Principles

1. Learner-first: Large text, clear colors, minimal distractions for ages 5-13
2. Accessibility: WCAG AA compliance -- readable fonts, high contrast, keyboard navigation
3. Mobile-responsive: Works on tablets and phones (primary platform)
4. Inclusive: Support dyslexia-friendly fonts, multiple languages, high-contrast mode
5. Parent-friendly: Clear, no jargon, actionable insights only
6. Admin-efficient: Fast, bulk actions, keyboard shortcuts, real-time feedback

## Typography

- Learner UI: 32px headings, 16px body, 14px secondary, 12px small text
- Parent Portal: 24px headings, 14px body, 12px secondary
- Admin: 20px headings, 13px body, 12px small text
- Support Poppins font + OpenDyslexic option

## Colors

Primary: #7C5CFC (purple)
Success: #10B981 (green)
Warning: #F59E0B (orange)
Danger: #EF4444 (red)
Gray scale: #F9FAFB to #101828

## Layout

- Learner UI: Max 1200px, 16-24px padding
- Parent Portal: Max 1400px, 20px padding
- Admin: 100% width, 280px sidebar, 20px padding

## Components

- Cards: White bg, 1px gray border, 12px radius, 20px padding
- Buttons: 8px radius, 10px/18px padding, 14px/600wt text
- Inputs: 8px radius, 2px gray border, 10-12px padding
- Progress bars: 6px height, 9999px radius
- Badges: 4px/10px padding, 12px/600wt, 9999px radius

## Mastery Heatmap

Grid 4x2, 80x80px cells:
- Mastered (80-100%): Green
- In Progress (30-79%): Orange
- Not Started (under 30%): Gray

## Buttons

Primary: Purple bg, white text
Secondary: White bg, purple border, purple text
Danger: Red bg, white text
Disabled: Gray bg, gray text

## Accessibility

- Color contrast: 4.5:1 for normal, 3:1 for large text (over 18px)
- Focus indicators on all interactive elements
- Keyboard navigation in logical order
- All images have alt text
- All inputs have associated labels
- Status: Claimed but not verified (Phase 13.4 will audit)

## Mobile

- Breakpoints: under 640px (mobile), 640-1024px (tablet), over 1024px (desktop)
- Touch targets: min 44x44px, buttons 48x48px
- Single column, full-width cards, bottom tab bar

## Do Nots

- No hard-coded hex colors outside CSS variables
- No more than 2 levels of card shadows
- No more than 3 font sizes per page
- No auto-play audio/video without consent
- No scroll required on modals (content fits viewport)
- Never show raw error messages to learners
- Never disable inputs without explanation

## Verification and Tracking

The UI rules are design-time guidance. Implementation tracking:
- ui-registry.md: component inventory with build status
- RoadMap.md Phase 3: frontend build health
- RoadMap.md Phase 13: frontend and product completeness
- TODO.md GAP-3: frontend verification tasks
- RoadMap.md Phase 16: beta feedback loop for design iteration

After beta, capture real learner/parent UX feedback and update these rules accordingly.
