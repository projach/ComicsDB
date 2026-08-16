import pytest


async def get_token(client, username="projach", password="12345678"):
    await client.post("/users/register", json={"username": username, "password": password})
    response = await client.post("/users/login", json={"username": username, "password": password})

    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_comics_requires_auth(client):
    response = await client.post("/comics", json={
        "issue": 1, "name": "Batman", "publisher": "DC", "writer": "Frank Miller"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_comics_and_get_comic(client, capsys):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/comics", json={
        "issue": 1, "name": "Batman", "publisher": "DC", "writer": "Frank Miller"
    }, headers = headers)

    assert response.status_code == 201

    response = await client.get("/comics", headers = headers)

    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_user_cannot_see_others_comics(client):
    projach_token = await get_token(client)
    headers_projach = {"Authorization": f"Bearer {projach_token}"}

    luckypro_token = await get_token(client, "luckypro", "12345678")
    headers_luckypro = {"Authorization": f"Bearer {luckypro_token}"}

    await client.post("/comics", json={
        "issue": 1, "name": "Batman", "publisher": "DC", "writer": "Frank Miller"
    }, headers = headers_projach)

    response = await client.get("/comics", headers = headers_luckypro)

    assert response.json() == []