import asyncpg
from models import Comic, ComicCreate


async def add_comic(comic: ComicCreate, db: asyncpg.Pool):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO comics (issue, name, publisher) VALUES($1,$2,$3) RETURNING id",
            comic.issue, comic.name, comic.publisher
        )
    return Comic(id=row["id"], **comic.model_dump())


async def update_comic_by_id(
    id: int,
    comic: ComicCreate,
    db: asyncpg.Pool
) -> bool:
    async with db.acquire() as conn:
        result = await conn.execute(
            "UPDATE comics SET name = $1, issue = $2, publisher = $3 WHERE id = $4",
            comic.name, comic.issue, comic.publisher, id
        )
    return result.endswith("1")

async def get_comic_by_id(id: int, db: asyncpg.Pool):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, issue, publisher FROM comics WHERE id = $1", id
        )
        if row is None:
            return None
        return Comic(id=row["id"], name=row["name"], issue=row["issue"], publisher=row["publisher"])


async def get_comics(db: asyncpg.Pool):
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, issue, publisher FROM comics")
        return [Comic(id=r["id"], name=r["name"], issue=r["issue"], publisher=r["publisher"]) for r in rows]


async def delete_comic_by_id(id: int, db: asyncpg.Pool) -> bool:
    async with db.acquire() as conn:
        result = await conn.execute("DELETE FROM comics WHERE id = $1", id)
        return result.endswith("1")
