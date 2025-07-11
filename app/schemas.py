from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from pydantic import EmailStr, BaseModel
from pydantic import conint


class UserCreate(SQLModel):
    email: str
    password: str