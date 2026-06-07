from typing import Optional
from src.clients.base import ServiceClient
from config import settings


class CommentClient(ServiceClient):
    def __init__(self):
        super().__init__(settings.COMMENT_SERVICE_URL)

    # ========== Комментарии к постам ==========

    async def list_post_comments(
            self,
            post_id: str,
            root_only: bool = True,
            skip: int = 0,
            limit: int = 20,
            sort_by: str = "created_at",
            sort_order: str = "asc"
    ) -> dict:
        params = {"root_only": root_only, "skip": skip, "limit": limit, "sort_by": sort_by, "sort_order": sort_order}
        return await self._request("GET", f"/posts/{post_id}/comments", params=params)

    async def create_post_comment(self, post_id: str, comment: str, token: str) -> dict:
        return await self._request("POST", f"/posts/{post_id}/comments", token=token, json={"comment": comment})

    async def get_post_comment(self, post_id: str, comment_id: str) -> dict:
        return await self._request("GET", f"/posts/{post_id}/comments/{comment_id}")

    async def update_post_comment(self, post_id: str, comment_id: str, comment: str, token: str) -> dict:
        return await self._request("PUT", f"/posts/{post_id}/comments/{comment_id}", token=token,
                                   json={"comment": comment})

    async def delete_post_comment(self, post_id: str, comment_id: str, token: str) -> None:
        return await self._request("DELETE", f"/posts/{post_id}/comments/{comment_id}", token=token)

    # ========== Комментарии к трекам ==========

    async def list_track_comments(
            self,
            track_id: str,
            root_only: bool = True,
            skip: int = 0,
            limit: int = 20,
            timecode_from: Optional[int] = None,
            timecode_to: Optional[int] = None
    ) -> dict:
        params = {"root_only": root_only, "skip": skip, "limit": limit}
        if timecode_from:
            params["timecode_from"] = timecode_from
        if timecode_to:
            params["timecode_to"] = timecode_to
        return await self._request("GET", f"/tracks/{track_id}/comments", params=params)

    async def create_track_comment(self, track_id: str, comment: str, token: str,
                                   track_timecode: Optional[int] = None) -> dict:
        payload = {"comment": comment}
        if track_timecode:
            payload["track_timecode"] = track_timecode
        return await self._request("POST", f"/tracks/{track_id}/comments", token=token, json=payload)

    async def get_track_comment(self, track_id: str, comment_id: str) -> dict:
        return await self._request("GET", f"/tracks/{track_id}/comments/{comment_id}")

    async def update_track_comment(self, track_id: str, comment_id: str, comment: str, token: str,
                                   track_timecode: Optional[int] = None) -> dict:
        payload = {"comment": comment}
        if track_timecode:
            payload["track_timecode"] = track_timecode
        return await self._request("PUT", f"/tracks/{track_id}/comments/{comment_id}", token=token, json=payload)

    async def delete_track_comment(self, track_id: str, comment_id: str, token: str) -> None:
        return await self._request("DELETE", f"/tracks/{track_id}/comments/{comment_id}", token=token)

    async def reply_to_track_comment(self, track_id: str, comment_id: str, comment: str, token: str,
                                     track_timecode: Optional[int] = None) -> dict:
        payload = {"comment": comment}
        if track_timecode:
            payload["track_timecode"] = track_timecode
        return await self._request("POST", f"/tracks/{track_id}/comments/{comment_id}/replies", token=token,
                                   json=payload)

    # ========== Лайки комментариев ==========

    async def like_comment(self, comment_id: str, token: str) -> dict:
        return await self._request("POST", f"/comments/{comment_id}/like", token=token)

    async def dislike_comment(self, comment_id: str, token: str) -> dict:
        return await self._request("POST", f"/comments/{comment_id}/dislike", token=token)

    async def unlike_comment(self, comment_id: str, token: str) -> dict:
        return await self._request("DELETE", f"/comments/{comment_id}/like", token=token)

    async def undislike_comment(self, comment_id: str, token: str) -> dict:
        return await self._request("DELETE", f"/comments/{comment_id}/dislike", token=token)