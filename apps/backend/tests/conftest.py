from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db, get_redis
from app.main import app
from app.models import Base

# Async SQLite engine for testing
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    future=True
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

import fnmatch


class MockRedis:
    """Mock Redis client for test suite execution supporting Lua script eval, scans, and TTLs."""
    def __init__(self):
        self.store = {}
        self.ttls = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        self.store[key] = str(value)
        if ex:
            self.ttls[key] = ex
        return True

    async def delete(self, *keys: str):
        count = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                self.ttls.pop(k, None)
                count += 1
        return count

    async def ping(self):
        return True

    async def close(self):
        pass

    def pipeline(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def incr(self, key: str):
        val = int(self.store.get(key, 0)) + 1
        self.store[key] = str(val)
        return val

    async def expire(self, key: str, seconds: int):
        self.ttls[key] = seconds
        return True

    async def eval(self, script: str, numkeys: int, *keys_and_args):
        # Lua script emulation for rate limiter: INCR + EXPIRE
        if numkeys >= 1 and len(keys_and_args) >= 1:
            key = keys_and_args[0]
            expire_sec = keys_and_args[1] if len(keys_and_args) > 1 else 60
            val = int(self.store.get(key, 0)) + 1
            self.store[key] = str(val)
            if val == 1:
                self.ttls[key] = expire_sec
            return val
        return 1

    async def scan_iter(self, match: str = "*", count: int = 100):
        for key in list(self.store.keys()):
            if fnmatch.fnmatch(key, match):
                yield key

    async def keys(self, pattern: str = "*"):
        return [k for k in self.store.keys() if fnmatch.fnmatch(k, pattern)]

    async def execute(self):
        return [True]

    def clear(self):
        self.store.clear()
        self.ttls.clear()

mock_redis_client = MockRedis()


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def override_get_redis():
    yield mock_redis_client

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()
