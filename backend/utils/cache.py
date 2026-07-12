import json

try:
    import redis.asyncio as redis
except Exception:  # redis not installed / unavailable
    redis = None

from config import settings

_redis = None


async def init_redis():
    """Connect to Redis if available. Silently no-op if it isn't —
    the app must run without a cache."""
    global _redis
    if redis is None:
        return
    try:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        await _redis.ping()
    except Exception:
        _redis = None


async def get_cache(key: str):
    if not _redis:
        return None
    try:
        val = await _redis.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


async def set_cache(key: str, value, ttl: int = 300):
    if not _redis:
        return
    try:
        await _redis.setex(key, ttl, json.dumps(value))
    except Exception:
        pass
