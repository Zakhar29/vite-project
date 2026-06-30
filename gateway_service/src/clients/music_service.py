from typing import Optional
from src.clients.base import ServiceClient
from config import settings
import uuid



class MusicClient(ServiceClient):
    def __init__(self):
        super().__init__(settings.MUSIC_CATALOG_URL)

    # ========== Создание и управление ==========

    async def create_album_draft(self, title: str, type: str, cover_url: str, token: str) -> dict:
        """Создать черновик альбома"""
        payload = {"title": title, "type": type, "cover_url": cover_url}
        return await self._request("POST", "/album_create/albums", token=token, json=payload)

    async def update_album_draft(self, album_id: str, token: str, title: str = None, cover_url: str = None,
                                 type: str = None) -> dict:
        """Обновить черновик альбома"""
        payload = {}
        if title:
            payload["title"] = title
        if cover_url:
            payload["cover_url"] = cover_url
        if type:
            payload["type"] = type
        return await self._request("PATCH", f"/album_create/albums/{album_id}", token=token, json=payload)

    async def attach_audio(self, track_id: str, s3_url: str, token: str) -> dict:
        """Привязать S3 URL к треку"""
        return await self._request("PATCH", f"/album_create/tracks/{track_id}/audio", token=token,
                                   params={"s3_url": s3_url})

    async def create_and_attach_track(self, album_id: str, title: str, text: str, bpm: float, token: str,
                                      author_attention: bool = False) -> dict:
        """Создать трек и привязать к альбому"""
        payload = {
            "title": title,
            "text": text,
            "bpm": bpm,
            "author_attention": author_attention
        }
        return await self._request("POST", f"/album_create/albums/{album_id}/tracks", token=token, json=payload)

    async def attach_genres_to_track(self, track_id: str, genre_ids: list [int], token: str) -> dict:
        """Привязка жанров к треку"""
        payload = {"genre_ids": genre_ids}
        return await self._request("POST", f"/album_create/tracks/{track_id}/genres", token=token, json=payload)

    async def publish_album(self, album_id: str, token: str) -> dict:
        """Опубликовать альбом"""
        return await self._request("POST", f"/album_create/albums/{album_id}/publish", token=token)

    # ========== Публичные данные ==========

    async def get_track_full(self, track_id: str) -> dict:
        """Полная информация о треке"""
        return await self._request("GET", f"/get_music/track_full/{track_id}")

    async def get_track(self, track_id: str) -> dict:
        """Краткая информация о треке"""
        return await self._request("GET", f"/get_music/track/{track_id}")

    async def get_album(self, album_id: str) -> dict:
        """Информация об альбоме"""
        return await self._request("GET", f"/get_music/albums/{album_id}")

    async def get_user_albums(self, user_id: str) -> dict:
        """Альбомы пользователя и фиты"""
        return await self._request("GET", f"/get_music/albums/user/{user_id}")

    # ========== ПОИСК ==========

    async def search_tracks(
            self,
            query: Optional[str] = None,
            genre_ids: Optional[list [int]] = None,
            author_id: Optional[str] = None,
            bpm_min: Optional[float] = None,
            bpm_max: Optional[float] = None,
            sort_by: str = "relevance",
            sort_order: str = "desc",
            skip: int = 0,
            limit: int = 20
    ) -> dict:
        """Поиск треков с фильтрацией"""
        params = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "skip": skip,
            "limit": limit
        }
        if query:
            params["query"] = query
        if genre_ids:
            params["genre_ids"] = ",".join(str(g) for g in genre_ids)
        if author_id:
            params["author_id"] = author_id
        if bpm_min:
            params["bpm_min"] = bpm_min
        if bpm_max:
            params["bpm_max"] = bpm_max

        return await self._request("GET", "/tracks/search", params=params)

    async def search_albums(
            self,
            query: Optional[str] = None,
            genre_ids: Optional[list[int]] = None,
            author_id: Optional[str] = None,
            album_type: Optional[int] = None,
            published_after: Optional[str] = None,
            published_before: Optional[str] = None,
            sort_by: str = "relevance",
            sort_order: str = "desc",
            skip: int = 0,
            limit: int = 20
    ) -> dict:
        """Поиск альбомов с фильтрацией"""
        params = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "skip": skip,
            "limit": limit
        }
        if query:
            params["query"] = query
        if genre_ids:
            params["genre_ids"] = ",".join(str(g) for g in genre_ids)
        if author_id:
            params["author_id"] = author_id
        if album_type:
            params["album_type"] = album_type
        if published_after:
            params["published_after"] = published_after
        if published_before:
            params["published_before"] = published_before

        return await self._request("GET", "/albums/search", params=params)

    # ========== РЕКОМЕНДАЦИИ ==========

    async def get_track_recommendations(
            self,
            user_id: Optional[uuid.UUID] = None,
            limit: int = 20
    ) -> dict:
        """
        Получение рекомендаций треков.
        Если user_id указан — персонализированные рекомендации.
        Если нет — глобальные.
        """
        params = {"limit": limit}
        if user_id:
            params["user_id"] = str(user_id)  # Преобразуем UUID в строку

        return await self._request("GET", "/tracks/recommendations", params=params)

    async def get_album_recommendations(
            self,
            user_id: Optional[uuid.UUID] = None,
            limit: int = 20
    ) -> dict:
        """
        Получение рекомендаций альбомов.
        Если user_id указан — персонализированные рекомендации.
        Если нет — глобальные.
        """
        params = {"limit": limit}
        if user_id:
            params["user_id"] = str(user_id)  # Преобразуем UUID в строку

        return await self._request("GET", "/albums/recommendations", params=params)

    # ========== ПОХОЖИЕ ТРЕКИ/АЛЬБОМЫ ==========

    async def get_similar_tracks(self, track_id: str, limit: int = 10) -> dict:
        """Получение треков, похожих на указанный"""
        return await self._request("GET", f"/tracks/{track_id}/similar", params={"limit": limit})

    async def get_similar_albums(self, album_id: str, limit: int = 10) -> dict:
        """Получение альбомов, похожих на указанный"""
        return await self._request("GET", f"/albums/{album_id}/similar", params={"limit": limit})

    # ========== Счётчики (внутренние) ==========

    async def inc_track_comments(self, track_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/tracks/{track_id}/inc-comments", token=token)

    async def dec_track_comments(self, track_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/tracks/{track_id}/dec-comments", token=token)

    async def inc_album_comments(self, album_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/albums/{album_id}/inc-comments", token=token)

    async def dec_album_comments(self, album_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/albums/{album_id}/dec-comments", token=token)

    async def inc_track_likes(self, track_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/tracks/{track_id}/inc-likes", token=token)

    async def dec_track_likes(self, track_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/tracks/{track_id}/dec-likes", token=token)

    async def inc_album_likes(self, album_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/albums/{album_id}/inc-likes", token=token)

    async def dec_album_likes(self, album_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/albums/{album_id}/dec-likes", token=token)

    async def inc_track_listening(self, track_id: str) -> dict:
        return await self._request("PATCH", f"/music/tracks/{track_id}/inc-listening")

    async def inc_album_listening(self, album_id: str) -> dict:
        return await self._request("PATCH", f"/music/albums/{album_id}/inc-listening")

    async def album_follow(self, album_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/albums/{album_id}/follow", token=token)

    async def album_unfollow(self, album_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/music/albums/{album_id}/unfollow", token=token)

    # ========== Справочники ==========

    async def get_genres(self) -> dict:
        return await self._request("GET", "/get_dirs_lists/genres")

    async def get_album_types(self) -> dict:
        return await self._request("GET", "/get_dirs_lists/album_types")
