from typing import Optional
from src.clients.base import ServiceClient
from config import settings


class SocialClient(ServiceClient):
    def __init__(self):
        super().__init__(settings.SOCIAL_FEED_URL)

    async def create_post(self, text: str, token: str, media: Optional[list] = None) -> dict:
        """Создать пост"""
        payload = {"text": text, "media": media or []}
        return await self._request("POST", "/posts", token=token, json=payload)

    async def list_posts(
            self,
            author_id: Optional[str] = None,
            skip: int = 0,
            limit: int = 20,
            sort_by: str = "created_at",
            sort_order: str = "desc",
            created_after: Optional[str] = None,
            created_before: Optional[str] = None
    ) -> dict:
        """Список постов"""
        params = {"skip": skip, "limit": limit, "sort_by": sort_by, "sort_order": sort_order}
        if author_id:
            params["author_id"] = author_id
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before
        return await self._request("GET", "/posts", params=params)

    async def get_recommended_posts(
        self,
        following_ids: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """
        Получение рекомендаций постов.
        """
        params = {"skip": skip, "limit": limit}
        
        if following_ids:
            params["following_ids"] = ",".join(following_ids)
        
        try:
            response = await self._request("GET", "/feed/recommendations", params=params)
            
            # ===== ПРОВЕРЯЕМ ОТВЕТ =====
            print(f"🔍 Ответ от social_feed_service: {response}")
            print(f"🔍 Тип ответа: {type(response)}")
            
            # Если ответ None или пустой
            if not response:
                return {"items": [], "total": 0}
            
            # Если ответ - список
            if isinstance(response, list):
                return {"items": response, "total": len(response)}
            
            # Если ответ - словарь
            if isinstance(response, dict):
                items = response.get("items", [])
                if not isinstance(items, list):
                    items = []
                return {
                    "items": items,
                    "total": response.get("total", len(items))
                }
            
            # Если ничего не подошло
            return {"items": [], "total": 0}
        
        except Exception as e:
            print(f"❌ Ошибка получения рекомендаций: {e}")
            return {"items": [], "total": 0}

    async def get_post(self, post_id: str) -> dict:
        """Получить пост"""
        return await self._request("GET", f"/posts/{post_id}")

    async def update_post(self, post_id: str, token: str, text: Optional[str] = None,
                          media: Optional[list] = None) -> dict:
        """Обновить пост"""
        payload = {}
        if text is not None:
            payload["text"] = text
        if media is not None:
            payload["media"] = media
        return await self._request("PUT", f"/posts/{post_id}", token=token, json=payload)

    async def delete_post(self, post_id: str, token: str) -> None:
        """Удалить пост"""
        return await self._request("DELETE", f"/posts/{post_id}", token=token)

    async def like_post(self, post_id: str, token: str) -> dict:
        """Лайкнуть пост"""
        return await self._request("POST", f"/posts/{post_id}/like", token=token)

    async def unlike_post(self, post_id: str, token: str) -> dict:
        """Убрать лайк"""
        return await self._request("DELETE", f"/posts/{post_id}/like", token=token)

    async def inc_post_comments(self, post_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/posts/{post_id}/inc-comments", token=token)

    async def dec_post_comments(self, post_id: str, token: str) -> dict:
        return await self._request("PATCH", f"/posts/{post_id}/dec-comments", token=token)