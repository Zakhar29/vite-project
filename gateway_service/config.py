import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Сервисы
    USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8000")
    MEDIA_SERVICE_URL = os.getenv("MEDIA_SERVICE_URL", "http://localhost:8002")
    MUSIC_CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8003")
    SOCIAL_FEED_URL = os.getenv("SOCIAL_SERVICE_URL", "http://localhost:8004")
    COMMENT_SERVICE_URL = os.getenv("COMMENTS_SERVICE_URL", "http://localhost:8005")
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'http://localhost:9092')
    KAFKA_CLIENT_ID = "my-producer-id"
    # Таймауты
    REQUEST_TIMEOUT = 30.0
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    # Токены

    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


settings = Settings()