import asyncpg
from core.auth import create_access_token, hash_password, verify_password
from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException

import users.crud as crud  # noqa: PLR0402

from .models import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post(path="/register", response_model=UserOut, status_code=201)
async def register(user: UserCreate, db=Depends(get_db)):  # noqa: B008
    hashed_password = hash_password(password=user.password)
    try:
        new_user = await crud.create_user(db=db, username=user.username, hashed_password=hashed_password)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Username already taken")
    return new_user

@router.post(path="/login")
async def login(user: UserCreate, db=Depends(get_db)):  # noqa: B008
    row = await crud.get_user_by_username(db=db, username=user.username)
    if row is None or not verify_password(user.password, row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub":row["username"]})
    return {"access_token": token, "token_type": "bearer"}