import asyncpg
import pytest
from httpx import AsyncClient
from tests.conftest import TEST_DATABASE_URL


@pytest.mark.asyncio
async def test_delete_me_requires_auth(client: AsyncClient):
    response = await client.delete("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_me_returns_204(client: AsyncClient, user):
    response = await client.delete("/users/me", headers=user.headers)
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.asyncio
async def test_deleted_user_cannot_login(client: AsyncClient, user):
    await client.delete("/users/me", headers=user.headers)

    response = await client.post("/users/login", json={
        "username": user.username, "password": user.password
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_is_rejected_after_delete(client: AsyncClient, user):
    await client.delete("/users/me", headers=user.headers)

    response = await client.delete("/users/me", headers=user.headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_me_does_not_affect_other_users(client: AsyncClient, make_user):
    user1 = await make_user()
    user2 = await make_user()

    await client.delete("/users/me", headers=user1.headers)

    login = await client.post("/users/login", json={
        "username": user2.username, "password": user2.password
    })
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_delete_me_cascades_to_comics(client: AsyncClient, user):
    response = await client.post("/comics", json={
            "issue": 3,
            "name": "D'Orc",
            "publisher": "image comics",
            "writer": "Brett Bean",
            "release_date": "2026-08-01",
            "acquired_date": None,
            "cover": "Cover D Brett Bean I Hate Fairyland Team Up NSFW Variant",
            "comic_shop": "star comics",
            "price" : 3.99
        }, headers = user.headers)
    assert response.status_code in (200, 201)

    conn = await asyncpg.connect(TEST_DATABASE_URL)
    try:
        user_id = await conn.fetchval("SELECT id FROM users WHERE username = $1", user.username)
        before = await conn.fetchval("SELECT count(*) FROM comics WHERE user_id = $1", user_id)
        assert before == 1

        response = await client.delete("/users/me", headers=user.headers)
        assert response.status_code == 204

        after = await conn.fetchval("SELECT count(*) FROM comics WHERE user_id = $1", user_id)
        assert after == 0
    finally:
        await conn.close()