from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from typing import AsyncGenerator

from example.config import postgres_settings


engine = create_async_engine(
    postgres_settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  #
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция, которую FastAPI будет использовать как зависимость.
    Она создает сессию, отдает её в эндпоинт, а после закрывает.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()