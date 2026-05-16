from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os

app = FastAPI()

DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN", "")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r") as f:
        return f.read()

@app.get("/api/collection/{username}")
async def get_collection(username: str, page: int = 1):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"https://api.discogs.com/users/{username}/collection/folders/0/releases",
            params={"page": page, "per_page": 100, "token": DISCOGS_TOKEN},
            headers={"User-Agent": "VinylFM/1.0 +https://github.com/arruzas"}
        )
        data = r.json()
        if "pagination" not in data:
            return {
                "pagination": {"pages": 1, "page": 1, "items": 0},
                "releases": [],
                "debug": data
            }
        return data

@app.get("/api/tracklist/{release_id}")
async def get_tracklist(release_id: int):
    """Haal de tracklist en YouTube videos op van een Discogs release."""
    import re
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"https://api.discogs.com/releases/{release_id}",
            params={"token": DISCOGS_TOKEN},
            headers={"User-Agent": "VinylFM/1.0 +https://github.com/arruzas"}
        )
        data = r.json()

        # Haal YouTube video IDs op uit de videos sectie
        videos = []
        for v in data.get("videos", []):
            uri = v.get("uri", "")
            title = v.get("title", "")
            match = re.search(r"(?:v=|youtu\\.be/)([a-zA-Z0-9_-]{11})", uri)
            if match:
                videos.append({
                    "videoId": match.group(1),
                    "title": title,
                    "uri": uri
                })

        tracks = []
        for i, t in enumerate(data.get("tracklist", [])):
            if t.get("type_") == "track" and t.get("title"):
                # Koppel video aan track op basis van volgorde
                video = videos[i] if i < len(videos) else None
                tracks.append({
                    "title": t["title"],
                    "duration": t.get("duration", ""),
                    "position": t.get("position", ""),
                    "videoId": video["videoId"] if video else None,
                    "videoTitle": video["title"] if video else None
                })

        return {
            "tracks": tracks,
            "videos": videos,
            "release_id": release_id
        }

@app.get("/api/ytsearch")
async def youtube_search(q: str):
    """Zoek een YouTube video ID via de YouTube suggestie API (geen key nodig)."""
    import re
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        # YouTube geeft video IDs terug in de initiële HTML
        r = await client.get(
            "https://www.youtube.com/results",
            params={"search_query": q, "sp": "EgIQAQ%3D%3D"},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8"
            }
        )
        # Zoek video IDs in de HTML response
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
        if video_ids:
            return {"videoId": video_ids[0], "query": q}
        return {"videoId": None, "query": q}

@app.get("/api/soundcloud")
async def soundcloud_search(q: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://soundcloud.com/oembed",
            params={"url": f"https://soundcloud.com/search?q={q}", "format": "json"},
            follow_redirects=True
        )
        if r.status_code == 200:
            return r.json()
        return {"error": "not found"}
