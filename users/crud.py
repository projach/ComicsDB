import asyncpg

from .models import UserOut


async def create_user(db: asyncpg.Pool, username: str, hashed_password: str, email: str) -> UserOut:
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO users (username, hashed_password, email) VALUES ($1, $2, $3) RETURNING id, username, email",
            username, hashed_password, email
        )
        return UserOut(id=row["id"], username=row["username"], email=row["email"])


async def get_user_by_username(db: asyncpg.Pool, username: str):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, username, hashed_password FROM users WHERE username = $1",
            username
        )
        return row