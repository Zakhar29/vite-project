# dependencies.py
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.S3client.minio_client import S3Client
from src.services.media import MediaService
from uuid import UUID
from jose import JWTError, jwt
from pydantic import BaseModel

from config import settings

security = HTTPBearer()


class CurrentUser(BaseModel):
    id: UUID


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc

    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id or payload.get("type") not in (None, "access"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload")

    try:
        return CurrentUser(id=UUID(user_id))
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid user id") from exc


async def get_s3_client(request: Request) -> S3Client:
    """Зависимость для получения S3 клиента"""
    client: S3Client = request.app.state.s3_client
    if not client:
        raise HTTPException(503, "S3 client not initialized")
    return client


async def get_media_service(request: Request) -> MediaService:
    """Зависимость для получения MediaService"""
    service: MediaService = request.app.state.media_service
    if not service:
        raise HTTPException(503, "Media service not initialized")
    return service