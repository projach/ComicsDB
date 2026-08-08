from pydantic import BaseModel, Field


class ComicCreate(BaseModel):
    issue: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=1000)
    publisher: str = Field(min_length=1)

    model_config = {"extra":"forbid"}

class Comic(ComicCreate):
    id: int
    