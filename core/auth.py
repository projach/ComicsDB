import os
from datetime import datetime, timedelta, timezone

import asyncpg
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from users.crud import get_user_by_username

from .database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 7
ENCODING = "utf-8"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(ENCODING), bcrypt.gensalt()).decode(ENCODING)

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(ENCODING), hashed.encode(ENCODING))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: asyncpg.Pool = Depends(get_db)  # noqa: B008
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    row = await get_user_by_username(db, username)
    if row is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return {"id": row["id"], "username": row["username"]}