from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=14,
        pattern=r"^[A-Za-z0-9_.-]+$",
    ),
    Field(description="3-14 characters: letters, digits, underscore, dot or hyphen. No spaces."),
]

class User(BaseModel):
    username: Username
    password: str = Field(min_length=8, description="Minimum 8 characters")
    
    model_config = {"extra":"forbid"}

class UserCreate(User):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

class UserOut(BaseModel):
    username: Username
    email: str
    
class VerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    
    model_config = {"extra":"forbid"}

class ResendCodeRequest(BaseModel):
    email: EmailStr

    model_config = {"extra":"forbid"}