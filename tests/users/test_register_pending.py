import json

import pytest
from httpx import AsyncClient

from core.email.exceptions import EmailSendException
from tests.conftest import user_payload


@pytest.mark.asyncio
async def test_register_stores_pending_signup_and_sends_one_email(
    client: AsyncClient, redis_client, no_real_emails
):
    response = await client.post("/users/register", json=user_payload())

    assert response.status_code == 202
    raw = await redis_client.get("pending_signup:test@test.com")
    assert json.loads(raw)["username"] == "projach"
    assert await redis_client.get("pending_username:projach") == "test@test.com"
    assert len(no_real_emails) == 1


@pytest.mark.asyncio
async def test_register_twice_same_email_conflicts_and_keeps_code(
    client: AsyncClient, redis_client, no_real_emails
):
    first = await client.post("/users/register", json=user_payload())
    code_before = json.loads(await redis_client.get("pending_signup:test@test.com"))["code"]

    second = await client.post("/users/register", json=user_payload())

    assert first.status_code == 202
    assert second.status_code == 409
    code_after = json.loads(await redis_client.get("pending_signup:test@test.com"))["code"]
    assert code_after == code_before
    assert len(no_real_emails) == 1


@pytest.mark.asyncio
async def test_register_same_username_other_email_conflicts(client: AsyncClient):
    await client.post("/users/register", json=user_payload(username="bob", email="a@test.com"))

    response = await client.post(
        "/users/register", json=user_payload(username="bob", email="b@test.com")
    )

    assert response.status_code == 409
    assert "username" in str(response.json()["detail"]).lower()


@pytest.mark.asyncio
async def test_register_same_email_other_username_conflicts_and_releases_username(
    client: AsyncClient, redis_client
):
    await client.post("/users/register", json=user_payload(username="bob", email="a@test.com"))

    response = await client.post(
        "/users/register", json=user_payload(username="alice", email="a@test.com")
    )

    assert response.status_code == 409
    assert "email" in str(response.json()["detail"]).lower()
    assert await redis_client.exists("pending_username:alice") == 0

@pytest.mark.asyncio
async def test_register_rolls_back_when_email_fails(client, redis_client, monkeypatch):
    def boom(*args, **kwargs):
        raise EmailSendException()
    monkeypatch.setattr("users.router.send_email", boom)

    response = await client.post("/users/register", json=user_payload())

    assert response.status_code == 503
    assert await redis_client.exists("pending_signup:test@test.com") == 0
    assert await redis_client.exists("pending_username:projach") == 0