from sqlmodel import SQLModel, Field, Relationship
from typing   import Optional, List
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"

    id:   Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_admin: bool = Field(default=False)

    interactions: List["Interaction"] = Relationship(back_populates="user")

    class Config:
        from_attributes = True



class Video(SQLModel, table=True):
    id:   Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    url: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    interactions: List["Interaction"] = Relationship(back_populates="video")

    class Config:
        from_attributes = True



class Interaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id:  int = Field(foreign_key="users.id")
    video_id: int = Field(foreign_key="video.id")

    action: str                                # "watch", "like", "complete"…
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # back-refs (many-to-one)
    user:  Optional[User]  = Relationship(back_populates="interactions")
    video: Optional[Video] = Relationship(back_populates="interactions")
