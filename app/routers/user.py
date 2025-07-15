from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from ..schemas import UserCreate, UserOut
from ..crud import create_user, list_users, get_user_by_id, get_user_by_email

router = APIRouter(tags=["Users"])

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = create_user(db, user)
    return new_user

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