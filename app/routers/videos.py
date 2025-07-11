from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from ..schemas import VideoCreate, VideoRead
from ..crud import create_video, get_video_by_id, delete_video, list_videos

router = APIRouter(tags=["api"])

@router.post("/videos", response_model=VideoRead, status_code=201)
def upload_video(
    data: VideoCreate,
    db: Session = Depends(get_session),
):
    return create_video(
        db, title=data.title, url=data.url, description=data.description
    )

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
        raise HTTPException(404, "Video not found")
    return video

@router.delete("/videos/{video_id}", status_code=204)
def remove_video(video_id: int, db: Session = Depends(get_session)):
    if not delete_video(db, video_id):
        raise HTTPException(404, "Video not found")
    return {"detail": "Video deleted successfully"}




