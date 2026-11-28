import json
import secrets

import redis.asyncio as Redis

from .exceptions import (
    CooldownException,
    EmailPendingException,
    PendingSignupNotFoundException,
    UsernamePendingException,
)

AUTH_CODE_LIFE_SECONDS = 600
RESEND_CODE_TIMOUT_SECONDS = 60

async def create_pending_signup(
    email: str, username: str, hashed_password: str, redis_client: Redis
) -> str:
    username_key = f"pending_username:{username.lower()}"
    signup_key = f"pending_signup:{email}"

    if not await redis_client.set(username_key, email, nx=True, ex=AUTH_CODE_LIFE_SECONDS):
        raise UsernamePendingException()

    code = f"{secrets.randbelow(1000000):06d}"

    created = await redis_client.set(
        signup_key,
        json.dumps({"username": username, "hashed_password": hashed_password, "email": email, "code": code}),
        nx=True,
        ex=AUTH_CODE_LIFE_SECONDS,
    )

    if not created:
        await redis_client.delete(username_key)
        raise EmailPendingException()

    return code


async def get_pending_signup(email: str, redis_client: Redis) -> dict | None:
    raw = await redis_client.get(f"pending_signup:{email}")
    return json.loads(raw) if raw else None


async def delete_pending_signup(email: str, redis_client: Redis):
    await redis_client.delete(f"pending_signup:{email}")


async def resend_pending_signup_code(email: str, redis_client: Redis) -> tuple[str, int]:
    cooldown_key = f"resend_cooldown:{email}"

    if await redis_client.exists(cooldown_key):
        ttl = await redis_client.ttl(cooldown_key)
        raise CooldownException(seconds_remaining=ttl)

    pending = await get_pending_signup(email=email, redis_client=redis_client)
    if pending is None:
        raise PendingSignupNotFoundException()

    code = f"{secrets.randbelow(1000000):06d}"
    pending["code"] = code

    await redis_client.set(
        f"pending_signup:{email}",
        json.dumps(pending),
        ex=AUTH_CODE_LIFE_SECONDS,
    )
    await redis_client.set(cooldown_key, "1", ex=RESEND_CODE_TIMOUT_SECONDS)

    return code, RESEND_CODE_TIMOUT_SECONDS
