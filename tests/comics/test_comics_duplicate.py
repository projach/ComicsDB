
import pytest
from httpx import AsyncClient

from tests.conftest import AuthedUser

from .test_comics import comic_payload


@pytest.mark.asyncio
async def test_exact_duplicate_returns_409(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()

    first = await client.post("/comics", json=comic_payload(), headers=user.headers)
    assert first.status_code == 201

    second = await client.post("/comics", json=comic_payload(), headers=user.headers)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_duplicate_with_null_fields_returns_409(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
    payload = comic_payload(
        publisher=None,
        release_date=None,
        acquired_date=None,
        cover=None,
        comic_shop=None,
        price=None,
    )

    first = await client.post("/comics", json=payload, headers=user.headers)
    assert first.status_code == 201

    second = await client.post("/comics", json=payload, headers=user.headers)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_same_key_with_different_extras_is_still_duplicate(client: AsyncClient, make_user):
    # cover, comic_shop, price and acquired_date are not part of the unique key
    user: AuthedUser = await make_user()
    await client.post("/comics", json=comic_payload(), headers=user.headers)

    response = await client.post(
        "/comics",
        json=comic_payload(
            cover="Another cover",
            comic_shop="other shop",
            price=9.99,
            acquired_date="2026-12-01",
        ),
        headers=user.headers,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "change",
    [
        {"issue": 2},
        {"name": "Batman"},
        {"publisher": "DC"},
        {"writer": "Someone Else"},
        {"release_date": "2026-09-01"},
    ],
)
async def test_changing_a_key_field_is_not_a_duplicate(client: AsyncClient, make_user, change):
    user: AuthedUser = await make_user()
    await client.post("/comics", json=comic_payload(), headers=user.headers)

    response = await client.post("/comics", json=comic_payload(**change), headers=user.headers)

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_same_comic_for_different_users_is_allowed(client: AsyncClient, make_user):
    user1: AuthedUser = await make_user()
    user2: AuthedUser = await make_user()

    first = await client.post("/comics", json=comic_payload(), headers=user1.headers)
    second = await client.post("/comics", json=comic_payload(), headers=user2.headers)

    assert first.status_code == 201
    assert second.status_code == 201


@pytest.mark.asyncio
async def test_can_recreate_a_comic_after_deleting_it(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
    created = await client.post("/comics", json=comic_payload(), headers=user.headers)
    comic_id = created.json()["id"]

    await client.delete(f"/comics/{comic_id}", headers=user.headers)
    again = await client.post("/comics", json=comic_payload(), headers=user.headers)

    assert again.status_code == 201


@pytest.mark.asyncio
async def test_update_into_a_duplicate_returns_409(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
    await client.post("/comics", json=comic_payload(issue=1), headers=user.headers)
    second = await client.post("/comics", json=comic_payload(issue=2), headers=user.headers)
    second_id = second.json()["id"]

    response = await client.put(
        f"/comics/{second_id}", json=comic_payload(issue=1), headers=user.headers
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_without_changing_the_key_is_not_a_duplicate(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
    created = await client.post("/comics", json=comic_payload(), headers=user.headers)
    comic_id = created.json()["id"]

    response = await client.put(
        f"/comics/{comic_id}", json=comic_payload(price=1.50), headers=user.headers
    )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_setting_a_null_field_into_a_duplicate_returns_409(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
    await client.post("/comics", json=comic_payload(release_date="2026-08-01"), headers=user.headers)
    other = await client.post("/comics", json=comic_payload(release_date=None), headers=user.headers)
    other_id = other.json()["id"]

    response = await client.put(
        f"/comics/{other_id}",
        json=comic_payload(release_date="2026-08-01"),
        headers=user.headers,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_clearing_a_field_into_a_duplicate_returns_409(client: AsyncClient, make_user):
    user: AuthedUser = await make_user()
    await client.post("/comics", json=comic_payload(release_date=None), headers=user.headers)
    other = await client.post("/comics", json=comic_payload(release_date="2026-08-01"), headers=user.headers)
    other_id = other.json()["id"]

    response = await client.put(
        f"/comics/{other_id}",
        json=comic_payload(release_date=None),
        headers=user.headers,
    )

    assert response.status_code == 409