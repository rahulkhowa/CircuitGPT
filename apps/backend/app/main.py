import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware

# 1. Initialize Structured Logging Formatting
setup_logging()

# 2. Lifecycle Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("[START] CircuitGPT FastAPI Application booting up...")
    yield
    # Cleanup connections
    from app.core.database import redis_client
    await redis_client.close()
    logging.info("[STOP] CircuitGPT FastAPI Application shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend production services for CircuitGPT - AI-powered EE workspace",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# 3. CORS Configuration
# Allowed origins can be restricted in production config settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Custom Middlewares
# (Note: Middleware executes in reverse order of registration in FastAPI)
app.add_middleware(RateLimitMiddleware, limit=150, window_seconds=60)
app.add_middleware(RequestLoggingMiddleware)

# 5. Router Registration
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root_endpoint():
    return {
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "online",
        "debug_mode": settings.DEBUG
    }
