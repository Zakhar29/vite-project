from typing import Optional
from src.clients.base import ServiceClient
from config import settings


class UsersClient(ServiceClient):
    def __init__(self):
        super().__init__(settings.USERS_SERVICE_URL)

    # ========== Аутентификация ==========

    async def register(self, username: str, email: str, password: str, nickname: str) -> dict:
        """Регистрация пользователя"""
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "nickname": nickname
        }
        return await self._request("POST", "/auth/register", json=payload)

    async def login(self, email: str, password: str) -> dict:
        """Вход в аккаунт"""
        payload = {"email": email, "password": password}
        return await self._request("POST", "/auth/login", json=payload)

    async def refresh(self, refresh_token: str) -> dict:
        """Обновление токенов"""
        return await self._request("POST", "/auth/refresh", params={"refresh_token": refresh_token})

    async def logout(self, token: str) -> dict:
        """Выход из аккаунта"""
        return await self._request("POST", "/auth/logout", token=token)

    # ========== Пользователи ==========

    async def get_me(self, token: str) -> dict:
        """Получить текущего пользователя"""
        return await self._request("GET", "/users/me", token=token)

    async def get_user_info(self, user_id: str) -> dict:
        """Полная информация о пользователе"""
        return await self._request("GET", f"/users/get_user_info/{user_id}")

    async def get_user(self, user_id: str) -> dict:
        """Краткая информация о пользователе"""
        return await self._request("GET", f"/users/get_user/{user_id}")

    async def get_user_status(self, user_id: str) -> dict:
        """Статус пользователя"""
        return await self._request("GET", f"/users/get_user_status/{user_id}")

    # ========== Подписки и друзья ==========

    async def follow(self, user_id: str, token: str) -> dict:
        """Подписаться на пользователя"""
        return await self._request("POST", f"/follow/{user_id}", token=token)

    async def unfollow(self, user_id: str, token: str) -> dict:
        """Отписаться от пользователя"""
        return await self._request("DELETE", f"/follow/{user_id}", token=token)

    async def get_followers(self, user_id: str, skip: int = 0, limit: int = 50) -> dict:
        """Список подписчиков"""
        return await self._request("GET", f"/users/followers/{user_id}", params={"skip": skip, "limit": limit})

    async def get_following(self, user_id: str, skip: int = 0, limit: int = 50) -> dict:
        """Список подписок"""
        return await self._request("GET", f"/users/following/{user_id}", params={"skip": skip, "limit": limit})

    async def get_friends(self, user_id: str, skip: int = 0, limit: int = 50) -> dict:
        """Список друзей"""
        return await self._request("GET", f"/users/friends/{user_id}", params={"skip": skip, "limit": limit})

    # ========== Настройки ==========

    async def update_avatar(self, avatar_url: str, token: str) -> dict:
        """Обновить аватар"""
        return await self._request("POST", "/settings/avatar", token=token, json={"avatar_url": avatar_url})

    async def update_bio(self, bio: str, token: str) -> dict:
        """Обновить биографию"""
        return await self._request("POST", "/settings/bio", token=token, json={"bio": bio})

    async def rename_nickname(self, nickname: str, token: str) -> dict:
        """Изменить никнейм"""
        return await self._request("POST", "/settings/rename_nickname", token=token, json={"nickname": nickname})

    async def rename_username(self, username: str, token: str) -> dict:
        """Изменить username"""
        return await self._request("POST", "/settings/rename_username", token=token, json={"username": username})

    async def change_password(self, password: str, new_password: str, token: str) -> dict:
        """Сменить пароль"""
        payload = {"password": password, "new_password": new_password}
        return await self._request("POST", "/settings/change_password", token=token, json=payload)