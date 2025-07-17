from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from ..schemas import InteractionCreate, InteractionRead
from ..crud import create_interaction, get_interactions_by_user, list_interactions_by_video, get_interaction
from ..deps import require_admin, ensure_self_or_admin, get_current_user

router = APIRouter(tags=["interactions"])

@router.post("/interactions", status_code=201,
             response_model=InteractionRead)
def add_interaction(data: InteractionCreate,
                    current_user = Depends(get_current_user),
                    db: Session = Depends(get_session)):
    # prevent duplicate like/watch rows
    existing = get_interaction(
        db,
        user_id=current_user.id,
        video_id=data.video_id,
        action=data.action,
    )
    if existing:
        return existing

    inter = create_interaction(
        db,
        user_id = current_user.id,
        video_id = data.video_id,
        action   = data.action,
    )
    return inter

@router.get("/users/{user_id}/interactions",
            response_model=List[InteractionRead])
def user_history(user_id: int,
                 _ = Depends(ensure_self_or_admin),
                 db: Session = Depends(get_session)):
    return get_interactions_by_user(db, user_id)


@router.get("/videos/{video_id}/interactions",
            response_model=List[InteractionRead])
def video_events(video_id: int,
                 _admin = Depends(require_admin),
                 db: Session = Depends(get_session)):
    return list_interactions_by_video(db, video_id)





