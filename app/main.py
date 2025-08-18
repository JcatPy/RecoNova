from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import videos, user, auth, interactions
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Where media will live on the EC2 instance (root EBS is fine to start)
MEDIA_ROOT = Path("/var/app/media")
THUMBS_DIR = MEDIA_ROOT / "thumbs"
CLIPS_DIR  = MEDIA_ROOT / "clips"

# Ensure folders exist
for p in (THUMBS_DIR, CLIPS_DIR):
    p.mkdir(parents=True, exist_ok=True)


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT)), name="media")

app.include_router(videos.router)
app.include_router(user.router)
app.include_router(interactions.router)
app.include_router(auth.router)


