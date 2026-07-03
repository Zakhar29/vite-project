from uuid import UUID
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from config import settings

from src.clients.users_service import UsersClient
from src.clients.media_service import MediaClient
from src.clients.music_service import MusicClient
from src.clients.social_feed_service import SocialClient
from src.clients.comments_service import CommentClient

security = HTTPBearer()

class CurrentUser(BaseModel):
    """Только то, что нужно для хедера на каждой странице"""
    id: UUID
    nickname: str
    avatar_url: str
    token: str = ""

    class Config:
        from_attributes = True


# Глобальный кэш для пользователей (опционально, чтобы не дёргать user_service на каждый запрос)
_user_cache = {}


def get_users_client() -> UsersClient:
    return UsersClient()


def get_media_client() -> MediaClient:
    return MediaClient()


def get_music_client() -> MusicClient:
    return MusicClient()


def get_social_client() -> SocialClient:
    return SocialClient()


def get_comment_client() -> CommentClient:
    return CommentClient()


async def refresh_access_token(
        refresh_token: str,
        users_client: UsersClient
) -> Optional[str]:
    """Обновление access_token через refresh_token"""
    try:
        result = await users_client.refresh(refresh_token)
        return result.get("access_token")
    except Exception:
        return None


async def get_current_user(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        users_client: UsersClient = Depends(get_users_client)
) -> CurrentUser:
    """
    Получение текущего пользователя с автообновлением токена.
    Если access_token просрочен, пробует обновить через refresh_token из cookies.
    """

    # Функция для создания CurrentUser из payload
    async def make_current_user(
            user_uuid: UUID,
            users_client: UsersClient = Depends(get_users_client),
            token: str = ""
    ) -> CurrentUser:
        user = await users_client.get_user_info(user_id = str(user_uuid))
        return CurrentUser(
            id=user_uuid,
            nickname=user.get("user_nickname"),
            avatar_url=user.get("user_avatar") or "",
            token=token
        )

    # Проверяем наличие access_token в заголовке
    access_token = None
    if credentials:
        access_token = credentials.credentials

    # Пробуем декодировать access_token
    if access_token:
        try:
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            token_type = payload.get("type")
            if token_type in (None, "access"):
                user_id = payload.get("user_id") or payload.get("sub")
                if user_id:
                    return await make_current_user(UUID(user_id), users_client, access_token)
        except JWTError:
            # Токен просрочен или невалидный, пробуем обновить
            pass

    # Если access_token нет или он невалидный, пробуем обновить через refresh_token из cookies
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        new_access_token = await refresh_access_token(refresh_token, users_client)
        if new_access_token:
            # Обновляем токен в заголовке для текущего запроса
            try:
                payload = jwt.decode(
                    new_access_token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                )
                user_id = payload.get("user_id") or payload.get("sub")
                if user_id:
                    return await make_current_user(UUID(user_id), users_client, new_access_token)
            except JWTError:
                pass

    # Если ничего не сработало — пользователь не авторизован
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_current_user(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        users_client: UsersClient = Depends(get_users_client)
) -> Optional[CurrentUser]:
    """Для публичных страниц (неавторизованные пользователи)"""
    try:
        return await get_current_user(request, credentials, users_client)
    except HTTPException:
        return None
