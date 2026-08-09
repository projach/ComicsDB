import asyncpg

from .models import UserOut


async def create_user(db: asyncpg.Pool, username: str, hashed_password: str) -> UserOut:
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO users (username, hashed_password) VALUES ($1, $2) RETURNING id, username",
            username, hashed_password
        )
        return UserOut(id=row["id"], username=row["username"])