from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from pydantic import EmailStr, BaseModel
from pydantic import conint


class UserCreate(SQLModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        orm_mode = True

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    id: Optional[str] = None

class VideoBase(SQLModel):
    title: str
    description: Optional[str] = None
    url: str

class VideoCreate(VideoBase):
    pass                                          # same fields as base

class VideoRead(VideoBase):
    id: int
    uploaded_at: datetime
    class Config:
        from_attributes = True


class InteractionCreate(SQLModel):
    video_id: int
    action: str                                   # "watch", "like", …

class InteractionRead(SQLModel):
    id: int
    user_id: int
    video_id: int
    action: str
    timestamp: datetime
    class Config:
        from_attributes = True
