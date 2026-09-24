import json
import logging
from typing import Any, Optional
from app.core.database import redis_client

logger = logging.getLogger(__name__)


class CacheService:
    """
    Asynchronous Redis Cache Service for fast in-memory caching and session acceleration.
    Handles JSON serialization, key expiration, and pattern-based cache invalidation.
    """

    def __init__(self, client=None) -> None:
        self._client = client or redis_client

    async def get(self, key: str) -> Optional[str]:
        """Retrieve raw string value by key."""
        try:
            return await self._client.get(key)
        except Exception as exc:
            logger.warning(f"[CacheService] get error for key '{key}': {exc}")
            return None

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Store string value with optional TTL in seconds."""
        try:
            if expire:
                await self._client.setex(key, expire, value)
            else:
                await self._client.set(key, value)
            return True
        except Exception as exc:
            logger.warning(f"[CacheService] set error for key '{key}': {exc}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """Retrieve and deserialize JSON object by key."""
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception as exc:
            logger.warning(f"[CacheService] JSON decode error for key '{key}': {exc}")
            return None

    async def set_json(self, key: str, value: Any, expire: Optional[int] = 300) -> bool:
        """Serialize and store JSON object with default 5-minute TTL."""
        try:
            serialized = json.dumps(value)
            return await self.set(key, serialized, expire=expire)
        except Exception as exc:
            logger.warning(f"[CacheService] JSON encode error for key '{key}': {exc}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete specific key."""
        try:
            await self._client.delete(key)
            return True
        except Exception as exc:
            logger.warning(f"[CacheService] delete error for key '{key}': {exc}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern (e.g. 'cache:search:*')."""
        try:
            keys = []
            async for k in self._client.scan_iter(match=pattern):
                keys.append(k)
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as exc:
            logger.warning(f"[CacheService] delete_pattern error for '{pattern}': {exc}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(await self._client.exists(key))
        except Exception as exc:
            logger.warning(f"[CacheService] exists error for key '{key}': {exc}")
            return False


cache_service = CacheService()
