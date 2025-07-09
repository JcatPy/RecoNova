from fastapi import FastAPI, Depends
from .database import create_db_and_tables
from .database import get_session
from sqlmodel import Session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/test")
def read_test(session: Session = Depends(get_session)):
    return {"message": "This is a test endpoint!"}