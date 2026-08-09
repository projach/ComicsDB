import asyncpg
from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException

import comics.crud as crud  # noqa: PLR0402
from comics.models import Comic, ComicCreate

router = APIRouter(prefix="/comics", tags=["comics"])


@router.post("", response_model=Comic, status_code=201)
async def add_comic(comic: ComicCreate, db = Depends(get_db)):  # noqa: B008
    try:
        return await crud.add_comic(comic, db)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Comic already exists")

@router.put("/{id}")
async def update_comic_by_id(id: int, comic: ComicCreate, db = Depends(get_db)): # noqa: B008
    try:
        updated = await crud.update_comic_by_id(id, comic, db)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Another comic already has this name/issue/publisher")
    if not updated:
        raise HTTPException(status_code=404, detail="Comic not found")
    return {"ok": True}

@router.get("/{id}")
async def get_comic_by_id(id: int, db = Depends(get_db)): # noqa: B008
    comic = await crud.get_comic_by_id(id, db)
    if comic is None:
        raise HTTPException(status_code=404, detail= "comic not found")
    return comic

@router.get("", response_model=list[Comic])
async def get_comics(db = Depends(get_db)): # noqa: B008
    return await crud.get_comics(db)

@router.delete("/{id}", response_model=Comic)
async def delete_comic_by_id(id: int, db = Depends(get_db)): # noqa: B008
    updated = await crud.delete_comic_by_id(id, db)
    if not updated:
        raise HTTPException(404, "Comic not found")
    return {"ok": True}
