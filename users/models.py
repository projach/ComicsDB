from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=6, max_length=14)
    password: str = Field(min_length=8) 

class UserOut(BaseModel):
    id: int
    username: str