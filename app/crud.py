# app/crud.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from .models import User, Video , Interaction, ActionEnum
from .schemas import UserCreate, VideoCreate
from .utils import hash_password


# ======================
# Users
# ======================

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    return db.exec(stmt).first()

def list_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    stmt = select(User).offset(skip).limit(limit)
    return db.exec(stmt).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ======================
# Videos
# ======================

def get_video_by_id(db: Session, video_id: int) -> Optional[Video]:
    return db.get(Video, video_id)

def get_video_by_pixabay_id(db: Session, px_id: int) -> Optional[Video]:
    stmt = select(Video).where(Video.pixabay_id == px_id)
    return db.exec(stmt).first()

def list_videos(db: Session, skip: int = 0, limit: int = 20) -> List[Video]:
    stmt = (
        select(Video)
        .order_by(Video.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.exec(stmt).all()

def create_or_update_video(db: Session, data: VideoCreate) -> Video:
    """
    Idempotent upsert keyed by unique pixabay_id.
    If a row exists, update metadata; otherwise insert a new one.
    """
    existing = get_video_by_pixabay_id(db, data.pixabay_id)
    if existing:
        existing.title = data.title
        existing.description = data.description
        existing.source_url = data.source_url
        existing.thumb_url = data.thumb_url
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    video = Video(
        pixabay_id=data.pixabay_id,
        title=data.title,
        description=data.description,
        source_url=data.source_url,
        thumb_url=data.thumb_url,
        uploaded_at=datetime.utcnow(),
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

def delete_video(db: Session, video_id: int) -> bool:
    video = db.get(Video, video_id)
    if not video:
        return False
    db.delete(video)
    db.commit()
    return True


# ======================
# Interactions
# ======================

def create_interaction(
    db: Session,
    *,
    user_id: int,
    video_id: int,
    action: ActionEnum,
    timestamp: Optional[datetime] = None,
) -> Interaction:
    """
    Insert a new interaction.
    Protected by a DB-level UniqueConstraint(user_id, video_id, action).
    If a duplicate insert happens, return the existing row.
    """
    inter = Interaction(
        user_id=user_id,
        video_id=video_id,
        action=action,
        timestamp=timestamp or datetime.utcnow(),
    )
    db.add(inter)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Fetch existing interaction
        stmt = select(Interaction).where(
            Interaction.user_id == user_id,
            Interaction.video_id == video_id,
            Interaction.action == action,
        )
        inter = db.exec(stmt).first()
        return inter

    db.refresh(inter)
    return inter

def get_interactions_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 50
) -> List[Interaction]:
    stmt = (
        select(Interaction)
        .where(Interaction.user_id == user_id)
        .order_by(Interaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
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
    db: Session, *, user_id: int, video_id: int, action: ActionEnum
) -> Optional[Interaction]:
    stmt = select(Interaction).where(
        Interaction.user_id == user_id,
        Interaction.video_id == video_id,
        Interaction.action == action,
    )
    return db.exec(stmt).first()
