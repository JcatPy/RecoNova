import os
import time
import argparse
from pathlib import Path
from typing import Iterable

import requests
from sqlmodel import Session
from app.database import engine
from app.schemas import VideoCreate
from app.crud import create_or_update_video

MEDIA_ROOT = Path("/var/app/media")
THUMBS_DIR = MEDIA_ROOT / "thumbs"
CLIPS_DIR  = MEDIA_ROOT / "clips"

PIXABAY_API_KEY = 'getenv("PIXABAY_API_KEY", "").strip()'

def ensure_dirs():
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

def _download(url: str, dest: Path, retries: int = 3, timeout: int = 30) -> None:
    for attempt in range(retries):
        r = requests.get(url, stream=True, timeout=timeout)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return
        time.sleep(1 + attempt)
    raise RuntimeError(f"Failed to download {url} -> {dest}")

def _safe_name(px_id: int, ext: str) -> str:
    return f"{px_id}{ext}"

def choose_small_rendition(videos_obj: dict) -> str:
    # videos: { "large": {...}, "medium": {...}, "small": {...}, "tiny": {...} }
    for key in ("tiny", "small", "medium", "large"):
        if key in videos_obj and "url" in videos_obj[key]:
            return videos_obj[key]["url"]
    raise ValueError("No usable video URL in Pixabay response")

def fetch_pixabay_page(query: str, page: int, per_page: int = 20) -> dict:
    if not PIXABAY_API_KEY:
        raise RuntimeError("Set PIXABAY_API_KEY environment variable")
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "page": page,
        "per_page": per_page,
        "safesearch": "true",
        "video_type": "all",
        "lang": "en",
    }
    url = "https://pixabay.com/api/videos/"
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def iterate_hits(query: str, pages: int, per_page: int) -> Iterable[dict]:
    for p in range(1, pages + 1):
        data = fetch_pixabay_page(query, p, per_page)
        for hit in data.get("hits", []):
            yield hit

def ingest_query(query: str, pages: int = 1, per_page: int = 20) -> int:
    ensure_dirs()
    imported = 0
    with Session(engine) as db:
        for hit in iterate_hits(query, pages, per_page):
            px_id = int(hit["id"])
            title = hit.get("tags") or f"Pixabay {px_id}"
            description = f'By {hit.get("user")}' if hit.get("user") else None

            # Thumbnail: prefer previewURL
            thumb_remote = hit.get("previewURL")
            # Clip: choose the smallest reasonable rendition
            clip_remote = choose_small_rendition(hit["videos"])

            # Local filenames
            thumb_name = _safe_name(px_id, ".jpg")
            clip_name  = _safe_name(px_id, ".mp4")

            thumb_dest = THUMBS_DIR / thumb_name
            clip_dest  = CLIPS_DIR / clip_name

            # Download only if missing (idempotent)
            if thumb_remote and not thumb_dest.exists():
                _download(thumb_remote, thumb_dest)
            if clip_remote and not clip_dest.exists():
                _download(clip_remote, clip_dest)

            # Local URLs served by FastAPI/Nginx
            local_thumb_url = f"/media/thumbs/{thumb_name}"
            local_clip_url  = f"/media/clips/{clip_name}"

            payload = VideoCreate(
                pixabay_id=px_id,
                title=title,
                description=description,
                source_url=local_clip_url,
                thumb_url=local_thumb_url,
            )
            create_or_update_video(db, payload)
            imported += 1
    return imported

def main():
    parser = argparse.ArgumentParser(description="Import Pixabay videos")
    parser.add_argument("--query", required=True, help="Search term (e.g., 'nature')")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--per-page", type=int, default=20)
    args = parser.parse_args()
    n = ingest_query(args.query, args.pages, args.per_page)
    print(f"Imported/updated {n} items for query='{args.query}'")

if __name__ == "__main__":
    main()
