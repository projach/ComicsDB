import sqlite3

import crud
import database
from fastapi import Depends, FastAPI, HTTPException
from models import Comic, ComicCreate

app = FastAPI(lifespan=database.lifespan)

@app.post("/comics", response_model=Comic, status_code=201)
async def add_comic(comic: ComicCreate, db = Depends(database.get_db)):  # noqa: B008
    try:
        return await crud.add_comic(comic, db)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Comic already exists")

@app.put("/comics/{id}")
async def update_comic_by_id(id: int, comic: ComicCreate, db = Depends(database.get_db)): # noqa: B008
    try:
        updated = await crud.update_comic_by_id(id, comic, db)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Another comic already has this name/issue/publisher")
    if not updated:
        raise HTTPException(status_code=404, detail="Comic not found")
    return {"ok": True}

@app.get("/comics/{id}")
async def get_comic_by_id(id: int, db = Depends(database.get_db)): # noqa: B008
    comic = await crud.get_comic_by_id(id, db)
    if comic is None:
        raise HTTPException(status_code=404, detail= "comic not found")
    return comic

@app.get("/comics")
async def get_comics(db = Depends(database.get_db)): # noqa: B008
    return await crud.get_comics(db)

@app.delete("/comics/{id}")
async def delete_comic_by_id(id: int, db = Depends(database.get_db)): # noqa: B008
    updated = await crud.delete_comic_by_id(id, db)
    if not updated:
        raise HTTPException(404, "Comic not found")
    return {"ok": True}
