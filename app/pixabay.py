import time, math, requests
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Session, create_engine, select
from .models import Video
from .database import engine


API_KEY = '51420264-ec5b2faae87adadaebb8986bd'

BASE_URL     = "https://pixabay.com/api/videos/"
PER_PAGE     = 200
CATEGORIES   = ["nature", "animals", "technology", "sports", "people", "travel", "music"]
MAX_CLIPS    = 5000
MAX_BYTES    = 5 * 1024**3
SLEEP_SECS   = 1

def get_page(category: str, page: int):
    params = {
        "key": API_KEY,
        "category": category,
        "per_page": PER_PAGE,
        "page": page,
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["hits"], r.json()["totalHits"]

def tiny_to_video(hit: dict, category: str) -> tuple[Video, int]:
    tiny  = hit["videos"]["tiny"]
    size  = tiny["size"]          # bytes
    video = Video(
        pixabay_id = hit["id"],
        title = f"{category}-{hit['id']}",
        description  = hit["tags"],
        url = tiny["url"]
    )
    return video, size

def ingest():
    total_clips = 0
    total_bytes = 0

    with Session(engine) as session:
        for cat in CATEGORIES:
            page = 1
            while total_clips < MAX_CLIPS and total_bytes < MAX_BYTES:
                hits, total_hits = get_page(cat, page)
                if not hits:
                    break

                for hit in hits:
                    if session.exec(
                            select(Video.id).where(Video.pixabay_id == hit["id"])
                    ).first():
                        continue

                    video, size = tiny_to_video(hit, cat)

                    if (total_clips + 1) > MAX_CLIPS or (total_bytes + size) > MAX_BYTES:
                        session.commit()
                        return

                    session.add(video)
                    total_clips += 1
                    total_bytes += size

                session.commit()

                max_pages = math.ceil(total_hits/ PER_PAGE)
                if page >= max_pages:
                    break

                page += 1
                time.sleep(SLEEP_SECS)

                if total_clips >= MAX_CLIPS or total_bytes >= MAX_BYTES:
                    break

    print(f"stored {total_clips} clips  |  {total_bytes/1024/1024:.1f} MB")


if __name__ == "__main__":
    ingest()
