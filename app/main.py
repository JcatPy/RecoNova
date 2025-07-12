from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import videos, user, auth, interactions


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(videos.router)
app.include_router(user.router)
app.include_router(interactions.router)


