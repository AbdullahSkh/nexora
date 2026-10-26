"""Redis client configuration and connectivity check."""

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def check_redis_connection() -> bool:
    """Verify Redis connectivity. Returns True if reachable."""
    try:
        await redis_client.ping()
        return True
    except Exception as exc:  # noqa: BLE001 - startup diagnostic
        logger.error("Redis connection check failed: %s", exc)
        return False


async def close_redis() -> None:
    """Close the Redis client on shutdown."""
    await redis_client.close()