# PR-CF-013 — Full outstanding content generation runner

## Status

Completed.

## Summary

Adds overnight-safe batch generation that fills all configured Content Factory gaps across all scopes and layers without promoting anything to production or bypassing review.

## Changes

### Backend

- Extended `ContentGenerationPlanner` to support all layers (diagnostic_items, lessons, assessment_blueprints, study_plan_templates)
- Added `BlueprintGenerator` for assessment blueprint generation
- Added `StudyPlanTemplateGenerator` for study-plan template generation
- Extended provider abstraction with `generate_assessment_blueprints` and `generate_study_plan_templates` methods
- Added `ContentGenerationRunLock` for preventing concurrent full runs
- Added `ContentGenerationReporter` for writing generation reports
- Added `run_full_generation.py` CLI script for overnight-safe batch generation
- Added admin API routes for full generation planning, starting, listing, canceling, and resuming

### Frontend

- Added TypeScript API functions for full generation endpoints
- Added `FullGenerationPanel` component for admin controls
- Integrated panel into Content Factory Live Dashboard

### Documentation

- Added full generation runner documentation

## Safety Guarantees

- No learner-visible content is generated or promoted
- No production promotion occurs
- No automatic approval
- Staging preview never exposes learner content
- Lock prevents concurrent full runs
- Budget and artifact caps prevent runaway generation
- Resumable execution handles interruptions

## Verification

- Python compilation passed
- Unit tests passed
- API tests passed
- OpenAPI check passed
- Frontend type-check passed
- Safety greps passed
