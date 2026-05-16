# VINYL.FM 深夜放送

Underground radiostation gebaseerd op je Discogs collectie.

## Deploy op Railway

### 1. GitHub repo aanmaken
- Ga naar github.com → New repository → naam: `vinylfm`
- Upload alle bestanden: `main.py`, `index.html`, `requirements.txt`, `Procfile`, `nixpacks.toml`

### 2. Railway project aanmaken
- Ga naar railway.app → New Project → Deploy from GitHub repo
- Selecteer je `vinylfm` repo

### 3. Environment variable instellen
- In Railway: ga naar je service → Variables
- Voeg toe: `DISCOGS_TOKEN` = jouw Discogs API token

### 4. Klaar
- Railway geeft je een URL zoals `vinylfm-production.up.railway.app`
- Open die URL, vul je gebruikersnaam in, druk op start

## Lokaal testen
```
pip install fastapi uvicorn httpx
export DISCOGS_TOKEN=jouw_token_hier
uvicorn main:app --reload
```
Open dan http://localhost:8000
