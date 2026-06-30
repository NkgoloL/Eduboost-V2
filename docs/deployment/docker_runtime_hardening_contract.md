# Docker Runtime Hardening Contract

## Purpose

This contract defines Docker image and runtime hardening expectations.

## Required Docker Controls

- pinned base image
- multi-stage build
- non-root user
- container healthcheck
- dependency lockfile
- vulnerability scan
- SBOM generation
- minimal runtime image
- no development secrets in image
- no test credentials in image
- explicit runtime command
- runtime role separation

## Required Image Roles

- API image
- worker image
- frontend image
- migration image
- scheduler image where applicable

## Boundary

This contract records Docker hardening readiness. It does not build, scan, publish, or deploy images.
