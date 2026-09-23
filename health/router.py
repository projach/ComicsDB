import asyncio
from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db
from core.redis_client import get_redis

router = APIRouter(tags=["health"])

@router.post("/awake")
async def awake(db=Depends(get_db), redis=Depends(get_redis)):
    async def ping_db():
        async with db.acquire() as conn:
            conn.execute("SELECT 1")
    async def ping_redis():
        await redis.ping()

    await asyncio.gather(ping_db(), ping_redis())