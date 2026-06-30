from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import redis
from jose import JWTError, jwt
import uuid

from src.db.postgres_engine import get_async_session
from src.models.users_models import Users
from config import settings

security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_async_session)
) -> Users:
    """
    Получает текущего аутентифицированного пользователя из JWT токена
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Преобразуем строковый ID в UUID
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    result = await db.execute(
        select(Users).where(Users.id == user_uuid)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def get_optional_current_user(
        request: Request,
        db: AsyncSession = Depends(get_async_session)
) -> Optional[Users]:
    """
    Получает текущего пользователя, если он авторизован.
    Если токен отсутствует или невалидный - возвращает None.
    """
    # Получаем Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    # Преобразуем строковый ID в UUID
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None
    
    result = await db.execute(
        select(Users).where(Users.id == user_uuid)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        return None
    
    return user


def decode_token(token: str) -> Optional[dict]:
    """Декодирует JWT токен с помощью jose"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def get_redis_client():
    """Зависимость для Redis клиента"""
    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        health_check_interval=30
    )
    try:
        yield redis_client
    finally:
        redis_client.close()