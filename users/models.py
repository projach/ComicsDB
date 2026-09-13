from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(min_length=4, max_length=14, description="4-14 characters")
    password: str = Field(min_length=8, description="Minimum 8 characters")
    
    model_config = {"extra":"forbid"}

class UserCreate(User):
    email: EmailStr

class UserOut(BaseModel):
    username: str
    email: str
    
class VerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    
    model_config = {"extra":"forbid"}