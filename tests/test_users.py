import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    response = await client.post("/users/register", json={
        "username": "projach", "password": "123456789", "email":"a@g.c"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "projach"

    response = await client.post("/users/login",json={
        "username": "projach", "password": "123456789"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/users/register", json={
        "username": "projach", "password": "123456789", "email":"a@g.c"
    })

    response = await client.post("/users/login", json={
        "username": "projach", "password": "11231233"
    })

    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_login_missing_email(client: AsyncClient):
    await client.post("/users/register", json={
        "username": "projach", "password": "123456789"
    })

    response = await client.post("/users/login", json={
        "username": "projach", "password": "11231233"
    })

    assert response.status_code == 401