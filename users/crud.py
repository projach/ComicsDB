import asyncpg

from .models import UserOut

async def create_user(db: asyncpg.Pool, username: str, hashed_password: str, email: str) -> UserOut:
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO users (username, hashed_password, email) VALUES ($1, $2, $3) RETURNING username, email",
            username, hashed_password, email
        )
        return UserOut(username=row["username"], email=row["email"])


async def get_user_by_username(db: asyncpg.Pool, username: str):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE username = $1",
            username
        )
        return row
    
async def get_user_by_email(db: asyncpg.Pool, email: str):
    async with db.acquire() as conn:
        conn: asyncpg.Connection
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email
        )
        return row