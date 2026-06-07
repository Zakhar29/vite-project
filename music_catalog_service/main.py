from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.api.routes import (
    album_create,
    get_music,
    social,
    track_search,
    album_search,
    get_dirs_lists
)
from src.db.postgres_engine import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Music Catalog Service", lifespan=lifespan)
app.include_router(album_create.router)
app.include_router(get_music.router)
app.include_router(social.router)
app.include_router(track_search.router)
app.include_router(album_search.router)
app.include_router(get_dirs_lists.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "music_catalog_service"}
