from pydantic import BaseModel, Field
from datetime import date


class ComicCreate(BaseModel):
    issue: int = Field(ge=0, lt=9999)
    name: str = Field(min_length=1, max_length=200)
    publisher: str | None = Field(default=None, min_length=1, max_length=200)
    writer: str = Field(min_length=1, max_length=200)
    release_date: date | None = None,
    aquired_date: date | None = None,
    cover: str | None = Field(default=None, min_length=1, max_length=200)
    comic_shop: str | None = Field(default=None, min_length=1, max_length=200)
    price: float | None = Field(default=None, ge=0)
    
    model_config = {"extra":"forbid"}

class Comic(ComicCreate):
    id: int
    