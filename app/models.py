# app/models.py
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_admin: bool = Field(default=False)

    interactions: list["Interaction"] = Relationship(back_populates="user")
    class Config:
        from_attributes = True


class Video(SQLModel, table=True):
    __tablename__ = "video"

    id: Optional[int] = Field(default=None, primary_key=True)
    pixabay_id: int = Field(unique=True, index=True)
    title: str
    description: Optional[str] = None

    # Local URLs (e.g., /media/clips/..., /media/thumbs/...)
    source_url: str = Field(index=True)
    thumb_url: Optional[str] = None

    uploaded_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    interactions: List["Interaction"] = Relationship(back_populates="video")

    class Config:
        from_attributes = True


class ActionEnum(str, Enum):
    view = "view"
    like = "like"
    complete = "complete"
    bookmark = "bookmark"
    share = "share"


class Interaction(SQLModel, table=True):
    __tablename__ = "interactions"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys only; no relationship() / Relationship()
    user_id: int = Field(foreign_key="users.id", index=True)
    video_id: int = Field(foreign_key="video.id", index=True)

    action: ActionEnum
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    user: Optional[User] = Relationship(back_populates="interactions")
    video: Optional[Video] = Relationship(back_populates="interactions")

    class Config:
        from_attributes = True
