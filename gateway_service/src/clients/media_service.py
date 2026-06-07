from fastapi import UploadFile
from src.clients.base import ServiceClient
from config import settings


class MediaClient(ServiceClient):
    def __init__(self):
        super().__init__(settings.MEDIA_SERVICE_URL)

    async def upload_avatar(self, file: UploadFile, token: str, replace: bool = True) -> dict:
        """Загрузить аватарку"""
        files = [("file", (file.filename, await file.read(), file.content_type))]
        data = [("replace", str(replace).lower())]
        return await self._request("POST", "/avatar", token=token, files=files, data=data)

    async def delete_avatar(self, token: str, sizes: list[str] = None) -> dict:
        """Удалить аватарку"""
        if sizes is None:
            sizes = ["small", "medium", "large"]
        return await self._request("DELETE", "/avatar", token=token, params={"sizes": sizes})

    async def upload_album_cover(self, album_id: str, file: UploadFile) -> dict:
        """Загрузить обложку альбома"""
        files = [("file", (file.filename, await file.read(), file.content_type))]
        return await self._request("POST", f"/cover/{album_id}", files=files)

    async def delete_album_cover(self, album_id: str, sizes: list[str] = None) -> dict:
        """Удалить обложку альбома"""
        if sizes is None:
            sizes = ["small", "medium", "large"]
        return await self._request("DELETE", f"/cover/{album_id}", params={"sizes": sizes})

    async def upload_post_image(self, post_id: str, file: UploadFile) -> dict:
        """Загрузить изображение в пост"""
        files = [("file", (file.filename, await file.read(), file.content_type))]
        return await self._request("POST", f"/media/{post_id}/image", files=files)

    async def upload_post_video(self, post_id: str, file: UploadFile, quality: str = "1080p") -> dict:
        """Загрузить видео в пост"""
        files = [("file", (file.filename, await file.read(), file.content_type))]
        data = [("quality", quality)]
        return await self._request("POST", f"/media/{post_id}/video", files=files, data=data)

    async def delete_post_media(self, post_id: str, media_keys: list[str]) -> dict:
        """Удалить медиа из поста"""
        return await self._request("DELETE", f"/media/{post_id}", params={"media_keys": media_keys})

    async def upload_track(self, album_id: str, track_number: int, file: UploadFile) -> dict:
        """Загрузить трек"""
        files = [("file", (file.filename, await file.read(), file.content_type))]
        return await self._request("POST", f"/track/{album_id}/{track_number}", files=files)

    async def delete_track(self, album_id: str, track_number: int) -> dict:
        """Удалить трек"""
        return await self._request("DELETE", f"/track/{album_id}/{track_number}")