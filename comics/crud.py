import asyncpg

from .models import Comic, ComicCreate
from core.logging import logger


async def add_comic(comic: ComicCreate, db: asyncpg.Pool, current_user: str):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO comics (issue, name, publisher, writer, release_date, acquired_date, cover, comic_shop, price, user_id)
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id
            """,
            comic.issue,
            comic.name,
            comic.publisher,
            comic.writer, 
            comic.release_date, 
            comic.acquired_date, 
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
            UPDATE comics SET name = $1, issue = $2, publisher = $3, writer = $4, release_date = $5, acquired_date = $6, cover = $7, comic_shop = $8, price = $9
            WHERE id = $10 AND user_id = $11
            """,
            comic.name, 
            comic.issue, 
            comic.publisher, 
            comic.writer, 
            comic.release_date, 
            comic.acquired_date, 
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
            "SELECT id, issue, name, publisher, writer, release_date, acquired_date, cover, comic_shop, price FROM comics WHERE id = $1 AND user_id = $2",
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
            acquired_date=row["acquired_date"], 
            cover=row["cover"], 
            comic_shop=row["comic_shop"]
        )

def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def get_comics(sort: str, offset: int, limit: int, db: asyncpg.Pool, current_user: str, search: str | None):
    async with db.acquire() as conn:
        conn: asyncpg.Connection

        conditions = ["user_id = $1"]
        params: list = [current_user]

        search = search.strip() if search else None
        if search:
            params.append(f"%{escape_like(search)}%")
            n = len(params)
            conditions.append(
                f"(name ILIKE ${n} OR publisher ILIKE ${n} OR writer ILIKE ${n})"
            )

        params.extend([offset, limit])
        offset_idx, limit_idx = len(params) - 1, len(params)

        query = f"""
            SELECT id, issue, name, publisher, writer, release_date,
                acquired_date, cover, comic_shop, price
            FROM comics
            WHERE {" AND ".join(conditions)}
            ORDER BY {sort}, id
            OFFSET ${offset_idx} LIMIT ${limit_idx}
        """

        logger.debug(f"query is: {query} search is: {escape_like(search) if search else None} and params are: {params}")
        rows = await conn.fetch(query, *params)

        return [Comic(**row) for row in rows]


async def delete_comic_by_id(id: int, db: asyncpg.Pool, current_user: str) -> bool:
    async with db.acquire() as conn:
        conn: asyncpg.Connection
        result = await conn.execute(
            "DELETE FROM comics WHERE id = $1 AND user_id = $2",
            id, current_user
        )
        return result.endswith("1")
