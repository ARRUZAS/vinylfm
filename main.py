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

@app.get("/api/soundcloud")
async def soundcloud_search(q: str):
    # SoundCloud oEmbed lookup
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://soundcloud.com/oembed",
            params={"url": f"https://soundcloud.com/search?q={q}", "format": "json"},
            follow_redirects=True
        )
        if r.status_code == 200:
            return r.json()
        return {"error": "not found"}
