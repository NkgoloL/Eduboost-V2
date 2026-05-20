# No False-Closure Status After DEPLOY-FE-RUNTIME-001R / code_2471_2510R

**Status:** nginx certificate path repair added.

## Proven

- `nginx/nginx.conf` certificate directives are aligned to `/etc/letsencrypt/live/<domain>/`.
- The repair preserves the existing `server_name` domain when available.
- The production frontend runtime static blocker for nginx certificate paths is removed.

## Not claimed

- Certificates exist.
- Certbot issued certificates.
- Nginx loaded the certificates successfully.
- TLS works in staging or production.
- Beta release is approved.
