import pytest
from httpx import AsyncClient
from .conftest import user_payload, get_verification_code
import redis.asyncio as Redis
import json

@pytest.mark.asyncio
async def test_register_returns_pending(client: AsyncClient):
    response = await client.post(url="/users/register", json=user_payload())
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_verify_with_correct_code_creates_user(client: AsyncClient, redis_client: Redis):
    payload = user_payload()
    await client.post("/users/register", json=payload)
    code = await get_verification_code(redis_client=redis_client, email=payload["email"])
    
    response = await client.post("/users/verify", json={
        "email": payload["email"], "code": code
    })
    assert response.status_code == 201
    assert response.json()["username"] == payload["username"]
    
@pytest.mark.asyncio
async def test_verify_with_wrong_code_fails(client: AsyncClient):
    payload = user_payload()
    
    await client.post("/users/register", json=payload)
        
    response = await client.post("/users/verify", json={
        "email": payload["email"], "code": "002345"
    })
    assert response.status_code == 400
    
@pytest.mark.asyncio
async def test_login_before_verification_fails(client: AsyncClient):
    payload = user_payload()
        
    await client.post("/users/register", json=payload)
    
    response = await client.post("/users/login", json={
        "username": payload["username"], "password": payload["password"]
    })
    
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, make_user):
    user = await make_user()
    
    response = await client.post("/users/login", json={
        "username": user.username, "password": "wrong-password"
    })
    
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_register_missing_email_rejected(client: AsyncClient):
    response = await client.post("/users/register", json=user_payload(email=None))
    
    assert response.status_code == 422
    