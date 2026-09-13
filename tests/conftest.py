from dotenv import load_dotenv  # noqa: I001
load_dotenv(".env.test", override=True)

import os
import json

import asyncpg
import fakeredis.aioredis
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from main import app

TEST_DATABASE_URL = os.getenv("DATABASE_URL")

class AuthedUser:
    def __init__(self, username, password, email, token):
        self.username = username
        self.password = password
        self.email = email
        self.token = token

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

@pytest_asyncio.fixture
def redis_client(monkeypatch):
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr("core.redis_client.redis_client", fake)
    return fake

@pytest_asyncio.fixture
async def client(redis_client):
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
    
def user_payload(**overrides):
    base = {"username": "projach", "password": "12345678", "email": "test@test.com"}
    return {**base, **overrides}

async def get_verification_code(redis_client, email: str) -> str:
    raw = await redis_client.get(f"pending_signup:{email}")
    return json.loads(raw)["code"]

async def _register_and_login(client, redis_client, username, password, email) -> AuthedUser:
    response = await client.post("/users/register", json={
        "username": username, "password": password, "email": email
    })

    if response.status_code == 202:
        raw = await redis_client.get(f"pending_signup:{email}")
        code = json.loads(raw)["code"]
        await client.post("/users/verify", json={"email": email, "code": code})

    login = await client.post("/users/login", json={"username": username, "password": password})
    return AuthedUser(username, password, email, login.json()["access_token"])

@pytest_asyncio.fixture
async def make_user(client, redis_client):
    counter = {"n": 0}
    async def _make(**overrides):
        counter["n"] += 1
        defaults = {
            "username": f"user{counter['n']}",
            "password": "12345678",
            "email": f"user{counter['n']}@test.com",
        }
        payload = {**defaults, **overrides}
        return await _register_and_login(client, redis_client, **payload)
    return _make

@pytest_asyncio.fixture
async def user(make_user):
    return await make_user()