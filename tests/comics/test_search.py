import pytest
from httpx import AsyncClient

from tests.conftest import AuthedUser
from .test_comics import comic_payload


async def create_comic(client: AsyncClient, user: AuthedUser, **overrides):
    response = await client.post("/comics", json=comic_payload(**overrides), headers=user.headers)
    assert response.status_code == 201
    return response.json()


async def search(client: AsyncClient, user: AuthedUser, text: str | None, **params):
    if text is not None:
        params["search"] = text
    response = await client.get("/comics", params=params, headers=user.headers)
    assert response.status_code == 200
    return response.json()


def names(results):
    return [c["name"] for c in results]


async def seed(client: AsyncClient, user: AuthedUser):
    await create_comic(client, user, name="Batman", publisher="DC", writer="Matt Fraction", issue=1)
    await create_comic(client, user, name="Batman", publisher="DC", writer="Matt Fraction", issue=3)
    await create_comic(client, user, name="I hate fairyland", publisher="Image", writer="Scotty young")
    await create_comic(client, user, name="Spiderman", publisher="Marvel", writer="Stan Lee")
    await create_comic(client, user, name="100% Real", publisher="Indie", writer="Jane Doe")


@pytest.mark.asyncio
async def test_search_matches_name_substring(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert names(await search(client, user, "bat")) == ["Batman", "Batman"]

@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["bat", "BAT", "BaTmAn"])
async def test_search_is_case_insensitive(client: AsyncClient, make_user, text):
    user = await make_user()
    await seed(client, user)

    assert names(await search(client, user, text)) == ["Batman", "Batman"]


@pytest.mark.asyncio
async def test_search_matches_publisher(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert names(await search(client, user, "marvel")) == ["Spiderman"]


@pytest.mark.asyncio
async def test_search_matches_writer(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert names(await search(client, user, "stan")) == ["Spiderman"]

@pytest.mark.asyncio
async def test_search_strips_surrounding_whitespace(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert names(await search(client, user, "  bat  ")) == ["Batman", "Batman"]


@pytest.mark.asyncio
async def test_blank_search_returns_everything(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert len(await search(client, user, "   ")) == 5


@pytest.mark.asyncio
async def test_no_search_param_returns_everything(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert len(await search(client, user, None)) == 5


@pytest.mark.asyncio
async def test_search_with_no_match_returns_empty_list(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert await search(client, user, "zzzz") == []


@pytest.mark.asyncio
async def test_search_with_apostrophe(client: AsyncClient, make_user):
    user = await make_user()
    await create_comic(client, user)

    assert names(await search(client, user, "d'orc")) == ["D'Orc"]

@pytest.mark.asyncio
async def test_cover_text_is_not_searched(client: AsyncClient, make_user):
    user = await make_user()
    await create_comic(client, user)

    assert await search(client, user, "fairyland") == []


@pytest.mark.asyncio
async def test_missing_space_does_not_match_yet(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert await search(client, user, "ihate") == []

@pytest.mark.asyncio
async def test_percent_is_matched_literally(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert names(await search(client, user, "100%")) == ["100% Real"]


@pytest.mark.asyncio
async def test_underscore_is_matched_literally(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert await search(client, user, "b_t") == []

@pytest.mark.asyncio
async def test_search_never_returns_other_users_comics(client: AsyncClient, make_user):
    user1 = await make_user()
    user2 = await make_user()
    await create_comic(client, user1, name="Batman")
    await create_comic(client, user2, name="Batman Beyond")

    assert names(await search(client, user1, "bat")) == ["Batman"]
    assert names(await search(client, user2, "bat")) == ["Batman Beyond"]


@pytest.mark.asyncio
async def test_sql_injection_in_search_is_harmless(client: AsyncClient, make_user):
    user = await make_user()
    await seed(client, user)

    assert await search(client, user, "'; DROP TABLE comics; --") == []
    assert len(await search(client, user, None)) == 5


@pytest.mark.asyncio
async def test_sql_injection_in_sort_by_is_rejected(client: AsyncClient, make_user):
    user = await make_user()

    response = await client.get(
        "/comics",
        params={"sort_by": "name; DROP TABLE comics", "search": "bat"},
        headers=user.headers,
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_pagination_with_search_has_no_duplicates_or_gaps(client: AsyncClient, make_user):
    user = await make_user()
    for issue in range(1, 6):
        await create_comic(client, user, name="Batman", issue=issue)

    page1 = await search(client, user, "bat", limit=2, offset=0)
    page2 = await search(client, user, "bat", limit=2, offset=2)
    page3 = await search(client, user, "bat", limit=2, offset=4)
    everything = await search(client, user, "bat", limit=100)

    paged_ids = [c["id"] for c in page1 + page2 + page3]
    assert paged_ids == [c["id"] for c in everything]
    assert len(set(paged_ids)) == 5


@pytest.mark.asyncio
async def test_limit_above_max_is_rejected(client: AsyncClient, make_user):
    user = await make_user()

    response = await client.get("/comics", params={"limit": 101}, headers=user.headers)

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_search_below_limit_is_rejected(client: AsyncClient, make_user):
    user = await make_user()

    response = await client.get("/comics", params={"search": ""}, headers=user.headers)

    assert response.status_code == 422

    response = await client.get("/comics", params={"search": " "}, headers=user.headers)
    
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("order", ["asc", "desc"])
async def test_sort_order_with_search(client: AsyncClient, make_user, order):
    user = await make_user()
    for name in ["Batwoman", "Batgirl", "Batman"]:
        await create_comic(client, user, name=name)

    result = names(await search(client, user, "bat", sort_order=order))

    assert result == sorted(result, reverse=(order == "desc"))