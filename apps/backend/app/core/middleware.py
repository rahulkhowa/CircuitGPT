import logging
import time

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import redis_client


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log execution time and status details of all incoming requests
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        method = request.method
        url = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        logger = logging.getLogger("request_logger")

        try:
            response = await call_next(request)
            process_time_ms = (time.time() - start_time) * 1000

            logger.info(
                f"HTTP {method} {url} - {response.status_code} - {process_time_ms:.2f}ms",
                extra={
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "process_time_ms": process_time_ms,
                    "client_ip": client_ip,
                }
            )
            response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
            return response
        except Exception as e:
            process_time_ms = (time.time() - start_time) * 1000
            logger.error(
                f"HTTP {method} {url} - FAILED - {process_time_ms:.2f}ms - {str(e)}",
                exc_info=True,
                extra={
                    "method": method,
                    "url": url,
                    "status_code": 500,
                    "process_time_ms": process_time_ms,
                    "client_ip": client_ip,
                    "error": str(e),
                }
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error occurred."}
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-backed rate limiting middleware (IP based) with fail-open fallback
    """
    def __init__(self, app, limit: int = 150, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        # Bypassing endpoints like health checks, docs, or landing requests
        if request.url.path in ["/api/v1/health", "/", "/api/v1/docs", "/api/v1/openapi.json"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        redis_key = f"rate_limit:{client_ip}"

        try:
            current_requests = await redis_client.get(redis_key)

            if current_requests and int(current_requests) >= self.limit:
                logging.getLogger("rate_limiter").warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Too many requests. Please try again later."}
                )

            # Use redis pipeline to increment and set expiration
            async with redis_client.pipeline() as pipe:
                await pipe.incr(redis_key)
                if not current_requests:
                    await pipe.expire(redis_key, self.window)
                await pipe.execute()

        except Exception as e:
            # Fail-open: log warning but let the request proceed if Redis is unreachable
            logging.getLogger("rate_limiter").warning(
                f"Redis connection failed in rate limiter: {str(e)}. Permitting request (fail-open)."
            )

        return await call_next(request)
