# Security Headers Policy

## Required Headers

- Strict-Transport-Security
- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy

## Required Rules

- HSTS is required for production
- Content-Security-Policy is required for production
- X-Content-Type-Options must use nosniff
- X-Frame-Options must prevent clickjacking
- Referrer-Policy must minimize leakage

## Boundary

This policy records security header expectations. It does not configure the runtime server.
