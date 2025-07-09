from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    uid: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None

    interactions: List["Interaction"] = Relationship(back_populates="user")


    class Config:
        orm_mode = True


class Video(SQLModel, table=True):
    vid: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    url: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    interactions: List["Interaction"] = Relationship(back_populates="video")

    class Config:
        orm_mode = True

class Interaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.uid")
    video_id: int = Field(foreign_key="video.vid")
    action: str  # "watch", "like", etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)

Interaction.user = Relationship(back_populates="interactions")
Interaction.video = Relationship(back_populates="interactions")


