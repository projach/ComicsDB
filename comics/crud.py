import asyncpg

from .models import Comic, ComicCreate
from core.logging import logger


async def add_comic(comic: ComicCreate, db: asyncpg.Pool, current_user: str):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO comics (issue, name, publisher, writer, release_date, aquired_date, cover, comic_shop, price, user_id)
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id
            """,
            comic.issue,
            comic.name,
            comic.publisher,
            comic.writer, 
            comic.release_date, 
            comic.aquired_date, 
            comic.cover, 
            comic.comic_shop, 
            comic.price, 
            current_user
        )
    return Comic(id=row["id"], **comic.model_dump())

async def update_comic_by_id(
    id: int,
    comic: ComicCreate,
    db: asyncpg.Pool,
    current_user: str
) -> bool:
    async with db.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE comics SET name = $1, issue = $2, publisher = $3, writer = $4, release_date = $5, aquired_date = $6, cover = $7, comic_shop = $8, price = $9
            WHERE id = $10 AND user_id = $11
            """,
            comic.name, 
            comic.issue, 
            comic.publisher, 
            comic.writer, 
            comic.release_date, 
            comic.aquired_date, 
            comic.cover, 
            comic.comic_shop, 
            comic.price, 
            id, 
            current_user
        )
    return result.endswith("1")

async def get_comic_by_id(id: int, db: asyncpg.Pool, current_user: str):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, issue, name, publisher, writer, release_date, aquired_date, cover, comic_shop, price FROM comics WHERE id = $1 AND user_id = $2",
            id, current_user
        )
        if row is None:
            return None
        return Comic(
            id=row["id"], 
            name=row["name"], 
            issue=row["issue"], 
            publisher=row["publisher"], 
            writer=row["writer"], 
            release_date=row["release_date"], 
            aquired_date=row["aquired_date"], 
            cover=row["cover"], 
            comic_shop=row["comic_shop"]
        )


async def get_comics(sort: str, offset: int, limit: int, db: asyncpg.Pool, current_user: str):
    async with db.acquire() as conn:
        conn: asyncpg.Connection
        logger.debug(f"sort is {sort}")
        rows = await conn.fetch(
            f"""SELECT id, issue, name, publisher, writer, release_date, aquired_date, cover, comic_shop, price 
            FROM comics WHERE user_id = $1 ORDER BY {sort} OFFSET $2 LIMIT $3""",
            current_user,
            offset, 
            limit
        )
        return [
            Comic(
                id=row["id"], 
                name=row["name"], 
                issue=row["issue"], 
                publisher=row["publisher"], 
                writer=row["writer"], 
                release_date=row["release_date"], 
                aquired_date=row["aquired_date"], 
                cover=row["cover"],
                comic_shop=row["comic_shop"],
                price=row["price"]
            ) for row in rows
        ]


async def delete_comic_by_id(id: int, db: asyncpg.Pool, current_user: str) -> bool:
    async with db.acquire() as conn:
        conn: asyncpg.Connection
        result = await conn.execute(
            "DELETE FROM comics WHERE id = $1 AND user_id = $2",
            id, current_user
        )
        return result.endswith("1")
