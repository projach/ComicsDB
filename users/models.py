from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=4, max_length=14, description="4-14 characters")
    password: str = Field(min_length=8, description="Minimum 8 characters") 

class UserOut(BaseModel):
    id: int
    username: str