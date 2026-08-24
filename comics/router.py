import asyncpg
from core.auth import get_current_user
from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from enum import Enum

import comics.crud as crud  # noqa: PLR0402
from comics.models import Comic, ComicCreate


router = APIRouter(prefix="/comics", tags=["comics"])

class SortField(str, Enum):
    issue = "issue"
    comic_name = "name"
    publisher = "publisher"
    writer = "writer"
    release_date = "release_date"
    aquired_date = "aquired_date"
    cover = "cover"
    comic_shop = "comic_shop"
    price = "price"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@router.post("", response_model=Comic, status_code=201)
async def add_comic(comic: ComicCreate, db = Depends(get_db), current_user: dict = Depends(get_current_user)):  # noqa: B008
    try:
        return await crud.add_comic(comic, db, current_user["id"])
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Comic already exists")

@router.put("/{id}")
async def update_comic_by_id(id: int, comic: ComicCreate, db = Depends(get_db), current_user: dict = Depends(get_current_user)): # noqa: B008
    try:
        updated = await crud.update_comic_by_id(id, comic, db, current_user["id"])
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Another comic already has this name/issue/publisher")
    if not updated:
        raise HTTPException(status_code=404, detail="Comic not found")
    return {"ok": True}

@router.get("/{id}", response_model=Comic)
async def get_comic_by_id(id: int, db = Depends(get_db), current_user: dict = Depends(get_current_user)): # noqa: B008
    comic = await crud.get_comic_by_id(id, db, current_user["id"])
    if comic is None:
        raise HTTPException(status_code=404, detail= "comic not found")
    return comic

@router.get("", response_model=list[Comic])
async def get_comics(
    sort_by: SortField = SortField.comic_name,
    sort_order: SortOrder = SortOrder.asc,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db = Depends(get_db), # noqa: B008
    current_user: dict = Depends(get_current_user) # noqa: B008
):
    sort = f"{sort_by.value} {sort_order.value.upper()}"
    return await crud.get_comics(sort=sort, offset=offset, limit=limit, db=db, current_user=current_user["id"])

@router.delete("/{id}")
async def delete_comic_by_id(id: int, db = Depends(get_db), current_user: dict = Depends(get_current_user)): # noqa: B008
    updated = await crud.delete_comic_by_id(id, db, current_user["id"])
    if not updated:
        raise HTTPException(404, "Comic not found")
    return {"ok": True}
