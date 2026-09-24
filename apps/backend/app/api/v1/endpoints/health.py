from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_redis

router = APIRouter()

@router.get("")
async def check_health(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Health check endpoint that probes connections to PostgreSQL and Redis.
    Returns detailed connectivity reports for orchestration checks.
    """
    postgres_health = "connected"
    redis_health = "connected"
    overall_status = "ok"

    # 1. Test PostgreSQL connection
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        postgres_health = f"disconnected: {str(e)}"
        overall_status = "degraded"

    # 2. Test Redis connection
    try:
        await redis.ping()
    except Exception as e:
        redis_health = f"disconnected: {str(e)}"
        overall_status = "degraded"

    # Return standard response
    return {
        "status": overall_status,
        "postgres": postgres_health,
        "redis": redis_health
    }
