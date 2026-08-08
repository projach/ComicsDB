from contextlib import asynccontextmanager

import aiosqlite
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await aiosqlite.connect("comics.db")

    await app.state.db.execute("""
        CREATE TABLE IF NOT EXISTS comics(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue INTEGER,
            name TEXT,
            publisher TEXT,
            UNIQUE(issue, name, publisher)
        )
    """)

    await app.state.db.commit()

    yield

    await app.state.db.close()

async def get_db(request: Request) -> aiosqlite.Connection:
    return request.app.state.db