import redis.asyncio as redis
from typing import Optional
from .settings import settings

# Global redis client
redis_client: Optional[redis.Redis] = None


async def init_redis() -> redis.Redis:
    """Initialize Redis connection."""
    global redis_client
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis() -> redis.Redis:
    """Dependency to get Redis client."""
    if redis_client is None:
        await init_redis()
    return redis_client
