import pytest
from httpx import AsyncClient
from core.logging import logger


async def get_token(client: AsyncClient, username="projach", password="12345678", email= "a@g.c"):
    await client.post("/users/register", json={"username": username, "password": password, "email":email})
    response = await client.post("/users/login", json={"username": username, "password": password})

    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_comics_requires_auth(client: AsyncClient):
    response = await client.post("/comics", json={
            "issue": 3,
            "name": "D'Orc",
            "publisher": "image comics",
            "writer": "Brett Bean",
            "release_date": "2026-08-01",
            "aquired_date": None,
            "cover": "Cover D Brett Bean I Hate Fairyland Team Up NSFW Variant",
            "comic_shop": "star comics",
            "price" : 3.99
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_comics_and_get_comic(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/comics", json={
        "issue": 3,
        "name": "D'Orc",
        "publisher": "image comics",
        "writer": "Brett Bean",
        "release_date": "2026-08-01",
        "aquired_date": None,
        "cover": "Cover D Brett Bean I Hate Fairyland Team Up NSFW Variant",
        "comic_shop": "star comics",
        "price" : 3.99
    }, headers = headers)

    assert response.status_code == 201

    response = await client.get("/comics", headers = headers)

    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_user_cannot_see_others_comics(client: AsyncClient):
    projach_token = await get_token(client)
    headers_projach = {"Authorization": f"Bearer {projach_token}"}

    luckypro_token = await get_token(client, "luckypro", "12345678", "a@c.c")
    headers_luckypro = {"Authorization": f"Bearer {luckypro_token}"}

    await client.post("/comics", json={
        "issue": 3,
        "name": "D'Orc",
        "publisher": "image comics",
        "writer": "Brett Bean",
        "release_date": "2026-08-01",
        "aquired_date": None,
        "cover": "Cover D Brett Bean I Hate Fairyland Team Up NSFW Variant",
        "comic_shop": "star comics",
        "price" : 3.99
    }, headers = headers_projach)

    response = await client.get("/comics", headers = headers_luckypro)

    assert response.json() == []
    
@pytest.mark.asyncio
async def test_user_update(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/comics", json={
        "issue": 3,
        "name": "D'Orc",
        "publisher": "image comics",
        "writer": "Brett Bean",
        "release_date": "2026-08-01",
        "aquired_date": None,
        "cover": "Cover D Brett Bean I Hate Fairyland Team Up NSFW Variant",
        "comic_shop": "CIA",
        "price" : 3.99
    }, headers=headers)
    id = response.json()["id"]
    
    response = await client.put(f"/comics/{id}", json={
        "issue": 1,
        "name": "Batman",
        "publisher": "DC",
        "writer": "Frank Miller",
        "release_date": "2026-07-01",
        "aquired_date": "2026-08-01",
        "cover": None,
        "comic_shop": "CIA",
        "price" : 2.99
    }, headers=headers)
    
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_delete_comic(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/comics", json={
        "issue": 3,
        "name": "D'Orc",
        "publisher": "image comics",
        "writer": "Brett Bean",
        "release_date": "2026-08-01",
        "aquired_date": None,
        "cover": "Cover D Brett Bean I Hate Fairyland Team Up NSFW Variant",
        "comic_shop": "CIA",
        "price" : 3.99
    }, headers=headers)
    id = response.json()["id"]
    
    response = await client.delete(f"/comics/{id}", headers=headers)
    
    assert response.status_code == 200