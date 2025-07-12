from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from ..schemas import UserCreate
from ..crud import create_user, list_users, get_user_by_id, get_user_by_email

router = APIRouter(tags=["Users"])

@router.get("/users", response_model=List[UserCreate])
def list_users(skip: int = 0, limit: int = 20,
               db: Session = Depends(get_session)):
    return list_users(db, skip, limit)


@router.get("/users/{user_id}", response_model=UserCreate)
def get_user_profile(user_id: int,
                     db: Session = Depends(get_session)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user