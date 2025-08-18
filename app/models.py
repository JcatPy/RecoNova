from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum as SAEnum, UniqueConstraint, Index, ForeignKey


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_admin: bool = Field(default=False)

    # relationships
    interactions: List["Interaction"] = Relationship(back_populates="user")

    class Config:
        from_attributes = True


class Video(SQLModel, table=True):
    __tablename__ = "video"  # keep in sync with foreign_key targets

    id: Optional[int] = Field(default=None, primary_key=True)
    pixabay_id: int = Field(unique=True, index=True)
    title: str
    description: Optional[str] = None

    # These are LOCAL URLs you’ll serve from FastAPI/Nginx (e.g., /media/thumbs/123.jpg)
    source_url: str = Field(index=True)
    thumb_url: Optional[str] = None

    uploaded_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # relationships
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

    # One row per (user, video, action). If you need counts of repeated views,
    # we’ll store them as separate rows later or add a counter column.
    __table_args__ = (
        UniqueConstraint("user_id", "video_id", "action", name="uq_user_video_action"),
        Index("ix_interactions_video_action", "video_id", "action"),
        Index("ix_interactions_user_ts", "user_id", "timestamp"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    # ON DELETE CASCADE to keep data tidy when a user or video is removed
    user_id: int = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    video_id: int = Field(
        sa_column=Column(
            ForeignKey("video.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    action: ActionEnum = Field(
        sa_column=Column(
            SAEnum(ActionEnum, name="action_enum"),
            nullable=False,
        )
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # back-refs (many-to-one)
    user: Optional[User] = Relationship(back_populates="interactions")
    video: Optional[Video] = Relationship(back_populates="interactions")

    class Config:
        from_attributes = True
