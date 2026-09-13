import os
from contextlib import asynccontextmanager

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from .logging import logger

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def run_migrations(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        conn: asyncpg.Connection
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations(
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT now()
            )
        """)
        applied = {row["version"] for row in await conn.fetch("SELECT version FROM schema_migrations")}
        migrations_dir = "migrations"
        for filename in sorted(os.listdir(migrations_dir)):
            if filename in applied:
                continue
            with open(os.path.join(migrations_dir, filename)) as f:
                sql = f.read()
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute("INSERT INTO schema_migrations (version) VALUES ($1)", filename)
            logger.debug(f"Applied migration: {filename}")
            
            
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await asyncpg.create_pool(DATABASE_URL)

    await run_migrations(app.state.db)

    yield

    await app.state.db.close()


async def get_db(request: Request):
    return request.app.state.db
