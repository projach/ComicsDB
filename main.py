from comics.router import router as comics_router
from core.database import lifespan
from fastapi import FastAPI
from users.router import router as users_router
from health.router import router as health_router
from __version__ import version

app = FastAPI(lifespan=lifespan, version=version)

app.include_router(comics_router)
app.include_router(users_router)
app.include_router(health_router)