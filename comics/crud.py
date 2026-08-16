import asyncpg

from .models import Comic, ComicCreate


async def add_comic(comic: ComicCreate, db: asyncpg.Pool, current_user: str):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO comics (issue, name, publisher, writer, user_id) VALUES($1,$2,$3,$4, $5) RETURNING id",
            comic.issue, comic.name, comic.publisher, comic.writer, current_user
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
            "UPDATE comics SET name = $1, issue = $2, publisher = $3, writer = $4 WHERE id = $5 AND user_id = $6",
            comic.name, comic.issue, comic.publisher, comic.writer, id, current_user
        )
    return result.endswith("1")

async def get_comic_by_id(id: int, db: asyncpg.Pool, current_user: str):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, issue, publisher, writer FROM comics WHERE id = $1 AND user_id = $2",
            id, current_user
        )
        if row is None:
            return None
        return Comic(id=row["id"], name=row["name"], issue=row["issue"], publisher=row["publisher"], writer=row["writer"])


async def get_comics(db: asyncpg.Pool, current_user: str):
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, issue, publisher, writer FROM comics WHERE user_id = $1", current_user)
        return [Comic(id=r["id"], name=r["name"], issue=r["issue"], publisher=r["publisher"], writer=r["writer"]) for r in rows]


async def delete_comic_by_id(id: int, db: asyncpg.Pool, current_user: str) -> bool:
    async with db.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM comics WHERE id = $1 AND user_id = $2",
            id, current_user
        )
        return result.endswith("1")
