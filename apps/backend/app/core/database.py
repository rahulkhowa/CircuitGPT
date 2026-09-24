import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 1. Asynchronous SQLAlchemy Setup
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}
if "sqlite" not in settings.SQLALCHEMY_DATABASE_URI:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 10
    })

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    **engine_kwargs
)

# Async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Declarative Base for models
class Base(DeclarativeBase):
    pass

# 2. Asynchronous Redis Setup
redis_client = aioredis.from_url(
    settings.REDIS_URI,
    decode_responses=True,
    socket_timeout=5.0,
    retry_on_timeout=True
)
