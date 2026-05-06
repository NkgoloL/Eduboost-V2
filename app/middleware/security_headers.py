from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Prevent browsers from performing MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent the page from being rendered in an iframe (Clickjacking protection)
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection in older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict-Transport-Security (HSTS) - enforce HTTPS
        # Only set if the request is over HTTPS or if in production
        # For now, we'll set it with a reasonable max-age
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content-Security-Policy (CSP)
        # This is a basic policy that can be refined based on frontend needs
        # We allow self, and perhaps some trusted CDNs for fonts/images if needed
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; " # refined as needed
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
