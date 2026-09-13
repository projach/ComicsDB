import secrets
import json
from datetime import datetime, timezone

import redis.asyncio as Redis
from .exceptions import CooldownException

AUTH_CODE_LIFE_SECONDS = 600
RESEND_CODE_TIMOUT_SECONDS = 100

async def create_pending_signup(email: str, username: str, hashed_password: str, redis_client: Redis) -> str:
    cooldown_key = f"resend_cooldown:{email}"
    if await redis_client.exists(cooldown_key):
        ttl = await redis_client.ttl(cooldown_key)
        raise CooldownException(seconds_remaining=ttl)
    
    code = f"{secrets.randbelow(1000000):06d}"
    await redis_client.set(
            name=f"pending_signup:{email}",
            ex=AUTH_CODE_LIFE_SECONDS,
            value=json.dumps({"username": username, "hashed_password": hashed_password, "email": email, "code": code})
        )
    
    await redis_client.set(name=cooldown_key, value = str(datetime.now(timezone.utc)), ex=RESEND_CODE_TIMOUT_SECONDS)
    
    return code

async def get_pending_signup(email: str, redis_client: Redis) -> dict | None:
    raw = await redis_client.get(f"pending_signup:{email}")
    return json.loads(raw) if raw else None

async def delete_pending_signup(email: str, redis_client: Redis):
    await redis_client.delete(f"pending_signup:{email}")