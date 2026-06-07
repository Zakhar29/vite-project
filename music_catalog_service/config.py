from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ========== Безопасность ==========
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ========== База данных ==========
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "admin"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "melo_tracks"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # ========== Redis ==========
    REDIS_URL: str = "redis://localhost:6379/0"

    # ========== НАСТРОЙКИ РЕКОМЕНДАЦИЙ ==========

    # Глубина поиска связанных жанров через GenreParents
    # 1 - только прямые родители/дети
    # 2 - добавляются "бабушки" и "внуки"
    RECOMMENDATIONS_GENRE_DEPTH: int = 2

    # Коэффициенты для глобальных рекомендаций (должны в сумме давать 1.0)
    RECOMMENDATIONS_POPULAR_FACTOR: float = 0.5  # популярные треки/альбомы
    RECOMMENDATIONS_NEW_FACTOR: float = 0.25  # новинки
    # random_factor = 1 - popular_factor - new_factor (0.25)

    # Минимальное количество треков для персонализации
    RECOMMENDATIONS_MIN_TRACKS_FOR_PERSONALIZATION: int = 3

    # Максимальное количество жанров для персонализации
    RECOMMENDATIONS_MAX_GENRES: int = 5

    # Максимальное количество авторов для персонализации
    RECOMMENDATIONS_MAX_AUTHORS: int = 10

    # ========== НАСТРОЙКИ ПОИСКА ==========

    # Максимальный лимит на один запрос
    SEARCH_MAX_LIMIT: int = 100

    # Лимит по умолчанию
    SEARCH_DEFAULT_LIMIT: int = 20

    # Минимальная длина поискового запроса
    SEARCH_MIN_QUERY_LENGTH: int = 1

    # Максимальная длина поискового запроса
    SEARCH_MAX_QUERY_LENGTH: int = 100

    # ========== НАСТРОЙКИ BPM ==========

    # Допустимое отклонение BPM для похожих треков (в процентах)
    # 0.05 = 5% отклонение
    SIMILAR_BPM_TOLERANCE: float = 0.05

    # Минимальный BPM для фильтрации
    BPM_MIN: int = 10

    # Максимальный BPM для фильтрации
    BPM_MAX: int = 1000

    # ========== НАСТРОЙКИ КЭШИРОВАНИЯ ==========

    # Время жизни кэша для рекомендаций (секунды)
    # 3600 = 1 час
    CACHE_RECOMMENDATIONS_TTL: int = 3600

    # Время жизни кэша для поиска (секунды)
    # 300 = 5 минут
    CACHE_SEARCH_TTL: int = 300

    # ========== НАСТРОЙКИ ПАГИНАЦИИ ==========

    # Максимальный размер страницы
    MAX_PAGE_SIZE: int = 100

    # Размер страницы по умолчанию
    DEFAULT_PAGE_SIZE: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()