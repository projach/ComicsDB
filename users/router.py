import asyncpg
from core.auth import hash_password
from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException

import users.crud as crud  # noqa: PLR0402

from .models import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post(path="", response_model=UserOut, status_code=201)
async def register(user: UserCreate, db=Depends(get_db)):
    hashed_password = hash_password(password=user.password)
    try:
        new_user = await crud.create_user(db=db, username=user.username, hashed_password=hashed_password)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Username already taken")
    return new_user