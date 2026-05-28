import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from config import MediaType
from src.S3client.minio_client import S3Client
from src.services.media import MediaService
from src.api.routes import avatars, covers, tracks, media
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""

    # === 1. Валидация переменных окружения ===
    minio_endpoint = os.getenv("MINIO_URL")
    minio_user = os.getenv("MINIO_ROOT_USER")
    minio_password = os.getenv("MINIO_ROOT_PASSWORD")
    default_bucket = os.getenv("S3_DEFAULT_BUCKET", "media")
    cdn_domain = os.getenv("CDN_DOMAIN", "localhost:9000")  # Публичный URL

    if not all([minio_endpoint, minio_user, minio_password]):
        raise RuntimeError(
            "S3 credentials not configured. Set MINIO_URL, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD"
        )

    # === 2. Инициализация S3 клиента ===
    s3_client = S3Client(
        endpoint_url=minio_endpoint,  # Внутренний адрес: http://minio:9000
        access_key=minio_user,
        secret_key=minio_password,
        bucket=default_bucket
    )

    # === 3. Подключение с повторными попытками ===
    retries = 5
    delay = 2.0
    for attempt in range(retries):
        try:
            await s3_client.start()
            # Проверка подключения
            await s3_client.client.list_buckets()
            break
        except Exception as e:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)

    # === 4. Создание бакетов ===
    required_buckets = [item.value for item in MediaType]
    await s3_client.create_buckets(required_buckets)

    # === 5. Инициализация MediaService ===
    media_service = MediaService(
        minio_client=s3_client,
        cdn_domain=cdn_domain  # Публичный домен для генерации URL
    )

    # === 6. Сохранение в app.state ===
    app.state.s3_client = s3_client
    app.state.media_service = media_service

    yield

    # === 7. Очистка при завершении ===
    await s3_client.close()


# Создаём приложение
app = FastAPI(lifespan=lifespan)
app.include_router(avatars.router)
app.include_router(covers.router)
app.include_router(tracks.router)
app.include_router(media.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
