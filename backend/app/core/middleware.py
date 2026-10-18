import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.app.core.config import settings

logger = logging.getLogger("astromind.security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforce defense-in-depth HTTP security response headers."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Baseline Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"

        # Content Security Policy (strict API default)
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"

        # Strict Transport Security (enforce HTTPS in production)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        return response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Inject unique request_id, monitor execution latency, and validate payload size."""

    async def dispatch(self, request: Request, call_next):
        # 1. Traceability: ensure every request has a unique request_id
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # 2. Body size safety check
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.MAX_REQUEST_BODY_BYTES:
            logger.warning(
                f"Payload Too Large: {content_length} bytes exceeds limit {settings.MAX_REQUEST_BODY_BYTES}",
                extra={"request_id": request_id},
            )
            return JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": (
                            f"Request body exceeds maximum allowed size of {settings.MAX_REQUEST_BODY_BYTES} bytes."
                        ),
                        "request_id": request_id,
                    }
                },
                headers={"X-Request-ID": request_id},
            )

        start_time = time.perf_counter()
        try:
            response: Response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            # Redact stack trace from client response; log securely server-side
            logger.error(
                f"Unhandled exception during request: {exc}",
                exc_info=True,
                extra={"request_id": request_id},
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": ("An unexpected server error occurred. Please reference the request ID."),
                        "request_id": request_id,
                    }
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time": f"{duration_ms:.2f}ms",
                },
            )
