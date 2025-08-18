from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session
from app.database import get_session
from ..schemas import InteractionCreate, InteractionRead
from ..crud import (
    create_interaction,
    get_interactions_by_user,
    list_interactions_by_video,
    get_interaction,
    get_video_by_id,
)
from ..deps import require_admin, ensure_self_or_admin, get_current_user
from ..models import User  # for typing

router = APIRouter(tags=["interactions"])

@router.post("/interactions", response_model=InteractionRead)
def add_interaction(
    data: InteractionCreate,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    # (Optional) ensure target video exists for a clean 404
    if not get_video_by_id(db, data.video_id):
        raise HTTPException(status_code=404, detail="Video not found")

    # Fast path: return existing with 200 OK
    existing = get_interaction(
        db,
        user_id=current_user.id,
        video_id=data.video_id,
        action=data.action,
    )
    if existing:
        response.status_code = status.HTTP_200_OK
        return existing

    # Create; crud will also be safe against races via UniqueConstraint+IntegrityError
    inter = create_interaction(
        db,
        user_id=current_user.id,
        video_id=data.video_id,
        action=data.action,
    )
    response.status_code = status.HTTP_201_CREATED
    return inter


@router.get("/users/{user_id}/interactions", response_model=List[InteractionRead])
def user_history(
    user_id: int,
    action: Optional[str] = None,   # optional filter, e.g. ?action=like
    skip: int = 0,
    limit: int = 50,
    _ = Depends(ensure_self_or_admin),
    db: Session = Depends(get_session),
):
    items = get_interactions_by_user(db, user_id, skip=skip, limit=limit)
    if action:
        items = [i for i in items if i.action == action]
    return items


@router.get("/videos/{video_id}/interactions", response_model=List[InteractionRead])
def video_events(
    video_id: int,
    action: Optional[str] = None,   # optional filter
    limit: int = 50,
    _admin = Depends(require_admin),
    db: Session = Depends(get_session),
):
    items = list_interactions_by_video(db, video_id, limit=limit)
    if action:
        items = [i for i in items if i.action == action]
    return items
