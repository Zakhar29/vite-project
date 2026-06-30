from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    status,
    Request
)
from typing import List, Optional
from pydantic import BaseModel
import json

from src.api.dependencies import (
    get_current_user,
    CurrentUser,
    get_users_client,
    get_music_client,
    get_media_client
)
from src.clients.media_service import MediaClient
from src.clients.music_service import MusicClient
from src.api.schemas import TrackItem

router = APIRouter(prefix="/new_album", tags=["Album Creation"])


@router.get("/create-form-data")
async def get_album_create_form_data(
        music_client: MusicClient = Depends(get_music_client)
):
    """
    Получение данных для страницы создания альбома:
    - список типов альбомов
    - список жанров
    """

    # Получаем список типов альбомов
    album_types = await music_client.get_album_types()

    # Получаем список жанров
    genres = await music_client.get_genres()

    return {
        "album_types": album_types.get("items", []),
        "genres": genres.get("items", [])
    }


# ========== POST: СОЗДАНИЕ АЛЬБОМА ==========

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_album(
        request: Request,
        current_user: CurrentUser = Depends(get_current_user),
        media_client: MediaClient = Depends(get_media_client),
        music_client: MusicClient = Depends(get_music_client)
):
    """
    Создание альбома с треками.

    Ожидает multipart/form-data с полями:
    - title: string
    - type: int (1-album, 2-single, 3-ep)
    - cover: file
    - tracks_count: int
    - track_0_title: string
    - track_0_bpm: float
    - track_0_genres: string (JSON массив, например "[1,2,3]")
    - track_0_text: string (опционально)
    - track_0_author_attention: boolean (опционально)
    - track_0_file: file
    - track_1_... и т.д.
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")

    # ========== 1. ПАРСИМ FORM DATA ==========
    form_data = await request.form()

    # Основные поля
    title = form_data.get("title")
    album_type = form_data.get("type")
    cover_file = form_data.get("cover")
    tracks_count_str = form_data.get("tracks_count")

    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    if not album_type:
        raise HTTPException(status_code=400, detail="type is required")
    if not cover_file:
        raise HTTPException(status_code=400, detail="cover is required")
    if not tracks_count_str:
        raise HTTPException(status_code=400, detail="tracks_count is required")

    try:
        album_type = int(album_type)
        tracks_count = int(tracks_count_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="type and tracks_count must be integers")

    if tracks_count < 1 or tracks_count > 50:
        raise HTTPException(status_code=400, detail="tracks_count must be between 1 and 50")

    # ========== 2. ПАРСИМ ТРЕКИ ==========
    tracks = []

    for i in range(tracks_count):
        track_title = form_data.get(f"track_{i}_title")
        track_bpm_str = form_data.get(f"track_{i}_bpm")
        track_genres_str = form_data.get(f"track_{i}_genres", "[]")
        track_text = form_data.get(f"track_{i}_text", "")
        track_author_attention = form_data.get(f"track_{i}_author_attention", "false")
        track_file = form_data.get(f"track_{i}_file")

        if not track_title:
            raise HTTPException(status_code=400, detail=f"track_{i}_title is required")
        if not track_bpm_str:
            raise HTTPException(status_code=400, detail=f"track_{i}_bpm is required")
        if not track_file:
            raise HTTPException(status_code=400, detail=f"track_{i}_file is required")

        try:
            track_bpm = float(track_bpm_str)
            track_genres = json.loads(track_genres_str)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"track_{i}_bpm must be a number")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail=f"track_{i}_genres must be a valid JSON array")

        if not isinstance(track_genres, list):
            raise HTTPException(status_code=400, detail=f"track_{i}_genres must be an array")

        tracks.append({
            "title": track_title,
            "bpm": track_bpm,
            "genres": track_genres,
            "text": track_text,
            "author_attention": track_author_attention.lower() == "true",
            "file": track_file
        })

    # ========== 3. СОЗДАНИЕ ЧЕРНОВИКА АЛЬБОМА (без обложки) ==========
    try:
        album_result = await music_client.create_album_draft(
            title=title,
            type=str(album_type),
            cover_url="",  # пока без обложки
            token=token
        )
        album_id = album_result.get("id")
        if not album_id:
            raise ValueError("Album ID not returned")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create album draft: {str(e)}"
        )

    # ========== 4. ЗАГРУЗКА ОБЛОЖКИ С РЕАЛЬНЫМ ALBUM_ID ==========
    try:
        cover_result = await media_client.upload_album_cover(
            album_id=album_id,  # ← используем реальный ID альбома
            file=cover_file
        )

        # Извлекаем URL большой обложки (cover_large)
        cover_url = ""
        if isinstance(cover_result, list):
            for item in cover_result:
                if "large" in item.get("key", "") or "cover_large" in item.get("key", ""):
                    cover_url = item.get("url", "")
                    break
        elif isinstance(cover_result, dict):
            if "media" in cover_result and isinstance(cover_result["media"], list):
                for item in cover_result["media"]:
                    if "large" in item.get("key", "") or "cover_large" in item.get("key", ""):
                        cover_url = item.get("url", "")
                        break
            elif "url" in cover_result:
                cover_url = cover_result["url"]

        # Если не нашли large, берём первый попавшийся
        if not cover_url and isinstance(cover_result, list) and cover_result:
            cover_url = cover_result[0].get("url", "")
        elif not cover_url and isinstance(cover_result, dict) and cover_result.get("media"):
            cover_url = cover_result["media"][0].get("url", "")

        if not cover_url:
            raise HTTPException(500, "Failed to get cover URL from media service")

        # Обновляем альбом с URL обложки
        await music_client.update_album_draft(
            album_id=album_id,
            token=token,
            cover_url=cover_url
        )

    except Exception as e:
        # Если загрузка обложки не удалась, удаляем черновик альбома
        try:
            await music_client.delete_album_draft(album_id, token=token)
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload cover: {str(e)}"
        )

    # ========== 5. СОЗДАНИЕ ТРЕКОВ В ЦИКЛЕ ==========
    created_tracks = []

    for idx, track in enumerate(tracks, start=1):
        track_id = None
        try:
            # 5a. Создание трека и привязка к альбому (без audio_url)
            track_result = await music_client.create_and_attach_track(
                album_id=album_id,
                title=track["title"],
                text=track["text"],
                bpm=track["bpm"],
                token=token,
                author_attention=track["author_attention"]
            )
            track_id = track_result.get("track_id")
            track_number = track_result.get("number", idx)

            if not track_id:
                raise ValueError("Track ID not returned")

            # 5b. Загрузка аудиофайла в S3
            audio_result = await media_client.upload_track(
                album_id=album_id,
                track_number=track_number,
                file=track["file"]
            )

            # Извлекаем URL аудио
            audio_url = ""
            if isinstance(audio_result, dict):
                if "media" in audio_result and audio_result["media"]:
                    audio_url = audio_result["media"][0].get("url", "")
                elif "url" in audio_result:
                    audio_url = audio_result["url"]
            elif isinstance(audio_result, list) and audio_result:
                audio_url = audio_result[0].get("url", "")

            if not audio_url:
                raise ValueError("Failed to get audio URL")

            # 5c. Привязка аудио к треку
            await music_client.attach_audio(
                track_id=track_id,
                s3_url=audio_url,
                token=token
            )

            # 5d. Привязка жанров к треку
            if track["genres"]:
                await music_client.attach_genres_to_track(
                    track_id=track_id,
                    genre_ids=track["genres"],
                    token=token
                )

            created_tracks.append({
                "track_id": track_id,
                "number": track_number,
                "title": track["title"],
                "genres": track["genres"]
            })

        except Exception as e:
            # При ошибке удаляем черновик альбома
            try:
                await music_client.delete_album_draft(album_id, token=token)
            except Exception:
                pass

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create track {track['title']}: {str(e)}"
            )

    # ========== 6. ПУБЛИКАЦИЯ АЛЬБОМА ==========
    try:
        publish_result = await music_client.publish_album(
            album_id=album_id,
            token=token
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish album: {str(e)}"
        )

    return {
        "message": "Album created and published successfully",
        "album_id": album_id,
        "title": title,
        "cover_url": cover_url,
        "tracks_count": len(created_tracks),
        "tracks": created_tracks
    }