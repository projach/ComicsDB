import pytest
from httpx import AsyncClient
from core.logging import logger
from .conftest import AuthedUser

def comic_payload(**overrides):
    base = {
            "issue": 1,
            "name": "D'Orc",
            "publisher": "image comics",
            "writer": "Brett Bean",
            "release_date": "2026-08-01",
            "aquired_date": "2026-10-01",
            "cover": "Cover D Brett Bean I Hate Fairyland Team Up NSFW Variant",
            "comic_shop": "star comics",
            "price" : 3.99
    }
    return {**base, **overrides}

@pytest.mark.asyncio
async def test_create_comics_requires_auth(client: AsyncClient):
    response = await client.post("/comics", json=comic_payload()
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_comics_and_get_comic(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
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
    }, headers = user.headers)

    assert response.status_code == 201

    response = await client.get("/comics", headers = user.headers)

    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_user_cannot_see_others_comics(client: AsyncClient, make_user):
    user1: AuthedUser = await make_user()
    user2: AuthedUser = await make_user()

    await client.post("/comics", json=comic_payload(), headers = user1.headers)

    response = await client.get("/comics", headers = user2.headers)

    assert response.json() == []
    
@pytest.mark.asyncio
async def test_user_update(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
    response = await client.post("/comics", json=comic_payload(), headers=user.headers)
    id = response.json()["id"]
    
    response = await client.put(f"/comics/{id}", json=comic_payload(issue=2), headers=user.headers)
    
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_delete_comic(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
    response = await client.post("/comics", json=comic_payload(), headers=user.headers)
    id = response.json()["id"]
    
    response = await client.delete(f"/comics/{id}", headers=user.headers)
    
    assert response.status_code == 200