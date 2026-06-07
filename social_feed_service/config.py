from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://admin:postgres@localhost:27017/?authSource=admin"
    MONGODB_DATABASE: str = "melo_social"
    POSTS_COLLECTION: str = "posts"

    USERS_SERVICE_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
