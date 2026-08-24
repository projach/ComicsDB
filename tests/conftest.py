from dotenv import load_dotenv  # noqa: I001
load_dotenv(".env.test", override=True)

import os

import asyncpg
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from main import app

TEST_DATABASE_URL = os.getenv("DATABASE_URL")


@pytest_asyncio.fixture
async def client():
    async with LifespanManager(app), AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        yield ac

@pytest_asyncio.fixture(autouse=True)
async def clean_db(client): #we need client here to depend on for correct order
    pool = await asyncpg.create_pool(TEST_DATABASE_URL)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM comics")
        await conn.execute("DELETE FROM users")
    await pool.close()
    yield