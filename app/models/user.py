from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone

from app.models.task import PyObjectId

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class UserResponse(UserBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
