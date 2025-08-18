from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum

class ActionEnum(str, Enum):
    view = "view"
    like = "like"
    complete = "complete"
    bookmark = "bookmark"
    share = "share"


# -------------------
# Auth / Tokens
# -------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


# -------------------
# Users
# -------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool = False

    class Config:
        from_attributes = True  # Pydantic v2: ORM mode


# -------------------
# Videos
# -------------------
class VideoCreate(BaseModel):
    pixabay_id: int
    title: str
    description: Optional[str] = None
    source_url: str                 # e.g., "/media/clips/12345.mp4"
    thumb_url: Optional[str] = None # e.g., "/media/thumbs/12345.jpg"

class VideoRead(VideoCreate):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# -------------------
# Interactions
# -------------------
class InteractionCreate(BaseModel):
    video_id: int
    action: ActionEnum              # safer than raw str

class InteractionRead(BaseModel):
    id: int
    user_id: int
    video_id: int
    action: ActionEnum
    timestamp: datetime

    class Config:
        from_attributes = True
