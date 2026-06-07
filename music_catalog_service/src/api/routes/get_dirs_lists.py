# src/api/routes/get_music.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.db.postgres_engine import get_db
from src.models.albums_models import AlbumTypes
from src.models.tracks_models import Genres

# ... ваши импорты ...

router = APIRouter(prefix="/get_dirs_lists", tags=["Public Music"])


@router.get("/genres")
async def get_genres(
        db: AsyncSession = Depends(get_db)
):
    genres = await db.execute(select(Genres)).scalars().all()

    if not genres_select:
        raise HTTPException(404, "Genres not found")

    return {
        [
            {
                "genre_id": genres.id,
                "title": genres.title
            }
        ]
    }

@router.get("/album_types")
async def get_album_types(
        db: AsyncSession = Depends(get_db)
):
    types = await db.execute(select(AlbumTypes)).scalars().all()

    if not genres_select:
        raise HTTPException(404, "Genres not found")

    return {
        [
            {
                "type_id": types.id,
                "title": types.title
            }
        ]
    }



