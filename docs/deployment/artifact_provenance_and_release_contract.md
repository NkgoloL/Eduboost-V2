# Artifact Provenance and Release Contract

## Purpose

This contract defines release artifact provenance expectations.

## Required Provenance Fields

- Git SHA
- image digest
- SBOM path
- build log path
- vulnerability scan path
- OpenAPI artifact path
- generated at UTC
- release owner
- environment
- promotion status

## Required Release Evidence

- build artifact is traceable to Git SHA
- image digest is immutable
- SBOM is retained
- vulnerability scan evidence is retained
- OpenAPI artifact is retained
- deployment logs are retained
- rollback evidence is retained
- manual production approval evidence is retained

## Boundary

This contract records artifact provenance and release evidence readiness. It does not create release artifacts, push images, or approve production launch.
