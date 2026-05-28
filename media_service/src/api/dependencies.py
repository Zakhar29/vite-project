# dependencies.py
from fastapi import Depends, Request, HTTPException
from src.S3client.minio_client import S3Client
from src.services.media import MediaService


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