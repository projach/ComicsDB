from comics.router import router as comics_router
from core.database import lifespan
from fastapi import FastAPI

app = FastAPI(lifespan=lifespan)

app.include_router(comics_router)