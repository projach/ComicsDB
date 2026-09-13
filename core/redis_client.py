import redis.asyncio as Redis
import os


REDIS_URL = os.getenv("REDIS_URL")

redis_client = Redis.from_url(
    url=REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2
)

def get_redis() -> Redis:
    return redis_client