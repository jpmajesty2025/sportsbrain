import redis
import os
from app.core.config import settings

# Get Redis URL from environment first (Railway REDIS_PUBLIC_URL), then settings
redis_url = os.getenv("REDIS_PUBLIC_URL") or os.getenv("REDIS_URL") or settings.REDIS_URL
redis_client = redis.from_url(redis_url, decode_responses=True)

def get_redis():
    return redis_client