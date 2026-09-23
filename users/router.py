import asyncpg
from fastapi import APIRouter, Depends, HTTPException

import users.crud as crud  # noqa: PLR0402
from users.auth import create_pending_signup, get_pending_signup, delete_pending_signup, resend_pending_signup_code
from core.auth import create_access_token, hash_password, verify_password
from users.exceptions import CooldownException, PendingSignupNotFoundException
from core.database import get_db
from core.redis_client import get_redis
from core.email.client import send_email

from .models import UserCreate, UserOut, User, VerifyRequest, ResendCodeRequest

from core.email.templates import auth_code_template

router = APIRouter(prefix="/users", tags=["users"])

@router.post(path="/register", status_code=202)
async def register(user: UserCreate, db=Depends(get_db), redis=Depends(get_redis)):  # noqa: B008
    email_row = await crud.get_user_by_email(db=db, email=user.email)
    if email_row is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    username_row = await crud.get_user_by_username(db=db, username=user.username)
    if username_row is not None:
        raise HTTPException(status_code=409, detail="Username already registered")
            
    hashed_password = hash_password(password=user.password)
    
    try:
        code = await create_pending_signup(email=user.email, username=user.username, hashed_password=hashed_password, redis_client=redis)
    except CooldownException as e:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {e.seconds_remaining} seconds before requesting another code",
        )
        
    send_email(to=user.email, template=auth_code_template(code=code))
    
    return {"detail": "Verification code sent"}

@router.post(path="/resend-code", status_code=201)
async def resend_code(payload:ResendCodeRequest, redis=Depends(get_redis)):
    try:
        code = await resend_pending_signup_code(payload.email, redis_client=redis)
    except CooldownException as e:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {e.seconds_remaining} seconds before requesting another code",
        )
    except PendingSignupNotFoundException:
        raise HTTPException(status_code=404, detail="No pending registration found for this email")

    send_email(payload.email, auth_code_template(code))
    return {"detail": "Verification code sent"}

@router.post(path="/verify", response_model=UserOut, status_code=201)
async def verify(payload:VerifyRequest, db=Depends(get_db), redis=Depends(get_redis)) -> UserOut:
    pending = await get_pending_signup(email=payload.email, redis_client=redis)
    if not pending or pending["code"] != payload.code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    try:
        new_user = await crud.create_user(
            db=db,
            username=pending["username"],
            hashed_password=pending["hashed_password"],
            email=pending["email"],
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Username or email already registered")

    await delete_pending_signup(email=payload.email, redis_client=redis)
    return new_user

@router.post(path="/login")
async def login(user: User, db=Depends(get_db)):  # noqa: B008
    row = await crud.get_user_by_username(db=db, username=user.username)
    if row is None or not verify_password(user.password, row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token, expires_at = create_access_token({"sub":row["username"]})
    return {
        "access_token": token, 
        "token_type": "bearer",
        "expires_at": expires_at
    }