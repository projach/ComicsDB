import os
from contextlib import asynccontextmanager

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, Request

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await asyncpg.create_pool(DATABASE_URL)

    async with app.state.db.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS comics(
                id SERIAL PRIMARY KEY,
                issue INTEGER NOT NULL,
                name TEXT NOT NULL,
                publisher TEXT NOT NULL,
                writer TEXT NOT NULL,
                UNIQUE(issue, name, publisher, writer)
            )
        """)

    yield

    await app.state.db.close()

async def get_db(request: Request):
    return request.app.state.db