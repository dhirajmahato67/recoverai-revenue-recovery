"""Custom middleware for request correlation, HTTP logging, and security headers."""

import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger, request_id_ctx

logger = get_logger("app.http")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Ensures every incoming request has an X-Request-ID header and context variable."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        incoming_req_id = request.headers.get("X-Request-ID")
        # Validate format or generate new UUID4
        request_id = incoming_req_id if incoming_req_id and len(incoming_req_id) <= 64 else str(uuid.uuid4())

        # Set context variable for this async task
        token = request_id_ctx.set(request_id)
        # Store in request state for easy access in handlers
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)


class HttpLoggingMiddleware(BaseHTTPMiddleware):
    """Logs incoming HTTP requests, response status codes, and latency."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        # Suppress noisy health checks from debug logging if desired
        is_health_check = path.endswith("/health/live")

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if not is_health_check:
                logger.info(
                    f"{method} {path} {response.status_code} - {duration_ms}ms",
                    extra={
                        "extra_data": {
                            "method": method,
                            "path": path,
                            "status_code": response.status_code,
                            "duration_ms": duration_ms,
                        }
                    },
                )
            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"{method} {path} FAILED ({exc.__class__.__name__}) - {duration_ms}ms",
                extra={
                    "extra_data": {
                        "method": method,
                        "path": path,
                        "duration_ms": duration_ms,
                        "error": str(exc),
                    }
                },
                exc_info=True,
            )
            raise exc


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Applies standard HTTP security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
