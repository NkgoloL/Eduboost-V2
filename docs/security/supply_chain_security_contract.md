# Supply Chain Security Contract

## Purpose

This contract defines supply-chain security controls.

## Required Supply-Chain Controls

- dependency lockfile is required
- SBOM is required
- artifact provenance is required
- dependency review is required
- license review is required
- signed artifact or digest pinning is required
- container image vulnerability scan is required
- transitive dependency risk is reviewed
- release artifact checksum is retained

## Boundary

This contract records supply-chain readiness. It does not sign artifacts or run dependency scanners.
