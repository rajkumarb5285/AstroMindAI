import asyncio
import logging
import time
from collections import defaultdict
from typing import ClassVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.app.core.config import settings

logger = logging.getLogger("astromind.rate_limit")


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter with endpoint tier classification."""

    def __init__(self) -> None:
        # Maps client_key -> list of timestamp floats
        self._history: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    def get_tier_limit(self, path: str) -> tuple[str, int]:
        """Categorize request path into rate limit tier and return (tier_name, requests_per_minute)."""
        if not settings.RATE_LIMIT_ENABLED:
            return ("unlimited", 100000)

        path_lower = path.lower()
        if "/api/v1/auth" in path_lower:
            return ("auth", settings.RATE_LIMIT_AUTH_PER_MINUTE)
        elif "/reports" in path_lower and "download" not in path_lower:
            return ("reports", settings.RATE_LIMIT_REPORTS_PER_MINUTE)
        elif "/chat" in path_lower or "/interpret" in path_lower or "/messages" in path_lower:
            return ("ai", settings.RATE_LIMIT_AI_PER_MINUTE)
        elif any(k in path_lower for k in ("/charts", "/compatibility", "/transits", "/astrology")):
            return ("calculation", settings.RATE_LIMIT_CALCULATION_PER_MINUTE)
        else:
            return ("default", settings.RATE_LIMIT_DEFAULT_PER_MINUTE)

    async def check_rate_limit(self, client_key: str, path: str) -> tuple[bool, int, int, int]:
        """
        Check whether client_key is within rate limit for the given path.
        Returns: (is_allowed, limit, remaining, retry_after_seconds)
        """
        tier_name, limit = self.get_tier_limit(path)
        if tier_name == "unlimited":
            return (True, limit, limit, 0)

        now = time.time()
        window_seconds = 60.0
        cutoff = now - window_seconds
        tier_client_key = f"{tier_name}:{client_key}"

        async with self._lock:
            # Purge timestamps outside sliding window
            timestamps = [ts for ts in self._history[tier_client_key] if ts > cutoff]

            if len(timestamps) >= limit:
                # Oldest timestamp in window determines reset time
                oldest_ts = timestamps[0]
                retry_after = max(1, int(cutoff + window_seconds - oldest_ts) + 1)
                self._history[tier_client_key] = timestamps
                return (False, limit, 0, retry_after)

            timestamps.append(now)
            self._history[tier_client_key] = timestamps
            remaining = max(0, limit - len(timestamps))
            return (True, limit, remaining, 0)

    async def reset(self) -> None:
        """Clear all rate limit records (useful for testing)."""
        async with self._lock:
            self._history.clear()


rate_limiter = SlidingWindowRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforces tiered sliding window rate limiting on all incoming API requests."""

    EXEMPT_PREFIXES: ClassVar[tuple[str, ...]] = (
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/static",
        "/favicon.ico",
    )

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Health checks, root and docs are exempt from rate limiting
        if path == "/" or any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return await call_next(request)

        # Extract client identifier: prioritize auth token / user ID header if present, else client IP
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Rate limit per token/user
            client_key = auth_header.split(" ")[1][:32]
        else:
            client_ip = request.client.host if request.client else "unknown"
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
            client_key = client_ip

        is_allowed, limit, remaining, retry_after = await rate_limiter.check_rate_limit(client_key, path)

        request_id = getattr(request.state, "request_id", "unknown")

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for client {client_key} on {path} (Limit: {limit}/min)",
                extra={"request_id": request_id, "client_key": client_key, "path": path},
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Too many requests. Limit of {limit} requests per minute exceeded.",
                        "request_id": request_id,
                        "retry_after": retry_after,
                    }
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                    "Retry-After": str(retry_after),
                },
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
