from comics.router import router as comics_router
from core.database import lifespan
from fastapi import FastAPI
from users.router import router as users_router

app = FastAPI(lifespan=lifespan)

app.include_router(comics_router)
app.include_router(users_router)