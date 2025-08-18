# app/routers/videos.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session
from app.database import get_session
from ..schemas import VideoCreate, VideoRead
from ..crud import create_or_update_video, get_video_by_id, delete_video, list_videos
from ..deps import require_admin

router = APIRouter(tags=["videos"])

@router.post("/videos", response_model=VideoRead, status_code=status.HTTP_201_CREATED)
def upload_video(
    data: VideoCreate,
    _admin = Depends(require_admin),
    db: Session = Depends(get_session),
):
    """
    Admin-only upsert by pixabay_id.
    Stores local URLs (source_url, thumb_url) that your server will serve under /media/*.
    """
    return create_or_update_video(db, data)

@router.get("/videos", response_model=List[VideoRead])
def browse_videos(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_session),
):
    return list_videos(db, skip, limit)

@router.get("/videos/{video_id}", response_model=VideoRead)
def fetch_video(video_id: int, db: Session = Depends(get_session)):
    video = get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_video(
    video_id: int,
    _admin = Depends(require_admin),
    db: Session = Depends(get_session),
):
    ok = delete_video(db, video_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Video not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
