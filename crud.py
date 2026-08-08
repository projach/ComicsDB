import aiosqlite
import models


async def add_comic(comic: models.ComicCreate, db: aiosqlite.Connection):
    cursor = await db.execute(
        "INSERT INTO comics (issue, name, publisher) VALUES(?,?,?)",
        (comic.issue, comic.name, comic.publisher),
    )
    await db.commit()
    id = cursor.lastrowid
    return models.Comic(id=id, **comic.model_dump())


async def update_comic_by_id(
    id: int,
    comic: models.ComicCreate,
    db: aiosqlite.Connection
):
    cursor = await db.execute(
        "UPDATE comics SET name = ?, issue = ?, publisher = ? WHERE id = ?",
        [comic.name, comic.issue, comic.publisher, id],
    )
    await db.commit()
    return cursor.rowcount > 0

async def get_comic_by_id(id: int, db: aiosqlite.Connection):
    cursor = await db.execute("SELECT name, issue, publisher FROM comics WHERE id = ?",[id])
    row = await cursor.fetchone()
    if row is None:
        return None
    return {"name": row[0], "issue": row[1], "publisher": row[2]}

async def get_comics(db: aiosqlite.Connection):
    cursor = await db.execute("SELECT id, name, issue, publisher FROM comics")
    rows = await cursor.fetchall()
    return [
        {"id": r[0], "name": r[1], "issue": r[2], "publisher": r[3]}
        for r in rows
    ]

async def delete_comic_by_id(id: int, db: aiosqlite.Connection):
    cursor = await db.execute("DELETE FROM comics WHERE id = ?", [id])
    await db.commit()
    if cursor.rowcount > 0: 
        return True
