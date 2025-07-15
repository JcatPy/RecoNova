from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, col
from .models import User, Video, Interaction
from .schemas import UserCreate
from .utils import hash_password


'''-----------Helper functions for CRUD operations on User, Video, and Interaction models-----------'''

# User helper functions
def get_user_by_id(db: Session, user_id:int ) -> Optional[User]:
    """Retrieve a user by their ID."""
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by their email."""
    stmt = select(User).where(User.email == email)
    return db.exec(stmt).first()

def list_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    """List all users with pagination."""
    stmt = select(User).offset(skip).limit(limit)
    return db.exec(stmt).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)  # Assuming password is hashed before passing
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Video helper functions
def create_video(db: Session, title: str, url: str, description: Optional[str] = None, uploaded_at: Optional[datetime] = None) -> Video:
    """Create a new video."""
    video = Video(title=title, url=url, description=description, uploaded_at=uploaded_at or datetime.utcnow())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

def get_video_by_id(db: Session, video_id: int) -> Optional[Video]:
    """Retrieve a video by its ID."""
    return db.get(Video, video_id)

def list_videos(db: Session, skip: int = 0, limit: int = 20) -> List[Video]:
    """List all videos with pagination."""
    stmt = select(Video).order_by(col(Video.uploaded_at).desc()).offset(skip).limit(limit)
    return db.exec(stmt).all()

def delete_video(db: Session, video_id: int) -> bool:
    video = db.get(Video, video_id)
    if not video:
        return False
    db.delete(video)
    db.commit()
    return True

# Interaction helper functions
def create_interaction(db: Session, user_id: int, video_id: int, action: str, timestamp: Optional[datetime] = None) -> Interaction:
    """Create a new interaction (like, watch, etc.) between a user and a video."""
    interaction = Interaction(user_id=user_id, video_id=video_id, action=action, timestamp=timestamp or datetime.utcnow())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction

def get_interactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Interaction]:
    """List all interactions for a specific user."""
    stmt = (select(Interaction)
            .where(Interaction.user_id == user_id)
            .order_by(Interaction.timestamp.desc())
            .offset(skip).limit(limit)
    )
    return db.exec(stmt).all()

def list_interactions_by_video(
    db: Session, video_id: int, limit: int = 50
) -> List[Interaction]:
    stmt = (
        select(Interaction)
        .where(Interaction.video_id == video_id)
        .order_by(Interaction.timestamp.desc())
        .limit(limit)
    )
    return db.exec(stmt).all()

def get_interaction(
    db: Session, *, user_id: int, video_id: int, action: str
) -> Optional[Interaction]:
    """Quick lookup: did this user already like/watch this video?"""
    stmt = (
        select(Interaction)
        .where(
            Interaction.user_id == user_id,
            Interaction.video_id == video_id,
            Interaction.action == action,
        )
    )
    return db.exec(stmt).first()






