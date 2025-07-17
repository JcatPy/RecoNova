from fastapi import Depends, HTTPException, status
from .models import User
from .oauth2 import oauth2_scheme, verify_access_token
from .database import get_session
from sqlmodel import Session

def get_current_user(token: str= Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    user = session.get(User, token_data.id)
    return user if user else None

def require_admin(current = Depends(get_current_user)):
    if not current.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin only.")
    return current

def ensure_self_or_admin(
    user_id: int,
    current = Depends(get_current_user)
):
    if current.is_admin or current.id == user_id:
        return current
    raise HTTPException(403, "Not allowed")
