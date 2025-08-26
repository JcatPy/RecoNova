import time
import argparse
from pathlib import Path
from typing import Iterable, Tuple, Optional

import requests
from sqlmodel import Session
from app.database import engine
from app.schemas import VideoCreate
from app.crud import create_or_update_video
import math
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# one shared session with retries (handles 429/5xx gracefully)
_session = requests.Session()
_adapter = HTTPAdapter(max_retries=Retry(
    total=3, backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504)
))
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

MEDIA_ROOT = Path("/var/app/media")
THUMBS_DIR = MEDIA_ROOT / "thumbs"
CLIPS_DIR  = MEDIA_ROOT / "clips"

PIXABAY_API_KEY = '51420264-ec5b2faae87adadaebb8986bd'

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

# NEW: pick clip + thumb together from the smallest reasonable rendition
def choose_clip_and_thumb(videos_obj: dict) -> Tuple[str, Optional[str]]:
    """
    Return (clip_url, thumb_url) preferring tiny→small→medium→large.
    Some responses may omit 'thumbnail'; caller should handle None.
    """
    first_thumb = None
    # capture any thumbnail we see while scanning, to use as fallback
    for d in videos_obj.values():
        if isinstance(d, dict) and d.get("thumbnail") and not first_thumb:
            first_thumb = d["thumbnail"]

    for key in ("tiny", "small", "medium", "large"):
        data = videos_obj.get(key)
        if data and data.get("url"):
            clip = data["url"]
            thumb = data.get("thumbnail") or first_thumb
            return clip, thumb

    raise ValueError("No usable video URL in Pixabay response")

# OPTIONAL: last-resort builder if API lacks thumbnail but has picture_id
def build_thumb_from_picture_id(hit: dict, w: int = 640, h: int = 360) -> Optional[str]:
    pid = hit.get("picture_id")
    if pid:
        # standard Vimeo CDN pattern used by Pixabay video thumbs
        return f"https://i.vimeocdn.com/video/{pid}_{w}x{h}.jpg"
    return None

def _respect_rate_limit(resp):
    # Pixabay returns these (case-insensitive)
    try:
        remaining = int(resp.headers.get("X-RateLimit-Remaining", "100"))
        reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
    except ValueError:
        return
    if remaining <= 1:
        # sleep until the window resets (plus a tiny buffer)
        time.sleep(reset + 1)


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
    _respect_rate_limit(r)
    return r.json()

def iterate_hits(query: str, pages: int, per_page: int) -> Iterable[dict]:
    first = fetch_pixabay_page(query, 1, per_page)
    for hit in first.get("hits", []):
        yield hit

    # API exposes totalHits but returns max 500 per query → don’t over-fetch
    total_hits = min(int(first.get("totalHits", 0)), 500)
    pages_total = max(1, math.ceil(total_hits / per_page))
    pages_to_fetch = min(pages, pages_total)

    for p in range(2, pages_to_fetch + 1):
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

            # UPDATED: get clip & thumb from video renditions (not previewURL)
            clip_remote, thumb_remote = choose_clip_and_thumb(hit["videos"])
            if not thumb_remote:
                # fallback to previewURL if present, else build from picture_id
                thumb_remote = hit.get("previewURL") or build_thumb_from_picture_id(hit)

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
            local_thumb_url = f"/media/thumbs/{thumb_name}" if thumb_remote else None
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
